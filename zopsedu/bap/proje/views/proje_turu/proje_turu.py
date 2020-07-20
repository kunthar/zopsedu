"""Proje Türü View Metotları"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-nested-blocks
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from flask import render_template, redirect, url_for
from flask_classful import FlaskView, route
from flask_babel import lazy_gettext as _
from flask_login import login_required

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.lib.db import DB
from zopsedu.models import ProjeTuru, EkDosya, ButceKalemi, Taslak
from zopsedu.models.taslak import TaslakTipleri
from zopsedu.bap.proje.forms.proje_turu.proje_turu import ProjeTuruFormu
from zopsedu.auth.lib import auth, Permission

PROJE_TURU_GELIR_KODLARI = [
    "3.6",
    "5.4.1",
    "6.5",
    "3.3",
    "3.5",
    "3.5.9",
    "3.2",
    "3.7",
    "6.1",
    "3.8",
    "6.3",
    "1",
    "3.5.9.3",
    # "630.99",
]


class ProjeTuruView(FlaskView):
    """Proje Türü View"""

    excluded_methods = ["init_proje_turu_gelir_kodlari_data"]

    @staticmethod
    def init_proje_turu_gelir_kodlari_data(proje_turu_formu, butce_kalemleri=None):
        """
        proje turu icin secilmis butce kalemlerinin verisini proje turu formu butce_kalemliri
        alanina ekler
        """
        if butce_kalemleri:
            for butce_kalemi in butce_kalemleri:
                for butce_kalem_form in proje_turu_formu.butce_kalemleri:
                    if butce_kalem_form.gider_siniflandirma_id.data == butce_kalemi.gider_siniflandirma_id:
                        butce_kalem_form.secili_mi.data = True
                        butce_kalem_form.butce_alt_limiti.data = butce_kalemi.butce_alt_limiti
                        butce_kalem_form.butce_ust_limiti.data = butce_kalemi.butce_ust_limiti

        return proje_turu_formu

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/', methods=["GET"], endpoint='proje_turu')
    def get_proje_turu_view(self):
        """
        Proje türü view ini almayı saglarl
        Returns:

        """
        proje_turu_formu = ProjeTuruFormu()
        return render_template("proje_turu/proje_turu.html",
                               proje_turu_formu=proje_turu_formu,
                               basvuru_yapilmis_mi=False,
                               guncel_mi=True)

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/<int:proje_turu_id>', methods=["GET"], endpoint='proje_turu_with_id')
    def get_proje_turu_view_with_id(self, proje_turu_id):
        """
        Proje türünü id si ile birlikte almayı sağlar.
        Args:
            proje_turu_id: proje türünün id si

        Returns:

        """
        try:
            proje_turu = DB.session.query(ProjeTuru).options(
                joinedload(ProjeTuru.butce),
                joinedload(ProjeTuru.cikti),
                joinedload(ProjeTuru.personel_ayarlari),
                joinedload(ProjeTuru.ek_dosyalar).joinedload(EkDosya.belge),
                joinedload(ProjeTuru.butce_kalemleri).joinedload(
                    ButceKalemi.gider_siniflandirma_kalemi)
            ).filter_by(id=proje_turu_id).one()
        except NoResultFound:
            return redirect(url_for('.proje_turu'))

        proje = DB.session.query(Proje.proje_turu).filter(Proje.proje_turu == proje_turu_id).all()

        butce_dict = proje_turu.butce.to_dict()
        personel_ayarlari_dict = proje_turu.personel_ayarlari.to_dict()
        proje_turu_dict = proje_turu.to_dict()

        if butce_dict:
            butce_dict.pop("id")
            butce_dict.pop("proje_turu_id")

        if personel_ayarlari_dict:
            personel_ayarlari_dict.pop("id")
            personel_ayarlari_dict.pop("proje_turu_id")

        ek_dosyalar = []
        for ek_dosya in proje_turu.ek_dosyalar:
            ek_dosyalar.append({
                "ek_dosya_id": ek_dosya.id,
                "zorunlu_mu": ek_dosya.zorunlu_mu,
                "proje_icerik_dosyasi_mi": ek_dosya.proje_icerik_dosyasi_mi,
                "belgenin_ciktisi_alinacak_mi": ek_dosya.belgenin_ciktisi_alinacak_mi,
                "belge": {
                    "adi": ek_dosya.belge.adi,
                    "aciklama": ek_dosya.belge.aciklama,
                    "turler": ek_dosya.belge.turler,
                    "file_id": ek_dosya.belge.file_id
                }
            })
        ciktilar = []
        for cikti in proje_turu.cikti:
            ciktilar.append({
                "cikti_id": cikti.id,
                "sablon_id": cikti.sablon_id,
                "adi": cikti.adi,
                "gorunurluk": cikti.gorunurluk,
                "belge_ciktisi_alinacak_mi": cikti.belge_ciktisi_alinacak_mi
            })

        proje_turu_formu = ProjeTuruFormu(**proje_turu_dict,
                                          **proje_turu.genel_uyari_mesajlari,
                                          butce_ayarlari=butce_dict,
                                          sablon_ayarlari=proje_turu_dict,
                                          personel_ayarlari=personel_ayarlari_dict,
                                          ek_dosyalar=ek_dosyalar,
                                          ciktilar=ciktilar)
        proje_turu_formu = self.init_proje_turu_gelir_kodlari_data(proje_turu_formu,
                                                                   proje_turu.butce_kalemleri)

        return render_template("proje_turu/proje_turu.html",
                               proje_turu_formu=proje_turu_formu,
                               proje_turu_id=proje_turu.id,
                               guncel_mi=proje_turu.guncel_mi,
                               basvuru_yapilmis_mi=True if proje else False)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turlerini_listeme"]),
                   menu_registry={'path': '.yonetim.bap.proje_turu', 'title': _("Proje Türleri"),
                                  "order": 0})
    @route('/liste', methods=['GET'])
    def proje_turu_listele():
        """Proje Turleri Listesi"""
        uyarilar = [
            "Proje türünü taslak olarak kaydedip daha sonra işlem yapmaya devam edebilirsiniz",
            "Başvuru yapılmış bir proje türünü güncelleyemezsiniz.",
            "Başvuru yapılmış bir projeyi güncellemek isterseniz versiyonlama özelliğini kullanabilirsiniz",
            "Bir proje türünü versiyonlarsanız eski versiyona artık başvuru yapılamayacaktır. Başvurular yeni versiyona yapılabilir.",
            "Eski versiyona yapılmış proje başvuruları o versiyondaki ayarlarla devam eder.",
            "Basvuru aktif mi seçeneğini işaretlemezseniz proje türü başvuruya açık olmaz",
        ]
        proje_turleri = DB.session.query(ProjeTuru).order_by(desc(ProjeTuru.created_at)).all()
        proje_turu_taslaklari = DB.session.query(Taslak).filter(Taslak.taslak_tipi == TaslakTipleri.bap_proje_turu).all()
        return render_template('/proje_turu/listeleme.html',
                               proje_turleri=proje_turleri,
                               taslak_proje_turleri=proje_turu_taslaklari,
                               uyarilar=uyarilar)
# pylint: enable=too-many-locals
# pylint: enable=too-many-branches
# pylint: enable=too-many-statements
# pylint: enable=too-many-return-statements
# pylint: enable=too-many-nested-blocks
