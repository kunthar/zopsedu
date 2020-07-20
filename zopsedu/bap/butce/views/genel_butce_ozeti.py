from datetime import datetime

from sqlalchemy import desc
from werkzeug.datastructures import MultiDict
from flask import render_template, request, jsonify
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_
from sqlalchemy.orm import joinedload

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.db import DB
from zopsedu.auth.lib import Permission, auth
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import GelirKasasi, ButceGirdi, AppState
from zopsedu.bap.butce.forms.kasa import KasaGirdiFormu, Kasa
from zopsedu.models.helpers import AppStates


class GenelButceOzetiView(FlaskView):
    """Bap Genel Butce Ozeti view classi"""

    @staticmethod
    @login_required
    @route('/genel-butce-ozeti', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]['genel_butce_goruntuleme']),
                   menu_registry={"path": ".bap.butce.genel_butce",
                                  "title": _("Genel Bütçe Özeti")})
    def genel_butce_ozeti_listele():
        proje_app_state = DB.session.query(AppState.current_app_state, AppState.id).filter(
            or_(AppState.current_app_state == AppStates.devam,
                AppState.current_app_state == AppStates.son),
            AppState.state_type == "proje"
        ).all()

        devam_eden_state_id = set()
        sonuclanan_state_id = set()
        for state in proje_app_state:
            if state.current_app_state == AppStates.devam:
                devam_eden_state_id.add(state.id)
            else:
                sonuclanan_state_id.add(state.id)

        ana_kasalar = DB.session.query(
            GelirKasasi
        ).options(joinedload(GelirKasasi.projeler).load_only("proje_durumu_id")).order_by(
            desc(GelirKasasi.updated_at)).all()

        ana_kasalar_data = []

        for kasa in ana_kasalar:
            devam_eden_proje_sayisi = 0
            sonuclanan_proje_sayisi = 0
            for proje in kasa.projeler:
                if proje.proje_durumu_id in devam_eden_state_id:
                    devam_eden_proje_sayisi += 1
                elif proje.proje_durumu_id in sonuclanan_state_id:
                    sonuclanan_proje_sayisi += 1
            kullanilabilir_para = kasa.toplam_para - \
                                  kasa.harcanan_para - \
                                  kasa.rezerv_para - kasa.devredilen_para
            ana_kasalar_data.append(
                {
                    "id": kasa.id,
                    "kasa_adi": kasa.adi,
                    "mali_yil": kasa.mali_yil,
                    "toplam_para": kasa.toplam_para,
                    "harcanan_para": kasa.harcanan_para,
                    "rezerv_para": kasa.rezerv_para,
                    "kullanilabilir_para": kullanilabilir_para,
                    "devreden_para": kasa.devreden_para,
                    "devredilen_para": kasa.devredilen_para,
                    "devam_eden_proje_sayisi": devam_eden_proje_sayisi,
                    "sonuclanan_proje_sayisi": sonuclanan_proje_sayisi
                }
            )
        return render_template("genel_butce_ozeti_listele.html",
                               ana_kasalar=ana_kasalar_data,
                               kasa_formu=Kasa())

    @staticmethod
    @login_required
    @route('/kasa-ekle', methods=['POST'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]['kasa_olusturma']))
    def kasa_ekle():
        kasa_data = MultiDict(mapping=request.get_json())
        kasa_formu = Kasa(kasa_data)

        kasa = DB.session.query(GelirKasasi).filter(GelirKasasi.adi == kasa_formu.adi.data).all()
        # :todo form validate edilecek ve hata ajax response ile return edilecek
        if kasa:
            return jsonify(status="error",
                           error_message=_("Bu isimde bir kasa mevcut lütfen başka"
                                           " bir isimle tekrar deneyiniz")), 400

        try:
            yeni_kasa = GelirKasasi(adi=kasa_formu.adi.data,
                                    mali_yil=datetime.now().year)
            DB.session.add(yeni_kasa)
            DB.session.commit()

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("kasa_girdi_sil").type_index,
                "nesne": 'GelirKasasi',
                "nesne_id": yeni_kasa.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} id'li {} isimli kasa oluşturdu".format(
                    current_user.username,
                    yeni_kasa.id,
                    yeni_kasa.adi
                )
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")
        except Exception as exc:
            CustomErrorHandler.error_handler(hata="Yeni kasa oluştururken bir hata meydana geldi."
                                                  "User id {}".format(exc)
                                             )
            return jsonify(status="error",
                           error_message=_("Girdi eklenirken beklenmedik bir hata oluştu. "
                                           "Lütfen daha sonra tekrar deneyiniz.")), 500

    @staticmethod
    @login_required
    @route('/kasa/<int:kasa_id>/girdi-listele', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]['kasa_girdileri_goruntuleme']))
    def kasa_girdileri_listele(kasa_id):
        kasa_girdi_formu = KasaGirdiFormu()
        kasa_girdileri = DB.session.query(GelirKasasi).options(
            joinedload(GelirKasasi.girdiler)).filter(GelirKasasi.id == kasa_id).one()

        return render_template("kasa_girdileri_listele.html",
                               kasa_girdileri=kasa_girdileri,
                               kasa_girdi_formu=kasa_girdi_formu,
                               kasa_id=kasa_id,
                               current_year=datetime.now().year)

    @staticmethod
    @login_required
    @route('/kasa/<int:kasa_id>/girdi-ekle', methods=['POST'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]['kasa_girdisi_ekleme']))
    def kasa_girdi_ekle(kasa_id):
        girdi_data = MultiDict(mapping=request.get_json())
        kasa_girdi_formu = KasaGirdiFormu(girdi_data)

        # var olmayan bir kasaya ekleme yapilmaya calisiyorsa 500 doner
        try:
            kasa = DB.session.query(GelirKasasi).filter(GelirKasasi.id == kasa_id).one()
        except NoResultFound as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(hata="Var olmayan bir kasaya girdi eklemeye calisildi"
                                                  "Hata: {}, User id: {}".format(exc,
                                                                                 current_user.id))
            return jsonify(status="error",
                           error_message=_("Var olmayan bir kasaya girdi eklemeye çalıştınız")), 500

        if kasa.mali_yil != datetime.now().year:
            return jsonify(status="error",
                           error_message=_("Geçmiş mali yıla ait bir kasaya girdi ekleyemezsiniz")
                           ), 400

        if not kasa_girdi_formu.validate():
            return jsonify(status="error",
                           error_message=_("Form alanlarını doldurduğunuzdan emin olunuz")), 400
        try:
            yeni_girdi = ButceGirdi(gelir_kasasi_id=kasa.id,
                                    aciklama=kasa_girdi_formu.aciklama.data,
                                    tutar=kasa_girdi_formu.tutar.data)
            DB.session.add(yeni_girdi)
            kasa.toplam_para += kasa_girdi_formu.tutar.data
            DB.session.commit()

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("kasa_girdi_ekle").type_index,
                "nesne": 'ButceGirdi',
                "nesne_id": yeni_girdi.id,
                "etkilenen_nesne": "GelirKasasi",
                "etkilenen_nesne_id": kasa.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} id'li kasaya {} id'li {} açıklaması ile"
                                " {} TL tutarında girdi ekledi.".format(
                    current_user.username,
                    kasa.id,
                    yeni_girdi.id,
                    yeni_girdi.aciklama,
                    yeni_girdi.tutar
                )
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")
        except Exception as exc:
            CustomErrorHandler.error_handler(
                hata="{} id li kasaya girdi eklemeye calisirken bir "
                     "hata olustu. User id {}".format(kasa_id, exc)
            )
            return jsonify(status="error",
                           error_message=_("Girdi eklenirken beklenmedik bir hata oluştu. "
                                           "Lütfen daha sonra tekrar deneyiniz.")), 500

    @staticmethod
    @login_required
    @route('/kasa-girdi/<int:girdi_id>/sil', methods=['POST'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]['kasa_girdisi_silme']))
    def kasa_girdi_sil(girdi_id):
        silinecek_girdi = DB.session.query(ButceGirdi).options(
            joinedload(ButceGirdi.gelir_kasasi)
        ).filter(ButceGirdi.id == girdi_id).one()
        kasa = silinecek_girdi.gelir_kasasi

        if not silinecek_girdi.tutar <= (
                kasa.toplam_para - kasa.harcanan_para - kasa.rezerv_para - kasa.devredilen_para):
            return jsonify(status="error",
                           error_message=_("Kasanızda yeterli "
                                           "miktarda kullanılabilir para bulunmamakta")), 400

        kasa.toplam_para = kasa.toplam_para - silinecek_girdi.tutar
        DB.session.delete(silinecek_girdi)
        DB.session.commit()

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("kasa_girdi_sil").type_index,
            "nesne": 'ButceGirdi',
            "nesne_id": silinecek_girdi.id,
            "etkilenen_nesne": "GelirKasasi",
            "etkilenen_nesne_id": kasa.id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} id'li kasanın {} id'li {} açıklamalı"
                            " {} TL tutarında girdisini sildi.".format(
                current_user.username,
                kasa.id,
                silinecek_girdi.id,
                silinecek_girdi.aciklama,
                silinecek_girdi.tutar
            )
        }
        signal_sender(**signal_payload)

        return jsonify(status="success")
