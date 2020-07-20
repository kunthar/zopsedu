from faker.utils.datetime_safe import datetime
from sqlalchemy.orm import lazyload

from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi
from zopsedu.lib.db import DB
from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.state_dispatcher import StateDispatcher
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import AppStateTracker
from zopsedu.models.helpers import JobTypes


class SatinalmaStateDispatcher(StateDispatcher):

    def __init__(self, state_type=None, action_type=None, entity_type=None, entity=None):
        super().__init__(state_type=state_type, action_type=action_type, entity_type=entity_type,
                         entity=entity)

    def state_change(self, next_app_state_code=None, triggered_by=None, bap_yetkilisi_notu=None,
                     description='', email_gonderilsin_mi=None, yurutucu_log=None):

        try:
            next_state_info = self.state_change_checker(next_app_state_code=next_app_state_code)

        except Exception as e:
            raise Exception(e)

        if next_state_info.app_state_id:
            try:
                app_state_tracker = AppStateTracker(
                    state_id=next_state_info.app_state_id,
                    params={'proje_id': self.entity.proje_id, 'satinalma_id': self.entity.id},
                    date=datetime.now(),
                    job_type=JobTypes.satinalma_state_change,
                    triggered_by=triggered_by,
                    description="{} {}".format(next_state_info.app_state_description, description)
                )

                entity_model = DB.session.query(self.entity_type).filter(
                    self.entity_type.id == self.entity.id).first()
                entity_model.durum_id = next_state_info.app_state_id
                DB.session.add(app_state_tracker)

                payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "satinalma_durum_degisimi").type_index,
                    "ekstra_mesaj": "{} id li {} durumu {} yapildi.".format(self.entity.__repr__(),
                                                                            self.entity.id,
                                                                            next_state_info.app_state_description),
                    "nesne": '{}'.format(self.entity.__repr__()),
                    "nesne_id": self.entity.id,
                }

                signal_sender(notification=True, **payload)

                proje = DB.session.query(Proje).filter(Proje.id == self.entity.proje_id).first()
                yurutucu_person_id = proje.proje_yurutucu.person.id

                satinalma = DB.session.query(
                    ProjeSatinAlmaTalebi.talep_numarasi.label("talep_numarasi")).options(
                    lazyload("*")).filter(ProjeSatinAlmaTalebi.id == self.entity.id).first()

                if yurutucu_log:
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "satinalma_durum_degisimi").type_index,
                        "ekstra_mesaj": "{} id'li projenin  id'li {} satinalma talebi {} yapildi.".format(
                            proje.id,
                            self.entity.id,
                            next_state_info.app_state_description),
                        "notification_receiver": yurutucu_person_id,
                        "notification_title": next_state_info.app_state_description,
                        "notification_message": "{} numaralı projenin {} numaralı satınalma "
                                                "talebinde yapılan durum değişimi için bap yetkili "
                                                "notu; {}".format(proje.proje_no,
                                                                  satinalma.talep_numarasi,
                                                                  yurutucu_log),
                        "proje_id": proje.id,
                        "related_table": "proje_mesaj"
                    }

                    signal_sender(log=False, notification=True, **payload)

                    if email_gonderilsin_mi:
                        SatinalmaStateDispatcher.email_gonder(
                            proje=proje,
                            subject=next_state_info.app_state_description,
                            content_text="{} numaralı projenin {} numaralı satınalma "
                                         "talebinde yapılan durum değişimi için bap yetkili "
                                         "notu; {}".format(
                                proje.proje_no,
                                satinalma.talep_numarasi,
                                yurutucu_log),
                            greeting_name="{} {}".format(
                                proje.proje_yurutucu.person.ad,
                                proje.proje_yurutucu.person.soyad))

                for bap_admin in bap_yetkili_and_admin_ids():
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "satinalma_durum_degisimi").type_index,
                        "ekstra_mesaj": "{} id'li projenin  id'li {} satinalma talebi {} yapildi.".format(
                            proje.id,
                            self.entity.id,
                            next_state_info.app_state_description),
                        "notification_receiver": bap_admin.person_id,
                        "notification_title": next_state_info.app_state_description,
                        "notification_message": "{} numaralı projenin {} numaralı satınalma "
                                                "talebi için durum değişimi yapıldı.{}".format(
                            proje.proje_no,
                            satinalma.talep_numarasi,
                            bap_yetkilisi_notu or next_state_info.app_state_description),
                    }

                    signal_sender(log=False, notification=True, **payload)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            raise ValueError("Could not find next possible state's id.")

        return next_state_info.app_state_id

    def do_action(self, next_app_action_code=None, triggered_by=None, bap_yetkilisi_notu=None,
                  description='', email_gonderilsin_mi=None, yurutucu_log=None):
        try:
            action_info = self.do_action_checker(next_app_action_code=next_app_action_code)

        except Exception as e:
            raise Exception(e)

        if action_info.app_action_id:
            try:
                app_state_tracker = AppStateTracker(
                    state_id=self.entity.durum_id,
                    params={'proje_id': self.entity.proje_id, 'satinalma_id': self.entity.id},
                    date=datetime.now(),
                    job_type=JobTypes.satinalma_action,
                    triggered_by=triggered_by,
                    description="{} {}".format(action_info.app_action_description, description)
                )

                proje = DB.session.query(Proje).filter(Proje.id == self.entity.proje_id).first()
                DB.session.add(app_state_tracker)

                satinalma = DB.session.query(
                    ProjeSatinAlmaTalebi.talep_numarasi.label("talep_numarasi")).options(
                    lazyload("*")).filter(ProjeSatinAlmaTalebi.id == self.entity.id).first()

                payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "satinalma_islemi").type_index,
                    "ekstra_mesaj": "{} id'li proje için  id'li {} satınalma talebi {} işlemi yapıldı.". \
                        format(proje.id, self.entity.id, action_info.app_action_description),
                    "nesne": 'Proje',
                    "nesne_id": self.entity.id,
                }

                signal_sender(notification=True, **payload)

                yurutucu_person_id = proje.proje_yurutucu.person.id

                if yurutucu_log:
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "satinalma_islemi").type_index,
                        "ekstra_mesaj": "{} id'li proje için  id'li {} satınalma talebi {} işlemi yapıldı.". \
                            format(proje.id, self.entity.id, action_info.app_action_description),
                        "notification_receiver": yurutucu_person_id,
                        "notification_title": action_info.app_action_description,
                        "notification_message": "{} numaralı projenin {} numaralı satınalma "
                                                "talebinde yapılan işlem için bap yetkili "
                                                "notu; {}".format(proje.proje_no,
                                                                  satinalma.talep_numarasi,
                                                                  yurutucu_log),
                        "proje_id": proje.id,
                        "related_table": "proje_mesaj"
                    }

                    signal_sender(log=False, notification=True, **payload)

                    if email_gonderilsin_mi:
                        SatinalmaStateDispatcher.email_gonder(
                            proje=proje,
                            subject=action_info.app_action_description,
                            content_text="{} numaralı projenin {} numaralı satınalma "
                                         "talebinde yapılan işlem için bap yetkili "
                                         "notu; {}".format(
                                proje.proje_no,
                                satinalma.talep_numarasi,
                                yurutucu_log),
                            greeting_name="{} {}".format(
                                proje.proje_yurutucu.person.ad,
                                proje.proje_yurutucu.person.soyad))

                for bap_admin in bap_yetkili_and_admin_ids():
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "satinalma_islemi").type_index,
                        "ekstra_mesaj": "{} id li projenin durumu {} yapildi.".format(proje.id,
                                                                                      action_info.app_action_description),
                        "notification_receiver": bap_admin.person_id,
                        "notification_title": action_info.app_action_description,
                        "notification_message": "{} numaralı projenin {} numaralı satınalma "
                                                "talebi için işlem yapıldı.{}".format(
                            proje.proje_no,
                            satinalma.talep_numarasi,
                            bap_yetkilisi_notu or action_info.app_action_description),
                        "proje_id": proje.id
                    }

                    signal_sender(log=False, notification=True, **payload)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)
        else:
            raise ValueError("Could not find next possible state's id.")
