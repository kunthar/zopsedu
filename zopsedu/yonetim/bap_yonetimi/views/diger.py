"""Bap Genel Ayarlari Diger Modulu"""
from flask import  render_template, request, flash
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import current_user, login_required

from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.sessions import SessionHandler
from zopsedu.models.ayarlar import GenelAyarlar
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.yonetim.bap_yonetimi.common import genel_ayarlar_guncelle
from zopsedu.yonetim.bap_yonetimi.forms.diger import DigerFormu


class DigerAyarlariView(FlaskView):
    """
    Bap ayarları diger bölümü
    """

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["diger_ayarlar"]),
                   menu_registry={'path': '.yonetim.bap.diger_ayarlari',
                                  'title': _("Diğer"), "order": 15})
    @route('/diger', methods=['GET'])
    def diger_get():
        """
        "Diger" ayarlarinin görüntülendigi view
        """
        diger_formu = DigerFormu()
        universite_id = SessionHandler.universite_id()
        genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(
            universite_id=universite_id,
            aktif_mi=True
        ).first()

        if genel_ayarlar and genel_ayarlar.bap_diger:
            diger_formu = DigerFormu(**genel_ayarlar.bap_diger)

        return render_template('diger.html', diger_formu=diger_formu)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["diger_ayarlar"]),
                   menu_registry={'path': '.yonetim.bap.diger_ayarlari',
                                  'title': _("Diğer"), "order": 15})
    @route('/diger', methods=['POST'])
    def diger_post():
        """
        "Diger" ayarlarinin kaydedildigi view
        """
        diger_formu = DigerFormu(request.form)
        if diger_formu.validate():
            universite_id = SessionHandler.universite_id()
            diger_ayarlar_data = dict(diger_formu.data)
            diger_ayarlar_data.pop('csrf_token')
            diger_ayarlar_data['yayinlar'].pop('csrf_token')
            diger_ayarlar_data['firma'].pop('csrf_token')
            diger_ayarlar_data['diger'].pop('csrf_token')
            genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                                     aktif_mi=True).first()
            if genel_ayarlar:
                yeni_ayarlar = genel_ayarlar_guncelle(genel_ayarlar,
                                                      "bap_diger",
                                                      diger_ayarlar_data)
            else:
                yeni_ayarlar = GenelAyarlar(universite_id=universite_id,
                                            bap_diger=diger_ayarlar_data)
            DB.session.add(yeni_ayarlar)
            DB.session.commit()

            flash(_("İşlem başarıyla gerçekleşti."))

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("ayarlar").get(
                    "bap_proje_guncelle").type_index,
                "nesne": 'GenelAyarlar',
                "nesne_id": yeni_ayarlar.id,
                "ekstra_mesaj": "{} adlı kullanıcı, bap diger ayarlarını güncelledi.".format(
                    current_user.username)
            }
            signal_sender(**signal_payload)

        return render_template('diger.html', diger_formu=diger_formu)
