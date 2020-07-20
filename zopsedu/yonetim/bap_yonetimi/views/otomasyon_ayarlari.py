"""Otomasyon Ayarlari Modulu"""

from flask import current_app, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import current_user, login_required

from werkzeug.datastructures import ImmutableMultiDict


from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict

from zopsedu.lib.db import DB
from zopsedu.lib.mail import init_mail, connection_test
from zopsedu.lib.sessions import SessionHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models.ayarlar import SiteAyarlari
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.yonetim.bap_yonetimi.forms.ayar import AyarlarForm
from zopsedu.yonetim.bap_yonetimi.forms.mail_sunucu_ayarlari import MailSunucuAyarlariForm


class AyarlarView(FlaskView):
    """Otomasyon ayarları view classi"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["otomasyon_ayarlari"]),
                   menu_registry={'path': '.yonetim.bap.uygulama_genel_ayarlar',
                                  'title': _("Genel Ayarlar"), "order": 3})
    @route('/otomasyon-ayarlari', methods=['GET'])
    def ayarlari_goruntule():
        """Ayarlar ekraninin goruntulendigi view"""
        form = AyarlarForm()
        ayar = DB.session.query(SiteAyarlari).first()
        logo_url = None
        if ayar:
            params = {}
            for key, value in ayar.params.items():
                params[key] = value
            form = AyarlarForm(**params)
            form.site_ayarlari.yoksis_kullanici_bilgisi.yoksis_password.data = ayar.yoksis_password
            form.site_ayarlari.yoksis_kullanici_bilgisi.yoksis_kullanici_adi.data = ayar.yoksis_kullanici_no
            if ayar.logo:
                logo_url = current_app.wsgi_app.url_for(ayar.logo.path)

        return render_template("otomasyon-ayarlar.html", form=form, logo_url=logo_url)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["otomasyon_ayarlari"]))
    @route('/otomasyon-ayarlari', methods=['POST'], endpoint='kaydet')
    def ayarlari_kaydet():
        """
        Ayarlarin kaydedildiği view

        """

        form = request.form
        ayarlar_form = AyarlarForm(form)

        universite_id = ayarlar_form.site_ayarlari.genel.universite_id.data if ayarlar_form.site_ayarlari.genel.universite_id.data else current_app.config["UNIVERSITE_CONFIG_ID"]

        if not ayarlar_form.validate():
            flash(_("Beklenmeyen bir hata oluştu. Lütfen gönderdiğiniz formu kontrol ediniz"))
            return render_template("otomasyon-ayarlar.html", form=ayarlar_form)
        ayar = DB.session.query(SiteAyarlari).filter_by(universite_id=universite_id).first()
        if not ayar:
            ayar = SiteAyarlari()

        ayar.universite_id = universite_id

        if ayar and ayar.mail_password and not ayarlar_form.mail_sunucu_ayarlari.mail_password.data:
            ayarlar_form.mail_sunucu_ayarlari.mail_password.data = ayar.mail_password
            ayarlar_form.mail_sunucu_ayarlari.mail_password_repeat.data = ayar.mail_password

        logo = request.files.get('site_ayarlari-genel-logo', None)
        ayarlar = {
            "site_ayarlari": {
                "genel": {
                    "site_adi": ayarlar_form.site_ayarlari.genel.site_adi.data,
                    "universite_id": ayarlar_form.site_ayarlari.genel.universite_id.data,

                    "bap_kisa_adi": ayarlar_form.site_ayarlari.genel.bap_kisa_adi.data,
                    "sehir": ayarlar_form.site_ayarlari.genel.sehir.data,
                    "adres": ayarlar_form.site_ayarlari.genel.adres.data,
                    "telefon": ayarlar_form.site_ayarlari.genel.telefon.data,
                    "faks": ayarlar_form.site_ayarlari.genel.faks.data
                },
                "sozlesme_yetkilisi": {
                    "gorevi": ayarlar_form.site_ayarlari.sozlesme_yetkilisi.gorevi.data,
                    "adi_soyadi": ayarlar_form.site_ayarlari.sozlesme_yetkilisi.adi_soyadi.data,
                }
            },
            "mail_sunucu_ayarlari": {
                "mail_server": ayarlar_form.mail_sunucu_ayarlari.mail_server.data,
                "mail_port": ayarlar_form.mail_sunucu_ayarlari.mail_port.data,
                "mail_use_tls": ayarlar_form.mail_sunucu_ayarlari.mail_use_tls.data,
                "mail_use_ssl": ayarlar_form.mail_sunucu_ayarlari.mail_use_ssl.data,
                "mail_username": ayarlar_form.mail_sunucu_ayarlari.mail_username.data,
                "mail_default_sender": ayarlar_form.mail_sunucu_ayarlari.mail_default_sender.data,
                "mail_max_emails": ayarlar_form.mail_sunucu_ayarlari.mail_max_emails.data,
            },
            "ebys_ayarlari": {
                "p_user_id": ayarlar_form.ebys_ayarlari.p_user_id.data if ayarlar_form.ebys_ayarlari.p_user_id else None,
                "p_token": ayarlar_form.ebys_ayarlari.p_token.data if ayarlar_form.ebys_ayarlari.p_token else None,
                "integration_url": ayarlar_form.ebys_ayarlari.integration_url.data if ayarlar_form.ebys_ayarlari.integration_url else None,
                "system_integration_url": ayarlar_form.ebys_ayarlari.system_integration_url.data if ayarlar_form.ebys_ayarlari.system_integration_url else None,
                "docdefid": ayarlar_form.ebys_ayarlari.docdefid.data if ayarlar_form.ebys_ayarlari.docdefid else None

            }
        }
        if ayarlar_form.site_ayarlari.yoksis_kullanici_bilgisi.yoksis_password.data is not '':
            ayar.yoksis_password = ayarlar_form.site_ayarlari.yoksis_kullanici_bilgisi.yoksis_password.data
            ayar.yoksis_kullanici_no = ayarlar_form.site_ayarlari.yoksis_kullanici_bilgisi.yoksis_kullanici_adi.data
        ayar.params = ayarlar
        if logo:
            try:
                ayar.logo = logo
            except ValueError as vexc:
                flash(str(vexc))
                return render_template("otomasyon-ayarlar.html", form=ayarlar_form)

        if ayarlar_form.mail_sunucu_ayarlari.mail_password.data is not '':
            ayar.mail_password = ayarlar_form.mail_sunucu_ayarlari.mail_password.data

        try:
            DB.session.add(ayar)
            DB.session.commit()
        except Exception as exc:
            DB.session.rollback()
            flash(_("Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyiniz"))

        current_app.extensions['redis'].set(current_app.config['UNIVERSITE_ID'], universite_id)
        SessionHandler.ebys_ayarlari(update=True)
        init_mail()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("ayarlar").get("ayar_guncelle").type_index,
            "nesne": 'Site Ayarlari',
            "nesne_id": ayar.id,
            "ekstra_mesaj": "{} adlı kullanıcı uygulama ayarlarini kaydetti.".format(
                current_user.username),
        }
        signal_sender(**signal_payload)

        flash("Ayarlarınız başarılı bir şekilde kaydedilmiştir")
        return redirect(url_for('bap_yonetimi.AyarlarView:ayarlari_goruntule'))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["otomasyon_ayarlari"]))
    @route('/mail-test', methods=['POST'], endpoint='mail_test')
    def mail_test():
        form_data = request.get_json()["mail-ayarlari-form"]
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form_data])
        mail_form = AyarlarForm(imd)
        config = {
            'mail_use_ssl': mail_form.mail_sunucu_ayarlari.mail_use_ssl.data,
            'mail_use_tls': mail_form.mail_sunucu_ayarlari.mail_use_tls.data,
            'mail_server': mail_form.mail_sunucu_ayarlari.mail_server.data,
            'mail_port': mail_form.mail_sunucu_ayarlari.mail_port.data,
            'mail_username': mail_form.mail_sunucu_ayarlari.mail_username.data,
            'mail_password': mail_form.mail_sunucu_ayarlari.mail_password.data
        }

        try:
            conn_test_result = connection_test(config)
        except Exception as exc:
            return jsonify(status="error",
                           error_message="E-posta sunucusu ayarları doğrulanamadı. Lütfen kontrol ediniz!"), 400

        if not conn_test_result:
            return jsonify(status="error",
                           error_message="E-posta sunucusu ayarları doğrulanamadı. Lütfen kontrol ediniz!"), 400

        return jsonify(status="success")
