"""Proje Dashboard view classları"""
from io import BytesIO
from decimal import Decimal

from flask import render_template, send_file, request, jsonify, abort, redirect, \
    url_for, flash
from flask_allows import Or
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import ProjeYurutucusu, AtanmisHakem
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.proje.forms.dashboard.sozlesme import SozlesmeYukleForm
from zopsedu.bap.proje.lib.proje_islemleri_get import project_management_methods_get
from zopsedu.bap.proje.lib.proje_islemleri_post import project_management_methods_post
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids
from zopsedu.lib.renders import TRenderer
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.proje_state_dispatcher import ProjeStateDispacther
from zopsedu.models import ProjeBelgeleri, AppState, AppAction
from zopsedu.models import File
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields
from zopsedu.models.helpers import StateTypes, ActionTypes
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeDashboardView(FlaskView):
    """
    Proje Dashboard
    """

    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_ozeti_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin'), AtanmisHakem()))
    @route("<int:proje_id>/dashboard/ozet", methods=["GET", "POST"], endpoint="proje_dashboard")
    def proje_dashboard(self, proje_id):
        """
        Proje özeti bilgilerine ulaşmak için kullanılır
        Args:
            proje_id(int): proje id si

        Returns:

        """
        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        atanmis_hakem = AtanmisHakem()
        sozlesme_ekle_form = SozlesmeYukleForm()

        try:
            proje = DB.session.query(Proje).options(
                joinedload(Proje.proje_proje_turu).load_only("ad"),
                joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                    OgretimElemani.personel).load_only("id").joinedload(
                    Personel.person).load_only("ad", "soyad"),
                joinedload(Proje.fakulte).load_only("ad"),
                joinedload(Proje.bolum).load_only("ad"),
                joinedload(Proje.ana_bilim_dali).load_only("ad"),
                joinedload(Proje.bilim_dali).load_only("ad"),
                lazyload(Proje.proje_detayi),
                lazyload(Proje.kabul_edilen_proje_hakemleri),
                lazyload(Proje.proje_hakem_onerileri),
                lazyload(Proje.proje_destekleyen_kurulus),
                joinedload(Proje.proje_kalemleri).lazyload("*"),
            ).filter(Proje.id == proje_id,
                     or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                         Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

            toplam_butce = Decimal("0.00")
            rezerv_butce = Decimal("0.00")
            kullanilan_butce = Decimal("0.00")
            for proje_kalemi in proje.proje_kalemleri:
                toplam_butce += proje_kalemi.toplam_butce
                rezerv_butce += proje_kalemi.rezerv_butce
                kullanilan_butce += proje_kalemi.kullanilan_butce

            kullanilabilir_butce = toplam_butce - rezerv_butce - kullanilan_butce
            kullanilabilir_butce = kullanilabilir_butce.quantize(Decimal(".01"))

            proje_durum = ProjeStateDispacther.current_state_info(proje_id=proje.id)

            possible_next_states = ProjeStateDispacther.possible_next_states_info(
                current_app_state_id=proje_durum.id)

            possible_actions = ProjeStateDispacther.possible_actions(
                current_app_state_id=proje_durum.id)

            actions_info = DB.session.query(AppAction).filter(
                AppAction.action_code.in_(possible_actions)).all()

            states_info = DB.session.query(AppState). \
                filter(AppState.state_code.in_(possible_next_states)).all()

            genel_uyari_mesajlari = proje.proje_proje_turu.genel_uyari_mesajlari
            sozlesme_sablon_id = proje.proje_proje_turu.sozlesme_sablon_id

            proje_durumlari = DB.session.query(
                AppState.state_code.label("state_code"),
                AppState.description.label("state_description"),
                AppState.current_app_state.label("current_app_state"),
            ).filter(
                AppState.state_type == StateTypes.proje
            ).options(lazyload("*")).order_by(AppState.id).all()

            proje_islemleri = DB.session.query(
                AppAction.action_code.label("action_code"),
                AppAction.description.label("action_description"),
            ).filter(
                AppAction.action_type == ActionTypes.proje
            ).order_by(
                AppAction.id
            ).all()

        except SQLAlchemyError as exc:
            CustomErrorHandler.error_handler(
                hata="Proje dashboard ekranı yüklenirken database sorgularında sorun oluştu "
                     "Hata: {}, User id: {}, Proje id: {}".format(exc, current_user.id, proje_id))

            return abort(500)

        # proje.proje_durum
        if not proje:
            pass
            # todo: proje bulunamadı hatası dön
        return render_template("dashboard/proje_ozeti.html",
                               proje=proje,
                               states_info=states_info,
                               actions_info=actions_info,
                               proje_durum=proje_durum,
                               sozlesme_ekle_form=sozlesme_ekle_form,
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               atanmis_hakem=atanmis_hakem,
                               genel_uyari_mesajlari=genel_uyari_mesajlari,
                               kullanilabilir_butce=kullanilabilir_butce,
                               kullanilan_butce=kullanilan_butce,
                               rezerv_butce=rezerv_butce,
                               toplam_butce=toplam_butce,
                               proje_durumlari=proje_durumlari,
                               proje_islemleri=proje_islemleri,
                               sozlesme_sablon_id=sozlesme_sablon_id)

    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_ozeti_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/proje_ek/<int:ek_id>", methods=["POST"], endpoint='proje_eki')
    def proje_ekleri(self, proje_id, ek_id):
        """
        Proje eklerini indirmek icin kullanilir
        Args:
            self:
            proje_id(int): proje idsi
            belge_id(int): projenin belge idsi

        Returns:

        """
        proje = get_proje_with_related_fields(proje_id=proje_id)
        proje_ek = DB.session.query(
            ProjeBelgeleri).filter_by(belge_id=ek_id).first()

        # for belge in proje.proje_belgeleri:
        # if request.method == "POST" and request.form.get(ek.baslik) == str(ek.belge_id):
        context = {**proje.__dict__, 'proje_detay': proje.proje_detayi}

        renderer = TRenderer(
            template=proje_ek.belge.file_object, context=context)
        rendered_document = renderer.render_document()

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("proje_eki_indirildi").type_index,
            "nesne": 'Proje Belgeleri',
            "nesne_id": ek_id,
            "etkilenen_nesne": "Proje",
            "etkilenen_nesne_id": proje_id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} adlı proje ekini indirdi.".format(
                current_user.username,
                proje_ek.belge.content.file.filename)
        }
        signal_sender(**signal_payload)

        return send_file(
            BytesIO(rendered_document),
            as_attachment=True,
            attachment_filename=proje_ek.belge.content.file.filename,
            mimetype='application/vnd.oasis.opendocument.text'
        )

    @staticmethod
    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_sozlesmesi_yukleme"]))
    @route("/dashboard/<int:proje_id>/sozlesme_yukle", methods=["POST"], endpoint="sozlesme_yukle")
    def proje_sozlesmesi_yukle(proje_id):
        """
        Proje sozlemesini Yukleme
        """
        try:
            sozlesme_formu = SozlesmeYukleForm(request.form)
            if sozlesme_formu.validate():
                sozlesme_file = request.files.get(sozlesme_formu.sozlesme_file.name, None)
                if sozlesme_file:
                    file = File(content=sozlesme_file,
                                user_id=current_user.id)
                    DB.session.add(file)
                    DB.session.flush()
                    proje = DB.session.query(Proje).filter(Proje.id == proje_id).first()
                    sozlesme_var_mi = True if proje.proje_sozlesme_id else False
                    proje.proje_sozlesme_id = file.id
                    DB.session.commit()
                    flash(_("Proje Sözleşmesi başarılı bir şekilde yüklenmiştir."))

                    if sozlesme_var_mi:
                        user_activity_message = _("Proje Sözleşmesi Güncellendi")
                    else:
                        user_activity_message = _("Proje Sözleşmesi Yüklendi")

                    revizyon_signal_payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "proje_sozlesmesi_yuklendi").type_index,
                        "nesne": 'Proje',
                        "nesne_id": proje_id,
                        "ekstra_mesaj": "{} adlı kullanıcı, {} numaralı projeye sözleşme yükledi".format(
                            current_user.username, proje.proje_no)
                    }

                    signal_sender(**revizyon_signal_payload)

                    for bap_admin in bap_yetkili_and_admin_ids():
                        payload = {
                            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                                "proje_sozlesmesi_yuklendi").type_index,
                            "ekstra_mesaj": "{} id li projeye sözleşme yüklendi".format(proje.id),
                            "notification_receiver": bap_admin.person_id,
                            "notification_title": user_activity_message,
                            "notification_message": "{} numaralı projenin sözleşmesi {} adlı kullanıcı"
                                                    " tarafından yüklendi.".format(proje.proje_no,
                                                                                   current_user.username),
                            "proje_id": proje.id
                        }

                        signal_sender(log=False, notification=True, **payload)
                else:
                    flash(_("Lütfen proje sözleşmesi yükleyiniz"))
            else:
                flash(_("Sözleşme kaydedilemedi."))
                flash(sozlesme_formu.sozlesme_file.errors[0])
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje sözleşmesi yüklenirken bir hata meydana geldi"
                     "Hata: {}".format(exc)
            )
        return redirect(url_for("proje.proje_dashboard", proje_id=proje_id))

    @staticmethod
    @login_required
    @auth.requires(Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route("/dashboard/<int:proje_id>/", methods=["POST"], endpoint="proje_durum_degistir")
    def proje_durum_degistir(proje_id):
        kod = request.get_json()['kod']

        template = project_management_methods_get[kod](proje_id=proje_id,
                                                       code=kod)

        return jsonify(status="success", template=template)

    @staticmethod
    @login_required
    @auth.requires(Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route("/<int:proje_id>", methods=["POST"], endpoint="proje_durum_kaydet")
    def proje_durum_kaydet(proje_id):

        request_json = request.get_json()
        form = request_json['form']
        kod = request_json['kod']

        try:
            template = project_management_methods_post[kod](proje_id=proje_id,
                                                            code=kod, form=form)
            if not template:
                return jsonify(status="success")

            if type(template) is str:
                return jsonify(status="error",
                               template=template,
                               code=kod,
                               hata_mesaji=""), 400
            return jsonify(status="error",
                           template=template[0],
                           code=kod,
                           hata_mesaji=template[1] if len(template) > 1 else ""), 400

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje ile ilgili işlem yapılırken bir hata oluştu"
                     "Hata: {}, Proje id: {}".format(exc, proje_id)
            )
            return jsonify(status="error", template=None), 500
