"""Bap Firma Yonetimi modulu"""
from flask import render_template, request, flash, jsonify, abort, send_file, redirect, url_for
from flask_allows import Or
from flask_login import current_user, login_required
from flask_babel import lazy_gettext as _
from flask_classful import FlaskView, route
from sqlalchemy.orm import joinedload

from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.yonetim.firma_yonetimi.form import FirmaKayitFormu
from zopsedu.bap.lib.auth import FirmaYetkilisi
from zopsedu.lib.db import DB
from zopsedu.models import BapFirma, File


class BapFirmaView(FlaskView):
    """Bap anasyafa view classi"""

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["yonetim"]["firma_yonetimi"]["firma_listesi_goruntuleme"]),
           Role("BAP Yetkilisi")),
        menu_registry={'path': '.yonetim.firma_yonetimi.firma_listesi',
                       'title': _("Firma Listesi")}
        )
    @route('/firma-liste', methods=['GET'])
    def firma_liste():
        """Firma Listesi Ekrani"""
        firmalar = DB.session.query(BapFirma).options(joinedload(BapFirma.user)).all()
        onay_bekleyen_firmalar = []
        reddedilen_firmalar = []
        kabul_edilen_firmalar = []

        for firma in firmalar:
            if firma.onaylandi:
                kabul_edilen_firmalar.append(firma)
            elif firma.reddedildi_mi:
                reddedilen_firmalar.append(firma)
            else:
                onay_bekleyen_firmalar.append(firma)

        return render_template("firma_liste.html",
                               kabul_edilen_firmalar=kabul_edilen_firmalar,
                               reddedilen_firmalar=reddedilen_firmalar,
                               onay_bekleyen_firmalar=onay_bekleyen_firmalar)

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["yonetim"]["firma_yonetimi"]["firma_goruntuleme"]),
           Role("BAP Yetkilisi")))
    @route('/firma-detay/<int:firma_id>', methods=['GET'])
    def firma_detay(firma_id):
        """Firma Listesi Ekrani"""

        firma = DB.session.query(BapFirma).filter(BapFirma.id == firma_id).one()
        form = FirmaKayitFormu(**firma.to_dict())

        return render_template("firma_bilgileri.html", firma=firma, form=form)

    @staticmethod
    @login_required
    @auth.requires(Or(Permission(*permission_dict["yonetim"]["firma_yonetimi"]["firma_guncelleme"]),
                      FirmaYetkilisi()))
    @route('/firma-detay-guncelle/<int:firma_id>', methods=['POST'],
           endpoint='firma_detay_guncelle')
    def firma_detay_guncelle(firma_id):
        """Firma Listesi Ekrani"""

        firma = DB.session.query(BapFirma).filter(BapFirma.id == firma_id).one()
        form = FirmaKayitFormu(request.form)
        form.yetkili_email.validators = None
        form.yetkili_adi.validators = None
        form.yetkili_soyadi.validators = None
        form.adres.validators = None
        form.firma_faaliyet_belgesi_id.validators = None
        form.telefon.validators = None
        form.email.validators = None
        firma.yetkili_adi = form.yetkili_adi.data
        firma.yetkili_soyadi = form.yetkili_soyadi.data
        firma.yetkili_email = form.yetkili_email.data
        firma.adres = form.adres.data
        firma_faaliyet_belgesi_id = request.files.get(form.firma_faaliyet_belgesi_id.name)
        if firma_faaliyet_belgesi_id:
            firma.firma_faaliyet_belgesi_id = firma_faaliyet_belgesi_id

        firma.telefon = form.telefon.data
        firma.email = form.email.data
        DB.session.commit()
        flash("Firma bilgileri başarıyla güncellenmiştir.")
        return redirect(url_for('firma.firma_detay', firma_id=firma.id))

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["yonetim"]["firma_yonetimi"]["firma_goruntuleme"]),
           Role("BAP Yetkilisi")))
    @route('/faaliyet-belgesi-indir/<int:firma_id>', methods=['GET'],
           endpoint="firma_faaliyet_belgesi_indir")
    def firma_faaliyet_belgesi_indir(firma_id):
        """Firma Listesi Ekrani"""
        firma = DB.session.query(BapFirma).get(firma_id)
        try:
            belge = DB.session.query(File).filter(File.id == firma.firma_faaliyet_belgesi_id).one()
            return send_file(
                belge.file_object,
                attachment_filename=belge.content.file.filename,
                as_attachment=True,
                mimetype=belge.content.file.content_type
            )
        except Exception as exc:
            CustomErrorHandler.error_handler()
            return abort(400)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["yonetim"]["firma_yonetimi"]["firma_onaylama"]),
                      Role("BAP Yetkilisi"), Role("BAP Admin")))
    @route('/firma-onay/<int:firma_id>', methods=['POST'])
    def firma_onay(self, firma_id):
        onay = bool(int(request.get_json().get('onay')))
        firma = DB.session.query(BapFirma).filter(BapFirma.id == firma_id).first()

        if not onay:
            firma.onaylandi = False
            firma.reddedildi_mi = True
            firma.faaliyet_durumu = False
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "firma_red").type_index,
                "nesne": 'BapFirma',
                "nesne_id": firma.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} idli firmayı reddetti.".format(
                    current_user.username, firma.id)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success")
        else:
            firma.onaylandi = True
            firma.faaliyet_durumu = True
            firma.reddedildi_mi = False

            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "firma_onay").type_index,
                "nesne": 'BapFirma',
                "nesne_id": firma.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} idli firmayı onayladı.".format(
                    current_user.username, firma.id)
            }
            signal_sender(**signal_payload)
            flash(
                "Firma başarıyla onaylanmıştır..")
            return jsonify(status="success")
