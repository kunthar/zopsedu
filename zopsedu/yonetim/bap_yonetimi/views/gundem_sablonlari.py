"""BAP GundemSablonlari View Modulu"""
from flask import render_template, request, url_for, redirect, flash, jsonify
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.auth.lib import Permission, auth
from zopsedu.lib.db import DB
from zopsedu.models import GundemSablon
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.yonetim.bap_yonetimi.forms.gundem_sablonlari import GundemSablonEkleForm, GundemSablonDuzenleForm


class GundemSablonlariView(FlaskView):
    """Gundem Sablon ile ilgili islemler Viewi"""

    excluded_methods = [
        "qry",
        "gundem_sablon_ekle_form",
        "user_id"
    ]

    @property
    def qry(self):
        """GundemSablon BaseQuery"""
        return DB.session.query(GundemSablon)

    @property
    def user_id(self):
        """Kullanici idsi dondurur"""
        return current_user.id

    @property
    def gundem_sablon_ekle_form(self):
        """Gundem Sablonu Ekleme Formu dondurur"""
        gundem_sablon_ekle_form = GundemSablonEkleForm(request.form)
        return gundem_sablon_ekle_form

    @property
    def gundem_sablon_duzenle_form(self):
        """Gundem Sablonu Duzenleme Formu dondurur"""
        gundem_sablon_duzenle_form = GundemSablonDuzenleForm(request.form)
        return gundem_sablon_duzenle_form

    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["gundem_sablonu_listeleme"]),
                   menu_registry={'path': '.yonetim.bap.sablon_listesi',
                                  'title': _("Gündem Şablonları"), "order": 1})
    @route("/listesi")
    def liste(self):
        """Gundem Sablon Listesi Ekrani"""
        sablon_listesi = self.qry.all()
        return render_template("gundem_sablonlari.html",
                               sablon_listesi=sablon_listesi,
                               gundem_sablon_ekle_form=self.gundem_sablon_ekle_form,
                               gundem_sablon_duzenle_form=self.gundem_sablon_duzenle_form, )

    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["gundem_sablonu_ekleme"]))
    @route("/gundem-sablon-ekle", methods=["POST"], endpoint='gundem_sablon_ekle')
    def gundem_sablon_ekle(self):
        """Gundem Sablonu Ekleme"""
        gundem_sablon_ekle_form = self.gundem_sablon_ekle_form
        data = GundemSablon.data_to_dict(gundem_sablon_ekle_form.data)
        sablon = GundemSablon(**data)
        try:
            DB.session.add(sablon)
            DB.session.commit()
        except IntegrityError:
            DB.session.rollback()
            flash(_("Aynı şablon tipi sadece bir kere oluşturulabilir!"))
            return redirect(url_for('bap_yonetimi.GundemSablonlariView:liste'))
        flash(_("Gündem Şablonu başarıyla eklenmiştir."))
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("gundem_sablon_ekle").type_index,
            "nesne": 'Gundem Sablon',
            "nesne_id": sablon.id,
            "ekstra_mesaj": "{} adlı kullanıcı gundem sablonu kaydetti.".format(
                current_user.username),
        }
        signal_sender(**signal_payload)
        return redirect(url_for('bap_yonetimi.GundemSablonlariView:liste'))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["gundem_sablonu_duzenleme"]))
    @route("/gundem-sablon-duzenle", methods=["GET"], endpoint='gundem_sablon_duzenle')
    def gundem_sablon_duzenle():
        """Gundem Sablonu Duzenleme"""
        sablon_id = int(request.args['sablon_id'])

        sablon = DB.session.query(
            GundemSablon
            ).filter(
                GundemSablon.id == sablon_id
                ).one_or_none()

        data = {
            "sablon_tipi": sablon.sablon_tipi.name,
            "kategori": sablon.kategori.name,
            "aciklama": sablon.aciklama,
            "karar": sablon.aciklama
        }

        return jsonify(data)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["gundem_sablonu_duzenleme"]))
    @route("/gundem-sablon-duzenle-post", methods=["POST"], endpoint='gundem_sablon_duzenle_post')
    def gundem_sablon_duzenle_post():
        """Gundem Sablonu Duzenleme Kayit"""
        sablon_id = request.args['sablon_id']

        sablon = DB.session.query(
            GundemSablon
            ).filter(
                GundemSablon.id == sablon_id
                ).one_or_none()

        gundem_sablon_duzenle_form = GundemSablonDuzenleForm(request.form)

        sablon.sablon_tipi = gundem_sablon_duzenle_form.duzenle.sablon_tipi.data
        sablon.kategori = gundem_sablon_duzenle_form.duzenle.kategori.data
        sablon.aciklama = gundem_sablon_duzenle_form.duzenle.aciklama.data
        sablon.karar = gundem_sablon_duzenle_form.duzenle.karar.data
        DB.session.commit()

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("gundem_sablon_guncelle").type_index,
            "nesne": 'Gundem Sablon',
            "nesne_id": sablon.id,
            "ekstra_mesaj": "{} adlı kullanıcı {} id'li gundem sablonu guncelledi.".format(
                current_user.username,
                sablon.id
            )
        }
        signal_sender(**signal_payload)

        return redirect(url_for('bap_yonetimi.GundemSablonlariView:liste'))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["gundem_sablonu_silme"]))
    @route("/gundem-sablon-sil/<int:sablon_id>/", methods=["DELETE"], endpoint='gundem_sablon_sil')
    def gundem_sablon_sil(sablon_id):
        """Gundem Sablonu Silme"""

        sablon = DB.session.query(
            GundemSablon
            ).filter(
                GundemSablon.id == sablon_id
                ).one_or_none()

        if sablon:
            DB.session.delete(sablon)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("gundem_sablon_sil").type_index,
                "nesne": 'Gundem Sablon',
                "nesne_id": sablon.id,
                "ekstra_mesaj": "{} adlı kullanıcı {} id'li gundem sablonu sildi.".format(
                    current_user.username,
                    sablon.id
                )
            }
            signal_sender(**signal_payload)
            return jsonify(status='success')

        DB.session.rollback()
        CustomErrorHandler.error_handler()

        return jsonify(status="error"), 400
