"""BAP Proje Hakem View Modulu"""
from flask_babel import gettext as _
from flask import render_template, jsonify
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_allows import And, Or
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_detay import ProjeHakemDavetDurumlari
from zopsedu.bap.proje.forms.dashboard.hakem import HakemEkleForm
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import ProjeHakemleri
from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.bap.lib.auth import ProjeYurutucusu
from zopsedu.bap.proje.views.dashboard.common import get_next_states_info, get_actions_info
from zopsedu.personel.models.hakem import Hakem
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeHakemView(FlaskView):
    """Proje hakem önerilerinin ve proje hakemlerinin goruntulendigi view"""

    @login_required
    @auth.requires(
        And(Permission(
            *permission_dict["bap"]["proje"]["dashboard"]["proje_hakemleri_goruntuleme"]),
            Or(Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route('<int:proje_id>/dashboard/hakem', methods=["GET"], endpoint='proje_hakem_get')
    def proje_hakem_get(self, proje_id):
        """Proje raporlarini goruntulemek icin kullanilir"""

        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(Proje.id == proje_id, or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                                           Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)
        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)

        proje_hakem_onerileri = proje.proje_hakem_onerileri

        proje_hakemleri = DB.session.query(ProjeHakemleri).options(
            joinedload(ProjeHakemleri.hakem).joinedload("*")
        ).filter(ProjeHakemleri.proje_id == proje_id).all()

        hakem_ekle_form = HakemEkleForm()

        return render_template(
            'dashboard/proje_hakemleri.html',
            proje_id=proje_id,
            proje=proje,
            proje_yurutucusu_mu=proje_yurutucusu_mu,
            next_states_info=next_states_info,
            actions_info=actions_info,
            hakem_onerileri=proje_hakem_onerileri,
            proje_hakemleri=proje_hakemleri,
            hakem_ekle_form=hakem_ekle_form
        )

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["projeye_hakem_atama"]),
            Or(Role("BAP Yetkilisi"), Role("BAP Admin"))))
    @route('/<int:proje_id>/proje-hakemleri/<int:proje_hakem_id>', methods=['DELETE'])
    def proje_hakem_sil(proje_id, proje_hakem_id):
        """
        Seçilen hakemin projehakem davet durumunu cikarildi olarak degistirir.

        """
        try:

            proje_hakem = DB.session.query(ProjeHakemleri).filter(
                ProjeHakemleri.proje_id == proje_id,
                ProjeHakemleri.id == proje_hakem_id).one()
            proje_hakem.davet_durumu = ProjeHakemDavetDurumlari.cikarildi

            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("hakem_atama_sil").type_index,
                "nesne": 'Proje Hakemleri',
                "nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} id'li hakemi proje hakemleri arasindan "
                                "cikardi.".format(current_user.username, proje_hakem_id)
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                                             hata="Proje idsi %s olan proje hakemleri arasından %s idli hakemi çıkarmaya "
                                                  "çalışılırken bir sorun oluştu. Hata: %s" % (
                                                      proje_id, proje_hakem_id, exc)
                                             )
        return jsonify(status="error"), 400

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["projeye_hakem_atama"]),
            Or(Role("BAP Yetkilisi"), Role("BAP Admin"))))
    @route('/<int:proje_id>/hakem/<int:hakem_id>/ekle', methods=['POST'])
    def proje_hakemi_ekle(proje_id, hakem_id):
        """
        Secilen hakemi proje hakemleri modeline kaydeder.
        Eger daha once kaydedilmemis bir hakem ise ProjeHakem model instance i olusturup kaydeder.
        Daha once projeye hakemlik teklifini reddeden bir hakeme teklif gonderilmis ise "davet_durumu"
        alani "gonderildi" yapilir.
        Eger daha önce projeye atanip proje hakemlerinden cikarilan bir hakemi eklemeye calisirsa
        var olan projehakem kaydini bulup "davet_durumu" alani "gonderildi" yapilir.


        """
        try:
            proje_hakem = DB.session.query(ProjeHakemleri).options(
                joinedload(ProjeHakemleri.hakem).joinedload(Hakem.person),
                joinedload(ProjeHakemleri.hakem).joinedload(Hakem.personel)
            ).filter(
                ProjeHakemleri.hakem_id == hakem_id,
                ProjeHakemleri.proje_id == proje_id).scalar()
            proje = DB.session.query(Proje.proje_no.label("proje_no")).filter(Proje.id == proje_id).first()
            if proje_hakem:
                if proje_hakem.davet_durumu == ProjeHakemDavetDurumlari.gonderildi:
                    # davet durumu gonderildi durumunda ise yani hakem daveti yanıtlamadıysa
                    # bu durum gecerlidir.
                    return jsonify(status="error",
                                   error_message=_("Bu hakeme zaten davet gönderildi")), 409
                elif proje_hakem.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi:
                    return jsonify(status="error",
                                   error_message=_("Bu kişi zaten proje hakemi")), 409

                else:
                    # daveti kabul etmeyen veya projeden cikarilan hakem durumlari icin gecerlidir
                    proje_hakem.davet_durumu = ProjeHakemDavetDurumlari.gonderildi
                # eger proje_hakem i var ise daha once bu hakeme teklif gonderilmis ve herhangi bir
                # "davet_durumu" stateinde olabilir.
                hakem_person_id = proje_hakem.hakem.personel.person_id if proje_hakem.hakem.personel else proje_hakem.hakem.person_id
            else:
                hakem = DB.session.query(Hakem).options(
                    joinedload(Hakem.person),
                    joinedload(Hakem.personel)
                ).filter(Hakem.id == hakem_id).first()
                # daha once bu hakem proje ile iliskilendirilmemis.
                yeni_hakem = ProjeHakemleri(proje_id=proje_id, hakem_id=hakem_id)
                DB.session.add(yeni_hakem)
                hakem_person_id = hakem.personel.person_id if hakem.personel else hakem.person_id

            payload = {
                "notification_receiver": hakem_person_id,
                "notification_title": "Proje Hakemlik Daveti",
                "notification_message": "{} numaralı projeye hakem olmanız için davet gönderildi.".format(
                    proje.proje_no),
                "proje_id": proje_id,
            }

            signal_sender(log=False, notification=True, **payload)

            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("hakem_atama").type_index,
                "nesne": 'Proje Hakemleri',
                "nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} id'li hakeme hakemlik daveti gonderidi.".format(
                    current_user.username,
                    hakem_id
                )
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                                             hata="Proje idsi %s olan projeye hakem eklemeye çalışılırken bir sorun oluştu. Hata: %s"
                                                  % (proje_id, exc)
                                             )
        return jsonify(status="error", error_message=_(
            "Beklenmedik bir hata oluştur. Lütfen daha sonra tekrar deneyiniz")), 409
