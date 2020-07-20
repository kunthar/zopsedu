"""BAP Şablon ve Ek dosyalarini View Modulu"""
from flask import render_template
from flask_allows import And, Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import Permission, auth, Role as RoleReq
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import ProjeYurutucusu, AtanmisHakem
from zopsedu.bap.models.helpers import GorunurlukSecenekleri, ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_turu import ProjeTuru, EkDosya
from zopsedu.lib.db import DB
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, get_next_states_info, \
    get_actions_info
from zopsedu.models import Sablon
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeSablonEkDosyaView(FlaskView):
    """
        Proje şablonlari ve ek dosyalari goruntulendigi view
    """

    @login_required
    @auth.requires(
        Or(And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_sablon_ek_dosya_goruntuleme"]),
               ProjeYurutucusu()), RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin"), AtanmisHakem()))
    @route('/<int:proje_id>/sablon', methods=['GET'], endpoint='sablon_ekdosya_listele')
    def sablon_ekdosya_listele(self, proje_id):
        """
        Projenin şablon cikti ve ek dosyalarina ulasmak icin kullanilir
        """
        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        atanmis_hakem = AtanmisHakem()
        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_proje_turu).load_only(
                "oneri_sablon_id",
                "hakem_degerlendirme_sablon_id",
                "hakem_ara_rapor_sablon_id",
                "ara_rapor_sablon_id",
                "sonuc_raporu_sablon_id",
                "sozlesme_sablon_id",
                "hakem_sonuc_rapor_sablon_id"),
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            joinedload(Proje.proje_belgeleri),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(
            Proje.id == proje_id,
            or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)
        ).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)

        proje_turu = DB.session.query(ProjeTuru).options(
            joinedload(ProjeTuru.cikti),
            joinedload(ProjeTuru.ek_dosyalar).joinedload(EkDosya.belge),
        ).filter_by(id=proje.proje_turu).one()
        ciktilar = []
        for cikti in proje_turu.cikti:
            ciktilar.append({
                "adi": cikti.adi,
                "yurutucu_gorebilir_mi": True if cikti.gorunurluk == GorunurlukSecenekleri.yurutucu_ve_yonetici else False,
                "sablon_id": cikti.sablon_id,
                "sablon_adi": cikti.sablon_belge.adi,
            })

        proje_ek_dosyalar = []
        proje_diger_dosyalar = []
        for ek_dosya in proje_turu.ek_dosyalar:
            for proje_belge in proje.proje_belgeleri:
                if proje_belge.proje_turu_ek_dosya_id == ek_dosya.id:
                    proje_ek_dosyalar.append({
                        # "proje_belge_id",
                        "proje_belge_file_id": proje_belge.belge_id,
                        "proje_belge_aciklama": proje_belge.aciklama,
                        "ornek_file_id": ek_dosya.belge.file_id,
                        "ornek_file_ad": ek_dosya.belge.adi,
                        "proje_icerik_dosyasi_mi": ek_dosya.proje_icerik_dosyasi_mi,
                        "belgenin_ciktisi_alinacak_mi": ek_dosya.belgenin_ciktisi_alinacak_mi,
                        "zorunlu_mu": ek_dosya.zorunlu_mu
                    })
                    break
        for proje_belge in proje.proje_belgeleri:
            if proje_belge.proje_turu_ek_dosya_id is None:
                proje_diger_dosyalar.append({
                    "adi": proje_belge.baslik,
                    "aciklama": proje_belge.aciklama,
                    "file_id": proje_belge.belge_id
                })
                break

        # todo: gereklimi ? ustteki querye dahil edilip alinabilir
        proje_turu_sablonlari = DB.session.query(Sablon).filter(Sablon.id.in_([
            proje.proje_proje_turu.oneri_sablon_id,
            proje.proje_proje_turu.hakem_degerlendirme_sablon_id,
            proje.proje_proje_turu.hakem_ara_rapor_sablon_id,
            proje.proje_proje_turu.hakem_sonuc_rapor_sablon_id,
            proje.proje_proje_turu.ara_rapor_sablon_id,
            proje.proje_proje_turu.sonuc_raporu_sablon_id,
            proje.proje_proje_turu.sozlesme_sablon_id,
        ])).all()
        return render_template("dashboard/proje_sablon_ekdosyalar.html",
                               proje_id=proje_id,
                               proje=proje,
                               next_states_info=next_states_info,
                               actions_info=actions_info,
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               ciktilar=ciktilar,
                               proje_ek_dosyalar=proje_ek_dosyalar,
                               proje_diger_dosyalar=proje_diger_dosyalar,
                               proje_turu_sablonlari=proje_turu_sablonlari,
                               proje_turu=proje_turu,
                               atanmis_hakem=atanmis_hakem)
