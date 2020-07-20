from flask import render_template, render_template_string, request, url_for, redirect, flash
from flask_classful import FlaskView, route
from flask_login import login_required
from flask_babel import gettext as _
from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.belge import BAPBelge
from zopsedu.bap.models.helpers import BAPBelgeTipi
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import File
from zopsedu.yonetim.ana_sayfa_yonetimi.forms.ana_sayfa_dosyalari import AnaSayfaDosyaAyarlari


class MevzuatAyarlarView(FlaskView):
    """Bap anasyafa view classi"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["ana_sayfa_ayarlari"]),
                   menu_registry={'path': '.yonetim.ana_sayfa.mevzuat_ayarlari',
                                  'title': _("Mevzuat Ayarları")})
    @route('/mevzuat-ayarlar', methods=['GET'])
    def mevzuat_ayarlar():
        form = AnaSayfaDosyaAyarlari()
        dosyalar = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.mevzuat).all()
        return render_template("ana_sayfa_dosya_ayarlari.html",
                               ana_sayfa_dosyalari=form,
                               dosyalar=dosyalar,
                               button_name="Mevuat Ekle",
                               route_name="Mevzuat Ayarları",
                               route=render_template_string(
                                   """
                                   {{url_for("ana_sayfa_yonetimi.MevzuatAyarlarView:mevzuat_ayarlar_kaydet")}}
                                   """)
                               )

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["ana_sayfa_ayarlari"]))
    @route('/mevzuat-ayarlar-kaydet', methods=['POST'])
    def mevzuat_ayarlar_kaydet():
        form = AnaSayfaDosyaAyarlari(request.form)
        ana_sayfa_dosya = request.files.get(form.file_id.name, None)
        dosya_id = None
        if not form.validate():
            flash("Lütfen uygun dosya uzantısı olan bir dosya yükleyiniz.")
            return redirect(
                url_for('ana_sayfa_yonetimi.MevzuatAyarlarView:mevzuat_ayarlar'))

        if ana_sayfa_dosya:
            bap_belge = BAPBelge()
            _ana_sayfa_dosya = File(content=ana_sayfa_dosya)
            try:
                DB.session.add(_ana_sayfa_dosya)
                DB.session.flush()
                bap_belge.file_id = _ana_sayfa_dosya.id
                dosya_id = _ana_sayfa_dosya.id
                bap_belge.adi = ana_sayfa_dosya.filename
                bap_belge.tur = BAPBelgeTipi.mevzuat
                DB.session.add(bap_belge)
                DB.session.commit()
            except Exception as exc:
                DB.session.rollback()
                CustomErrorHandler.error_handler(hata="Mevzuat oluşturulurken hata"
                                                      "oluştu.Hata: {}".format(exc))
                flash("Lütfen uygun dosya uzantısı olan bir dosya yükleyiniz.")
                return redirect(
                    url_for('ana_sayfa_yonetimi.MevzuatAyarlarView:mevzuat_ayarlar'))

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                "mevzuat_eklendi").type_index,
            "nesne": 'Ana Sayfa Mevzuat',
            "nesne_id": dosya_id,
            "ekstra_mesaj": "Mevzuat eklendi: {}".format(dosya_id),
        }
        signal_sender(**signal_payload)

        flash("Mevzuat başarılı bir şekilde kaydedilmiştir.")

        return redirect(url_for('ana_sayfa_yonetimi.MevzuatAyarlarView:mevzuat_ayarlar'))
