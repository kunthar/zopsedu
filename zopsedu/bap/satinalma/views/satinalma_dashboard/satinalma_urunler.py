"""BAP Satinalma Yapilan işlemler modülü View Modulu"""
from decimal import Decimal

from flask import render_template, abort
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required

from zopsedu.auth.lib import Permission, auth, Role as RoleReq
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.satinalma.views.commons import get_satinalma_with_related_fields, \
    get_satinalma_next_states_info, \
    get_satinalma_actions_info
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.bap.satinalma.lib.common import kdv_dahil_fiyat_hesabi


class SatinalmaUrunlerListesiView(FlaskView):
    """
        Satinalma ürünleri listeleyen view
    """

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_urun_listesi_goruntuleme"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/urun-listesi', methods=['GET'],
           endpoint='satinalma_urunler_listele')
    def satinalma_urunler_listele(self, satinalma_id):
        """
        Satinalma ürünlerine ulasmak icin kullanilir
        :param satinalma_id: satinalma_id(int)
        :return: http response
        """

        try:
            satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
            states_info = get_satinalma_next_states_info(satinalma_id=satinalma_id)
            actions_info = get_satinalma_actions_info(satinalma_id=satinalma_id)
            proje = DB.session.query(Proje).filter(Proje.id == satinalma.proje_id).first()

            talep_kalemleri_with_siparis_info = []
            for talep_kalemi in satinalma.talep_kalemleri:
                data = {
                    "kalem_adi": talep_kalemi.proje_kalemi.ad,
                    "kalem_gerekce": talep_kalemi.proje_kalemi.gerekce,
                    "birim": talep_kalemi.proje_kalemi.birim.value,
                    "miktar": talep_kalemi.talep_miktari,
                    "tutar": talep_kalemi.proje_kalemi.toplam_butce / talep_kalemi.proje_kalemi.toplam_miktar * talep_kalemi.talep_miktari,
                    "teknik_sartname_id": talep_kalemi.teknik_sartname_file_id,
                    "firma_adi": "-",
                    "teslimat_suresi": "-",
                    "kdv_dahil_teklif": 0,
                    "siparis_takip_no": "-",
                    "siparis_durumu": "-"
                }
                if talep_kalemi.siparis_takip:
                    kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                                                              talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani)
                    data.update({
                        "firma_adi": talep_kalemi.siparis_takip.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                        "teslimat_suresi": talep_kalemi.siparis_takip.kazanan_firma_teklif.teslimat_suresi,
                        "kdv_dahil_teklif": kdv_dahil_teklif,
                        "siparis_takip_no": talep_kalemi.siparis_takip.siparis_numarasi,
                        "siparis_durumu": talep_kalemi.siparis_takip.siparis_durumu.value if talep_kalemi.siparis_takip.siparis_durumu else "-"
                    })
                talep_kalemleri_with_siparis_info.append(data)

        except Exception as exc:
            CustomErrorHandler.error_handler(hata="Satinalma ürün listesi görüntülenirken hata oluştu."
                                                  "Hata: {}, Satinalma id: {}".format(satinalma_id,
                                                                                      exc)
                                             )
            return abort(500)

        return render_template("satinalma_dashboard/satinalma_urunler.html",
                               talep_kalemleri_with_siparis_info=talep_kalemleri_with_siparis_info,
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               proje=proje,
                               actions_info=actions_info,
                               states_info=states_info)
