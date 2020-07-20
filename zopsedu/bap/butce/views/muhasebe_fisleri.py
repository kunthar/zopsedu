from flask import render_template, render_template_string, abort
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required
from sqlalchemy import desc

from zopsedu.auth.lib import Role as RoleReq
from zopsedu.bap.lib.query_helpers import BapQueryHelpers
from zopsedu.bap.models.muhasebe_fisi import MuhasebeFisi
from zopsedu.lib.db import DB
from zopsedu.auth.lib import Permission, auth
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import Sablon


class MuhasebeFisleriView(FlaskView):
    """Bap Bütçe Kodları view classi"""

    @staticmethod
    @login_required
    @route('/liste', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]["muhasebe_fisleri_goruntuleme"]),
                   menu_registry={"path": ".bap.butce.muhasebe_fisleri",
                                  "title": _("Muhasebe Fişleri")})
    def butce_kodlari_goruntuleme_listele():
        # todo: monkey patch !!!
        # todo: server side yapilacak
        muhasebe_fisleri = DB.session.query(MuhasebeFisi).all()
        return render_template("muhasebe_fisleri_listeleme.html",
                               muhasebe_fisleri=muhasebe_fisleri)

    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["butce"]["muhasebe_fisleri_goruntuleme"]),
        Or(RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/muhasebe-fisi/<int:muhasebe_fis_id>', methods=['GET'])
    def get_odeme_emri(self, muhasebe_fis_id):
        """
        Odeme emri sablonunu ilgili muhasebe fisi alanlari ile render edip kullaniciya doner
        """
        try:
            muhasebe_fisi_data = BapQueryHelpers.get_muhasebe_fisi_bilgileri(muhasebe_fis_id)
            # sablon tipi id 49 --> Ödeme Emri Şablonu
            odeme_emri_sablonu = DB.session.query(Sablon).filter(
                Sablon.sablon_tipi_id == 49,
                Sablon.kullanilabilir_mi == True
            ).order_by(desc(Sablon.updated_at)).first()
            muhasebe_fisi = DB.session.query(MuhasebeFisi).filter(
                MuhasebeFisi.id == muhasebe_fis_id).first()
            muhasebe_fisi.odeme_emri_tamamlandi = True
            DB.session.commit()
            return render_template_string(odeme_emri_sablonu.sablon_text, data=muhasebe_fisi_data)

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(hata="Muhasebe fişi ödeme emrine çevrilirken bir hata "
                                                  "oluştu.Hata: {}, Muhasebe Fisi id: {}".format(
                muhasebe_fis_id,
                exc)
            )
            return abort(500)
