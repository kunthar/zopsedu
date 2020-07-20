from flask import current_app, render_template, request, redirect, url_for, flash
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user

from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.sessions import SessionHandler
from zopsedu.yonetim.bap_yonetimi.common import genel_ayarlar_guncelle
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import GenelAyarlar
from zopsedu.yonetim.bap_yonetimi.forms.hakem import HakemForm


class HakemAyarlarView(FlaskView):

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["hakem_ayarlari"]),
                   menu_registry={'path': '.yonetim.bap.hakem_ayarlari',
                                  'title': _("Hakem"), 'order': 10})
    @route('/hakem', methods=['GET'])
    def get():
        """Ayarlar ekraninin goruntulendigi view"""
        universite_id = SessionHandler.universite_id()
        genel_ayar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                              aktif_mi=True).first()

        if genel_ayar and genel_ayar.bap_hakem:
            form = HakemForm(**genel_ayar.bap_hakem)
        else:
            form = HakemForm()

        return render_template("hakem.html", form=form)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["hakem_ayarlari"]))
    @route('/hakem', methods=['POST'])
    def post():
        """
        Ayarlarin kaydedildiği view

        """

        form = HakemForm(request.form)
        if form.validate():
            form_data = dict(form.data)
            form_data.pop('csrf_token')
            universite_id = SessionHandler.universite_id()
            genel_ayar = DB.session.query(GenelAyarlar).filter_by(
                universite_id=universite_id,
                aktif_mi=True).first()
            if genel_ayar:
                yeni_ayarlar = genel_ayarlar_guncelle(genel_ayar, "bap_hakem", form_data)
            else:
                yeni_ayarlar = GenelAyarlar(universite_id=universite_id, bap_hakem=form_data)

            DB.session.add(yeni_ayarlar)
            DB.session.commit()
            flash(_("Ayarlarınız başarılı bir şekilde kayıt edildi."))
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("ayarlar").get(
                    "bap_hakem_guncelle").type_index,
                "nesne": 'GenelAyarlar',
                "nesne_id": yeni_ayarlar.id,
                "ekstra_mesaj": "{} adlı kullanıcı, bap hakem ayarlarını güncelledi.".format(
                    current_user.username)
            }
            signal_sender(**signal_payload)
            return redirect(url_for('bap_yonetimi.HakemAyarlarView:get'))

        return render_template("hakem.html", form=form)
