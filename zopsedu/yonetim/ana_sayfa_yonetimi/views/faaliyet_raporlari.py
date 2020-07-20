from flask import render_template, render_template_string, request, url_for, redirect, flash, send_file, jsonify
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


class BapFaaliyetRaporlariAyarlarView(FlaskView):
    """Bap anasyafa view classi"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["ana_sayfa_ayarlari"]),
                   menu_registry={'path': '.yonetim.ana_sayfa.faaliyet_raporlari',
                                  'title': _("Faaliyet Raporları Ayarları")})
    @route('/faaliyet-rapolari-ayarlar', methods=['GET'])
    def bap_faaliyet_raporlari_ayarlar():
        form = AnaSayfaDosyaAyarlari()
        dosyalar = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.faaliyet_raporlari).all()
        return render_template("ana_sayfa_dosya_ayarlari.html",
                               ana_sayfa_dosyalari=form,
                               dosyalar=dosyalar,
                               button_name="Faaliyet Raporu Ekle",
                               route_name="BAP Faaliyet Raporları Ayarları",
                               route=render_template_string(
                                   """
                                   {{url_for("ana_sayfa_yonetimi.BapFaaliyetRaporlariAyarlarView:bap_faaliyet_raporlari_ayarlar_kaydet")}}
                                   """)
                               )

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["ana_sayfa_ayarlari"]))
    @route('/faaliyet-rapolari-ayarlar-kaydet', methods=['POST'])
    def bap_faaliyet_raporlari_ayarlar_kaydet():
        form = AnaSayfaDosyaAyarlari(request.form)
        ana_sayfa_dosya = request.files.get(form.file_id.name, None)
        dosya_id = None
        if not form.validate():
            flash("Lütfen uygun dosya uzantısı olan bir dosya yükleyiniz.")
            return redirect(
                url_for('ana_sayfa_yonetimi.BapFaaliyetRaporlariAyarlarView:bap_faaliyet_raporlari_ayarlar'))

        if ana_sayfa_dosya:
            bap_belge = BAPBelge()
            _ana_sayfa_dosya = File(content=ana_sayfa_dosya)
            try:
                DB.session.add(_ana_sayfa_dosya)
                DB.session.flush()
                bap_belge.file_id = _ana_sayfa_dosya.id
                dosya_id = _ana_sayfa_dosya.id
                bap_belge.adi = ana_sayfa_dosya.filename
                bap_belge.tur = BAPBelgeTipi.faaliyet_raporlari
                DB.session.add(bap_belge)
                DB.session.commit()
            except Exception as exc:
                DB.session.rollback()
                CustomErrorHandler.error_handler(hata="Faaliyet Raporu oluşturulurken hata"
                                                      "oluştu.Hata: {}".format(exc))
                flash("Lütfen uygun dosya uzantısı olan bir dosya yükleyiniz.")
                return redirect(
                    url_for('ana_sayfa_yonetimi.BapFaaliyetRaporlariAyarlarView:bap_faaliyet_raporlari_ayarlar'))

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                "faaliyet_raporu_eklendi").type_index,
            "nesne": 'Faaliyet Raporu Ayarları',
            "nesne_id": dosya_id,
            "ekstra_mesaj": "Faaliyet Raporu eklendi: {}".format(dosya_id),
        }
        signal_sender(**signal_payload)

        flash("Faaliyet raporu başarılı bir şekilde kaydedilmiştir.")

        return redirect(url_for('ana_sayfa_yonetimi.BapFaaliyetRaporlariAyarlarView:bap_faaliyet_raporlari_ayarlar'))

    @staticmethod
    @login_required
    @route('/<int:belge_id>', methods=["POST"], endpoint='dosya_indir')
    def ek_dosya_indir(belge_id):

        """Gundem Ek Belgeler"""

        belge = BAPBelge.query.filter(BAPBelge.file_id == belge_id).one()

        return send_file(
            belge.file.file_object,
            as_attachment=True,
            attachment_filename=belge.file.content.file.filename,
            mimetype=belge.file.content.content_type
        )

    @staticmethod
    @login_required
    @route('/rapor-sil', methods=["POST"], endpoint='dosya_sil')
    def dosya_sil():
        belge_id = request.get_json()['file_id']

        try:
            BAPBelge.query.filter(BAPBelge.id == belge_id).delete()
            DB.session.commit()
        except Exception as exc:
            CustomErrorHandler.error_handler(hata="BAP Belge silinirken bir hata"
                                                  "oluştu.Hata: {}".format(exc))
            return jsonify(status="error"), 400

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                "bap_belge_silindi").type_index,
            "nesne": 'BAPBelge',
            "nesne_id": belge_id,
            "ekstra_mesaj": "BAP Belge silindi: {}".format(belge_id),
        }

        signal_sender(**signal_payload)

        return jsonify(status="success")
