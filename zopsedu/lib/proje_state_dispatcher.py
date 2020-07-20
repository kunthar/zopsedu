from datetime import datetime, timedelta

from sqlalchemy.orm import joinedload

from zopsedu.bap.models.proje import Proje
from zopsedu.lib.db import DB
from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import AppStateTracker, AppState, AppAction
from zopsedu.models.helpers import JobTypes
from zopsedu.lib.job_helpers.email_helpers import email_scheduler


class ProjeStateDispacther:
    @staticmethod
    def current_state_info(proje_id=None, params=None):
        if proje_id:
            return DB.session.query(AppState).join(Proje, Proje.id == proje_id).filter(
                Proje.id == proje_id,
                AppState.id == Proje.proje_durumu_id).first()

        return DB.session.query(AppStateTracker).filter(AppStateTracker.params.contains(params),
                                                        AppStateTracker.job_type == JobTypes.project_state_change).options(
            joinedload(AppStateTracker.app_state)).order_by(
            AppStateTracker.date.desc()).first()

    @staticmethod
    def all_states_info(params):
        return DB.session.query(AppStateTracker).filter(AppStateTracker.params.contains(params),
                                                        AppStateTracker.job_type == JobTypes.project_state_change). \
            options(AppStateTracker.app_state).all()

    @staticmethod
    def spec_state_info(params, app_state_tracker_id):
        return DB.session.query(AppStateTracker).filter(AppStateTracker.params.contains(params),
                                                        AppStateTracker.state_id == app_state_tracker_id,
                                                        AppStateTracker.job_type == JobTypes.project_state_change). \
            options(AppStateTracker.app_state).all()

    @staticmethod
    def possible_next_states_info(current_app_state_id):
        return DB.session.query(AppState.possible_states).filter(
            AppState.id == current_app_state_id).first()[0]

    @staticmethod
    def possible_actions(current_app_state_id):
        return DB.session.query(AppState.possible_actions).filter(
            AppState.id == current_app_state_id).first()[0]

    @staticmethod
    def do_action_checker(current_app_state_id, action_code):
        possible_actions = ProjeStateDispacther.possible_actions(
            current_app_state_id=current_app_state_id)

        for action in possible_actions:
            if action_code == action:
                action_info = DB.session.query(AppAction.id.label("app_action_id"),
                                               AppAction.description.label(
                                                   "app_action_description")). \
                    filter(AppAction.action_code == action).first()

                return action_info

        return None

    @staticmethod
    def state_change_checker(current_app_state_id, next_app_state_code):

        possible_next_states = ProjeStateDispacther.possible_next_states_info(
            current_app_state_id=current_app_state_id)

        for next_state in possible_next_states:
            if next_app_state_code == next_state:
                next_state_info = DB.session.query(AppState.id.label("app_state_id"),
                                                   AppState.description.label(
                                                       "app_state_description")). \
                    filter(AppState.state_code == next_state).first()

                return next_state_info

        return None

    @staticmethod
    def email_gonder(receiver_person_id=None, receiver_email=None, proje=None, subject=None,
                     content_text=None,
                     greeting_name=None):
        """
        yurutucunun mail adresi person modelinden alinir. birincil epostasi yoksa ikincil
        epostasi kullanilir.
        """
        if not receiver_email:
            receiver_email = proje.proje_yurutucu.person.birincil_eposta or proje.proje_yurutucu.person.ikincil_eposta
        if not receiver_person_id:
            receiver_person_id = proje.proje_yurutucu.person.id
        if not greeting_name:
            greeting_name = "{} {}".format(proje.proje_yurutucu.person.ad,
                                           proje.proje_yurutucu.person.soyad)

        email_scheduler(recipients=[{"email": receiver_email,
                                     "person_id": receiver_person_id}],
                        proje_id=proje.id, subject=subject,
                        greeting_name=greeting_name, content_text=content_text,
                        scheduler_params={"trigger": "date",
                                          "run_date": datetime.now() + timedelta(seconds=10)})

    @staticmethod
    def project_init(next_app_state_code='P1', params=None, triggered_by=None, proje_id=None,
                     email_gonderilsin_mi=None,
                     yurutucu_log=None):
        try:
            app_state_info = DB.session.query(AppState.id.label("app_state_id"),
                                              AppState.description.label("app_state_description")). \
                filter(AppState.state_code == next_app_state_code).first()

            app_state_tracker = AppStateTracker(
                state_id=app_state_info.app_state_id,
                params=params,
                date=datetime.now(),
                job_type=JobTypes.project_state_change,
                triggered_by=triggered_by,
                description=app_state_info.app_state_description,

            )
            DB.session.add(app_state_tracker)
            proje = DB.session.query(Proje).filter(Proje.id == proje_id).first()
            proje.proje_durumu_id = app_state_info.app_state_id

            DB.session.commit()

            payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "proje_durum_degisimi").type_index,
                "ekstra_mesaj": "{} numaralı projenin durumu {} yapildi.".format(proje.proje_no,
                                                                                 app_state_info.app_state_description),
                "nesne": 'Proje',
                "nesne_id": proje_id,
            }

            signal_sender(notification=True, **payload)

            yurutucu_person_id = proje.proje_yurutucu.person.id
            payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "proje_durum_degisimi").type_index,
                "ekstra_mesaj": "{} numaralı projenin durumu {} yapildi.".format(proje.proje_no,
                                                                                 app_state_info.app_state_description),
                "notification_receiver": yurutucu_person_id,
                "notification_title": app_state_info.app_state_description,
                "notification_message": "{} numaralı projenin yeni durumu: {} ".format(
                    proje.proje_no,
                    app_state_info.app_state_description),
                "proje_id": proje.id,
                "related_table": "proje_mesaj"
            }
            signal_sender(log=False, notification=True, **payload)

            for bap_admin in bap_yetkili_and_admin_ids():
                payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_durum_degisimi").type_index,
                    "ekstra_mesaj": "{} numaralı projenin durumu {} yapildi.".format(proje.proje_no,
                                                                                     app_state_info.app_state_description),
                    "notification_receiver": bap_admin.person_id,
                    "notification_title": app_state_info.app_state_description,
                    "notification_message": "{} no su ile proje başvurusu yapıldı.{}".format(
                        proje.proje_no, app_state_info.app_state_description),
                    "proje_id": proje.id
                }

                signal_sender(log=False, notification=True, **payload)

            if email_gonderilsin_mi:
                ProjeStateDispacther.email_gonder(proje=proje,
                                             subject=app_state_info.app_state_description,
                                             content_text=yurutucu_log,
                                             greeting_name="{} {}".format(
                                                 proje.proje_yurutucu.person.ad,
                                                 proje.proje_yurutucu.person.soyad))

            return True

        except Exception as exc:
            raise Exception(exc)

    @staticmethod
    def state_change(proje_id=None, next_app_state_code=None, params=None, triggered_by=None,
                     bap_yetkilisi_notu=None,
                     description='', email_gonderilsin_mi=None, yurutucu_log=None):

        try:
            current_state_info = ProjeStateDispacther.current_state_info(proje_id=proje_id)

            next_state_info = ProjeStateDispacther.state_change_checker(
                current_app_state_id=current_state_info.id,
                next_app_state_code=next_app_state_code)
        except Exception as e:
            raise Exception(e)

        if next_state_info.app_state_id:
            try:
                app_state_tracker = AppStateTracker(
                    state_id=next_state_info.app_state_id,
                    params=params,
                    date=datetime.now(),
                    job_type=JobTypes.project_state_change,
                    triggered_by=triggered_by,
                    description="{} {}".format(next_state_info.app_state_description, description)

                )

                proje = DB.session.query(Proje).filter(Proje.id == proje_id).first()
                proje.proje_durumu_id = next_state_info.app_state_id
                DB.session.add(app_state_tracker)
                DB.session.commit()

                payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_durum_degisimi").type_index,
                    "ekstra_mesaj": "{} id li projenin durumu {} yapildi.".format(proje.id,
                                                                                  next_state_info.app_state_description),
                    "nesne": 'Proje',
                    "nesne_id": proje.id,
                }

                signal_sender(notification=True, **payload)

                if yurutucu_log:
                    yurutucu_person_id = proje.proje_yurutucu.person.id
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "proje_durum_degisimi").type_index,
                        "ekstra_mesaj": "{} numaralı projenin durumu {} yapildi.".format(
                            proje.proje_no,
                            next_state_info.app_state_description),
                        "notification_receiver": yurutucu_person_id,
                        "notification_title": next_state_info.app_state_description,
                        "notification_message": "{} numaralı proje için bap yetkilisi notu; {} ".format(
                            proje.proje_no, yurutucu_log),
                        "proje_id": proje.id,
                        "related_table": "proje_mesaj"
                    }

                    signal_sender(log=False, notification=True, **payload)

                    if email_gonderilsin_mi:
                        ProjeStateDispacther.email_gonder(
                            proje=proje,
                            subject=next_state_info.app_state_description,
                            content_text="{} numaralı proje için bap yetkilisi notu; {} ".format(
                                proje.proje_no,
                                yurutucu_log),
                            greeting_name="{} {}".format(
                                proje.proje_yurutucu.person.ad,
                                proje.proje_yurutucu.person.soyad))

                for bap_admin in bap_yetkili_and_admin_ids():
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "proje_durum_degisimi").type_index,
                        "ekstra_mesaj": "{} numaralı  projenin durumu {} yapildi.".format(
                            proje.proje_no,
                            next_state_info.app_state_description),
                        "notification_receiver": bap_admin.person_id,
                        "notification_title": next_state_info.app_state_description,
                        "notification_message": "{} numaralı proje için durum değişimi gerçekleşti. {}".format(
                            proje.proje_no,
                            bap_yetkilisi_notu or next_state_info.app_state_description),
                    }

                    signal_sender(log=False, notification=True, **payload)


            except Exception as exc:
                raise Exception(exc)

        else:
            raise ValueError("Could not find next possible state's id.")

        return next_state_info.app_state_id

    @staticmethod
    def do_action(proje_id=None, action_code=None, params=None, triggered_by=None,
                  bap_yetkilisi_notu=None,
                  description='', email_gonderilsin_mi=None, yurutucu_log=None):
        try:
            current_state_info = ProjeStateDispacther.current_state_info(proje_id=proje_id)

            action_info = ProjeStateDispacther.do_action_checker(
                current_app_state_id=current_state_info.id,
                action_code=action_code)

        except Exception as e:
            raise Exception(e)

        if action_info.app_action_id:
            try:
                app_state_tracker = AppStateTracker(
                    state_id=current_state_info.id,
                    params=params,
                    date=datetime.now(),
                    job_type=JobTypes.project_action,
                    triggered_by=triggered_by,
                    description="{} {}".format(action_info.app_action_description, description)
                )

                DB.session.add(app_state_tracker)
                DB.session.commit()

                proje = DB.session.query(Proje).filter(Proje.id == proje_id).first()

                payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("proje_islem").type_index,
                    "ekstra_mesaj": "{} numaralı proje için {} işlemi yapıldı.".format(
                        proje.proje_no,
                        action_info.app_action_description),
                    "nesne": 'Proje',
                    "nesne_id": proje_id,
                }

                signal_sender(notification=True, **payload)

                if yurutucu_log:
                    yurutucu_person_id = proje.proje_yurutucu.person.id
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "proje_islem").type_index,
                        "ekstra_mesaj": "{} numaralı proje için {} işlemi yapıldı.".format(
                            proje.proje_no,
                            action_info.app_action_description),
                        "notification_receiver": yurutucu_person_id,
                        "notification_title": action_info.app_action_description,
                        "notification_message": "{} numaralı proje için bap yetkilisi notu: {}".format(
                            proje.proje_no, yurutucu_log),
                        "proje_id": proje.id,
                        "related_table": "proje_mesaj"
                    }

                    signal_sender(log=False, notification=True, **payload)
                    if email_gonderilsin_mi:
                        ProjeStateDispacther.email_gonder(
                            proje=proje,
                            subject=action_info.app_action_description,
                            content_text="{} numaralı proje için bap yetkilisi notu; {} ".format(
                                proje.proje_no,
                                yurutucu_log),
                            greeting_name="{} {}".format(
                                proje.proje_yurutucu.person.ad,
                                proje.proje_yurutucu.person.soyad))

                for bap_admin in bap_yetkili_and_admin_ids():
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "proje_islem").type_index,
                        "ekstra_mesaj": "{} numaralı proje için {} işlemi yapildi.".format(
                            proje.proje_no,
                            action_info.app_action_description),
                        "notification_receiver": bap_admin.person_id,
                        "notification_title": action_info.app_action_description,
                        "notification_message": "{} numaralı proje için işlem gerçekleşti. {}".format(
                            proje.proje_no,
                            bap_yetkilisi_notu or action_info.app_action_description),
                        "proje_id": proje.id
                    }

                    signal_sender(log=False, notification=True, **payload)

            except Exception as exc:
                raise Exception(exc)


        else:
            raise ValueError("Could not find next possible state's id.")
