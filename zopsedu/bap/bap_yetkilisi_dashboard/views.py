"""Proje Yurutucu Dashboard view classları"""
import datetime
from decimal import Decimal

from flask import render_template
from flask_allows import Or
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required
from sqlalchemy import or_, func

from zopsedu.auth.lib import auth, Role
from zopsedu.bap.models.gelir_kasasi import GelirKasasi
from zopsedu.bap.models.helpers import ProjeDegerlendirmeSonuc, ProjeBasvuruDurumu
from zopsedu.lib.db import DB
from zopsedu.models import Proje, Personel
from zopsedu.models.helpers import AppStates
from zopsedu.personel.models.hakem import Hakem


class BapYetkilisiDashboardView(FlaskView):
    """
    Proje Yurutucu Dashboard view methodlarini icerir
    """

    @staticmethod
    @login_required
    @route("/bap-yetkilisi-kontrol-paneli", methods=["GET"])
    @auth.requires(Or(Role("BAP Yetkilisi"), Role("BAP Admin")),
                   menu_registry={'path': '.bap_yetkilisi_dashboard',
                                  'title': _("Kontrol Paneli")})
    def index():
        """Bap yetkilisi dashboard genel bilgiler"""

        personel_sayi = DB.session.query(Personel.id).filter(Personel.personel_turu == "akademik").count()
        hakemler = DB.session.query(Hakem).all()
        projeler = DB.session.query(Proje).filter(
            or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).all()
        devam_etmeyen_proje_sayi = 0
        toplam_butce = DB.session.query(func.sum(GelirKasasi.toplam_para).label("toplam_butce"),
                                        func.sum(GelirKasasi.harcanan_para).label("harcanan_para"),
                                        func.sum(GelirKasasi.rezerv_para).label("rezerv_para"),
                                        GelirKasasi.adi.label("kasa_adi"),
                                        GelirKasasi.toplam_para.label("toplam_para")).filter(
            GelirKasasi.mali_yil == datetime.date.today().year).group_by(GelirKasasi.toplam_para, GelirKasasi.adi,
                                                                         GelirKasasi.harcanan_para,
                                                                         GelirKasasi.rezerv_para).all()
        butce_toplami = 0
        butce_kasalari = {}
        harcanan_para = 0
        rezerv_para = 0
        for butce in toplam_butce:
            butce_toplami += butce.toplam_butce.quantize(Decimal(".01"))
            harcanan_para += butce.harcanan_para.quantize(Decimal(".01"))
            rezerv_para += butce.rezerv_para.quantize(Decimal(".01"))

        butce_harcamalari = {"Toplam Bütçe": butce_toplami,
                             "Harcanan": harcanan_para,
                             "Rezerv": rezerv_para}

        proje_butce = 0
        proje_degerlendirmeleri = {"Olumlu": 0,
                                   "Olumsuz": 0,
                                   "Revizyon gerekli": 0,
                                   "Değerlendirilmedi": 0,
                                   }
        hakem_sayi = {"Kurum içi": 0, "Kurum dışı": 0}
        for hakem in hakemler:
            if hakem.kurum_ici:
                hakem_sayi["Kurum içi"] += 1
            else:
                hakem_sayi["Kurum dışı"] += 1
        for proje in projeler:
            if proje.proje_durumu.current_app_state == AppStates.son:
                devam_etmeyen_proje_sayi += 1

            for rapor in proje.proje_raporlari:
                if rapor.rapor_degerlendirme_durumu:
                    if rapor.rapor_degerlendirme_durumu == ProjeDegerlendirmeSonuc.olumlu:
                        proje_degerlendirmeleri["Olumlu"] += 1
                    elif rapor.rapor_degerlendirme_durumu == ProjeDegerlendirmeSonuc.olumsuz:
                        proje_degerlendirmeleri["Olumsuz"] += 1
                    elif rapor.rapor_degerlendirme_durumu == ProjeDegerlendirmeSonuc.revizyon:
                        proje_degerlendirmeleri["Revizyon gerekli"] += 1
                    elif rapor.rapor_degerlendirme_durumu == ProjeDegerlendirmeSonuc.degerlendirilmedi:
                        proje_degerlendirmeleri["Değerlendirilmedi"] += 1

            proje_butce += proje.kabul_edilen_butce if proje.kabul_edilen_butce else 0

        proje_sayi = {'Devam Eden': len(projeler) - devam_etmeyen_proje_sayi,
                      'Devam Etmeyen': devam_etmeyen_proje_sayi}

        for butce in toplam_butce:
            toplam_para = butce.toplam_para.quantize(Decimal(".01"))
            butce_kasalari.update({butce.kasa_adi: toplam_para})

        return render_template('bap_yetkilisi_dashboard.html',
                               hakem_sayi=hakem_sayi,
                               butce_toplami=butce_toplami,
                               proje_sayi=proje_sayi,
                               proje_degerlendirmeleri=proje_degerlendirmeleri,
                               proje_butce=proje_butce,
                               personel_sayi=personel_sayi,
                               butce_kasalari=butce_kasalari,
                               butce_harcamalari=butce_harcamalari)

    @staticmethod
    @login_required
    @route("/rektor-kokpiti", methods=["GET"])
    @auth.requires(Role("Rektör"))
    def rektor_kokpiti():

        return render_template('rektor_kokpiti.html')
