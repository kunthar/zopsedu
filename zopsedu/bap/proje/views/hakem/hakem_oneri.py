"""Proje Hakem Oneri view classları"""
from flask_allows import And
from flask import request, current_app, jsonify, abort
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import TamamlanmamisProjeBasvurusu, ProjeYurutucusu
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import Proje, OgretimElemani, ProjeTuru
from zopsedu.auth.lib import auth, Permission
from zopsedu.personel.models.hakem import HakemOneri
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class HakemOneriView(FlaskView):
    """Hakem Oneri View Class"""

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["hakem"]["projeye_hakem_onerme"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/hakem-oner/', methods=['POST'])
    def hakem_oner(proje_id):
        """
        Ad, Soyad ve email ile önerilen kişileri HakemOneri modeline kaydeder.

        Projenin belirli bir hakem limiti vardır.Bunlar kontrol edilip kaydedilir.
        Limite ulaşılmış ise hata dönülür
        Returns:

        """
        adi = request.get_json().get('ad')
        soyad = request.get_json().get('soyad')
        email = request.get_json().get('email')
        ogretim_elemani_id = request.get_json().get("ogretim_elemani_id")
        try:
            try:
                proje = DB.session.query(Proje).filter_by(id=proje_id).one()
                proje_turu = DB.session.query(ProjeTuru).filter_by(id=proje.proje_turu).one()
            except NoResultFound as exc:
                CustomErrorHandler.error_handler(
                    hata="Var Olmayan bir proje_turu_id veya proje_id ile hakem onerisi eklenmeye "
                    "çalışıldı. Hata: {}".format(exc))
                return abort(400)
            if not proje_turu.hakem_onerilsin_mi:
                # todo: bu projeye hakem onerilemez hatası dön
                pass
            if ogretim_elemani_id:
                try:
                    onerilen_hakemlerde_var_mi = DB.session.query(HakemOneri).filter_by(
                        proje_id=proje_id, ogretim_elemani_id=ogretim_elemani_id).first()
                    if onerilen_hakemlerde_var_mi:
                        return abort(400)
                    ogretim_elemani = DB.session.query(OgretimElemani).filter_by(
                        id=ogretim_elemani_id).one()
                    hakem_onerisi = HakemOneri(proje_id=proje_id,
                                               ogretim_elemani_id=ogretim_elemani_id)
                    DB.session.add(hakem_onerisi)
                    DB.session.commit()
                    signal_payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "oe_hakem_onerildi").type_index,
                        "nesne": 'Hakem Oneri',
                        "nesne_id": ogretim_elemani_id,
                        "etkilenen_nesne": "Proje",
                        "etkilenen_nesne_id": proje_id,
                        "ekstra_mesaj": "{} adlı kullanıcı, {} {} öğretim elemanını hakem olarak "
                                        "önerdi.".format(current_user.username, adi, soyad)
                    }
                    signal_sender(**signal_payload)
                    person = ogretim_elemani.person
                    return jsonify(status="success",
                                   hakemOneriData={
                                       "id": hakem_onerisi.id,
                                       "ad": person.ad,
                                       "soyad": person.soyad,
                                       "email": person.birincil_eposta or person.ikincil_eposta})
                except NoResultFound as exc:
                    DB.session.rollback()
                    CustomErrorHandler.error_handler(
                                                     hata="Var Olmayan bir ogretim_elemani_id ile hakem onerisi eklenmeye "
                                                          "çalışıldı. Hata: {}".format(exc)
                                                     )
                    return jsonify(status="error"), 400
            else:
                hakem_onerisi = HakemOneri(proje_id=proje_id,
                                           ad=adi,
                                           soyad=soyad,
                                           email=email)
                DB.session.add(hakem_onerisi)
                DB.session.commit()
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "kisi_hakem_onerildi").type_index,
                    "nesne": 'Hakem Oneri',
                    "nesne_id": ogretim_elemani_id,
                    "etkilenen_nesne": "Proje",
                    "etkilenen_nesne_id": proje_id,
                    "ekstra_mesaj": "{} adlı kullanıcı, {} {} kişiyi hakem olarak önerdi.".format(
                        current_user.username,
                        adi, soyad)
                }
                signal_sender(**signal_payload)
                return jsonify(status="success", hakemOneriData={"id": hakem_onerisi.id,
                                                                 "ad": adi,
                                                                 "soyad": soyad,
                                                                 "email": email})
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                                             hata="Proje idsi %s olan projeye hakem önerisi eklemeye"
                                                  "çalışılırken bir sorun oluştu. Hata: %s" % (
                                                      proje_id, exc)
                                             )
        return jsonify(status="error"), 400

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["hakem"]["projeye_hakem_onerme"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/hakem-oneri-sil/<int:oneri_id>', methods=['DELETE'])
    def hakem_oneri_sil(proje_id, oneri_id):
        """
        Daha önce proje için önerilip kaydedilmiş hakem önerisini siler
        """
        try:
            silinecek_oneri = DB.session.query(HakemOneri).filter_by(
                id=oneri_id, proje_id=proje_id).first()
            DB.session.delete(silinecek_oneri)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "hakem_onerisi_kaldirildi").type_index,
                "nesne": 'Hakem Oneri',
                "nesne_id": oneri_id,
                "etkilenen_nesne": "Proje",
                "etkilenen_nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} {} kişiyi hakem önerilerinden "
                                "kaldırdı.".format(current_user.username,
                                                   silinecek_oneri.ad, silinecek_oneri.soyad)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success")
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                                             hata="Proje idsi %s olan projeye hakem önerisi silinmeye"
                                                  "çalışılırken bir sorun oluştu. Hata: %s" % (
                                                      proje_id, exc)
                                             )
        return jsonify(status="error"), 400
