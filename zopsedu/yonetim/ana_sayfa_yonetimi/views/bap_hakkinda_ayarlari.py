from flask import render_template, request, flash, redirect, url_for
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_babel import gettext as _
from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.belge import BAPBelge
from zopsedu.bap.models.helpers import BAPBelgeTipi
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.yonetim.ana_sayfa_yonetimi.forms.bap_hakkinda import BAPHakkindaForm


class BapHakkindaAyarlarView(FlaskView):
    """Bap anasyafa view classi"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["ana_sayfa_ayarlari"]),
                   menu_registry={'path': '.yonetim.ana_sayfa.bap_hakkinda_ayarlari',
                                  'title': _("BAP Hakkında Ayarları")})
    @route('/bap-hakkinda-ayarlari', methods=['GET'])
    def bap_hakkinda_ayarlar():
        form = BAPHakkindaForm()
        metin = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.bap_hakkinda).first()
        if metin:
            form.bap_hakkinda_metni.data = metin.aciklama
        return render_template("bap_hakkinda_ayarlari.html", bap_hakkinda=form)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["ana_sayfa_ayarlari"]))
    @route('/bap-hakkinda-ayarlari-kaydet', methods=['POST'])
    def bap_hakkinda_ayarlar_kaydet():
        form = BAPHakkindaForm(request.form)
        metin = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.bap_hakkinda).first()
        if form.validate():
            if metin:
                metin.aciklama = form.bap_hakkinda_metni.data
                metin.tur = BAPBelgeTipi.bap_hakkinda
            else:
                metin = BAPBelge()
                metin.aciklama = form.bap_hakkinda_metni.data
                metin.tur = BAPBelgeTipi.bap_hakkinda
                DB.session.add(metin)
            try:
                DB.session.commit()
                flash("BAP Hakkında metni başarı ile kaydedildi")
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                        "bap_hakkinda_metni_eklendi").type_index,
                    "nesne": 'BAP Hakkında ayarları',
                    "nesne_id": current_user.id,
                    "ekstra_mesaj": "BAP Hakkında metni eklendi",
                }
                signal_sender(**signal_payload)
            except Exception as exc:
                DB.session.rollback()
                CustomErrorHandler.error_handler(hata="BAP Hakkında metni oluşturulurken bir hata"
                                                      "oluştu.Hata: {}".format(exc))
                flash("Bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.")
        else:
            flash("Bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.")

        return redirect(url_for('ana_sayfa_yonetimi.BapHakkindaAyarlarView:bap_hakkinda_ayarlar'))

