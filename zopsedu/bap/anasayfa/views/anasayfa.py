"""Bap anasayfa modulu"""
from datetime import datetime

from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from sqlalchemy.orm import lazyload

from zopsedu.bap.anasayfa.views.common import get_anasayfa_formlar, get_bap_duyurular, get_satinalma_duyurular
from zopsedu.lib.db import DB
from zopsedu.models import Icerik, Person, User, Birim
from zopsedu.icerik.model import IcerikBirimTipi, IcerikTipi
from zopsedu.auth.lib import auth
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class BapAnasayfaView(FlaskView):
    """Bap anasyafa view classi"""

    @staticmethod
    @route('/anasayfa', methods=['GET'])
    def bap_anasayfa():
        # tipi duyuru birimi bap olan iceriklerden ana sayfa gorunurlugu olanlari getirir.
        anasayfa_formlar = get_anasayfa_formlar()
        satinalma_duyurular = get_satinalma_duyurular()
        bap_duyurular = get_bap_duyurular()

        return render_template("anasayfa.html",
                               bap_duyurular=bap_duyurular,
                               satinalma_duyurular=satinalma_duyurular,
                               anasayfa_formlar=anasayfa_formlar)

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.akademisyen_ozgecmis",
                                  "title": _("Akademisyen Özgeçmiş"), "order": 1})
    @route('/akademisyen-ozgecmis', methods=['GET'])
    def akademisyen_ozgecmis():
        ogretim_elemani_query = DB.session.query(
            OgretimElemani,
            Person.birincil_eposta.label("birincil_eposta"),
            Person.ad.label("ou_ad"),
            Person.soyad.label("ou_soyad"),
            Birim.uzun_ad.label("birim"),
            User.avatar.label("avatar"),
            HitapUnvan.ad.label("ou_hitap_unvan_ad"),
        ).join(
            Personel, OgretimElemani.personel_id == Personel.id
        ).join(
            Birim, Birim.id == Personel.birim
        ).join(
            Person, Personel.person_id == Person.id
        ).join(
            User, Person.user_id == User.id
        ).join(
            HitapUnvan, HitapUnvan.id == OgretimElemani.unvan
        ).options(
            lazyload(OgretimElemani.hitap_unvan),
            lazyload(OgretimElemani.personel),
            lazyload(OgretimElemani.person),
        ).filter(
            OgretimElemani.yok_ozgecmis_bilgileri_var_mi == True
        ).all()
        data = []
        for oe in ogretim_elemani_query:
            data.append({
                "ou_hitap_unvan_ad": oe.ou_hitap_unvan_ad,
                "ou_ad": oe.ou_ad,
                "ou_soyad": oe.ou_soyad,
                "birim": oe.birim,
                "email_prefix": oe.birincil_eposta.split("@")[0],
            })
        return render_template("akademisyen_ozgecmis_listele.html",
                               akademisyen_verileri=data)

    @staticmethod
    @route('/duyurular', methods=['GET'], endpoint="bap_duyuru_listele")
    def bap_duyuru_listele():
        # bap duyurularindan aktif olanlari getirir
        bap_duyurular = DB.session.query(Icerik).join(
            User, User.id == Icerik.ekleyen_id).join(
            Person, Person.user_id == User.id).add_columns(Icerik.id,
                                                           Icerik.baslik,
                                                           Icerik.baslangic_tarihi,
                                                           Icerik.bitis_tarihi,
                                                           Person.ad.label("ekleyen_ad"),
                                                           Person.soyad.label("ekleyen_soyad")
                                                           ).filter(
            Icerik.tipi == IcerikTipi.duyuru,
            Icerik.birim_tipi == IcerikBirimTipi.bap,
            Icerik.aktif_mi == True,
            Icerik.baslangic_tarihi < datetime.now(),
            Icerik.bitis_tarihi > datetime.now()).all()
        return render_template("duyuru_listele.html",
                               duyurular=bap_duyurular,
                               panel_header=_("BAP Duyurular"),
                               duyuru_detay_endpoint="anasayfa.bap_duyuru_detay")

    @staticmethod
    @route('/duyuru/<int:duyuru_id>', methods=['GET'], endpoint="bap_duyuru_detay")
    def bap_duyuru_detay(duyuru_id):
        # bap duyurularindan aktif olanlari getirir
        bap_duyuru = DB.session.query(Icerik).join(
            User, User.id == Icerik.ekleyen_id).join(
            Person, Person.user_id == User.id).add_columns(Icerik.id,
                                                           Icerik.icerik,
                                                           Icerik.baslik,
                                                           Icerik.baslangic_tarihi,
                                                           Icerik.bitis_tarihi,
                                                           Person.ad.label("ekleyen_ad"),
                                                           Person.soyad.label("ekleyen_soyad")
                                                           ).filter(
            Icerik.tipi == IcerikTipi.duyuru,
            Icerik.birim_tipi == IcerikBirimTipi.bap,
            Icerik.aktif_mi == True,
            Icerik.id == duyuru_id,
            Icerik.baslangic_tarihi < datetime.now(),
            Icerik.bitis_tarihi > datetime.now()).one()
        return render_template("duyuru_detay.html", bap_duyuru=bap_duyuru)

    @staticmethod
    @route('/duyurular/satinalma', methods=['GET'])
    def bap_satinalma_listele():
        # bap satinalma duyurularindan aktif olanlari getirir
        satinalma_duyurulari = DB.session.query(Icerik).join(
            User, User.id == Icerik.ekleyen_id).join(
            Person, Person.user_id == User.id).add_columns(Icerik.id,
                                                           Icerik.baslik,
                                                           Icerik.baslangic_tarihi,
                                                           Icerik.bitis_tarihi,
                                                           Person.ad.label("ekleyen_ad"),
                                                           Person.soyad.label("ekleyen_soyad")
                                                           ).filter(
            Icerik.tipi == IcerikTipi.satinalma,
            Icerik.birim_tipi == IcerikBirimTipi.bap,
            Icerik.aktif_mi == True,
            Icerik.baslangic_tarihi < datetime.now(),
            Icerik.bitis_tarihi > datetime.now()).all()
        return render_template("duyuru_listele.html",
                               panel_header=_("Satınalma Duyuruları"),
                               duyurular=satinalma_duyurulari,
                               duyuru_detay_endpoint="anasayfa.BapAnasayfaView:satinalma_duyuru_detay")

    @staticmethod
    @route('/duyuru/satinalma/<int:duyuru_id>', methods=['GET'])
    def satinalma_duyuru_detay(duyuru_id):
        # bap satinalma duyurularindan aktif olanlari getirir
        bap_duyuru = DB.session.query(Icerik).join(
            User, User.id == Icerik.ekleyen_id).join(
            Person, Person.user_id == User.id).add_columns(Icerik.id,
                                                           Icerik.icerik,
                                                           Icerik.baslik,
                                                           Icerik.baslangic_tarihi,
                                                           Icerik.bitis_tarihi,
                                                           Person.ad.label("ekleyen_ad"),
                                                           Person.soyad.label("ekleyen_soyad")
                                                           ).filter(
            Icerik.tipi == IcerikTipi.satinalma,
            Icerik.birim_tipi == IcerikBirimTipi.bap,
            Icerik.aktif_mi == True,
            Icerik.id == duyuru_id,
            Icerik.baslangic_tarihi < datetime.now(),
            Icerik.bitis_tarihi > datetime.now()).one()
        return render_template("satinalma_duyuru_detay.html",
                               bap_duyuru=bap_duyuru)

    ################## BUNLAR YAPIM AŞAMASINDA :( #####################

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.bap_takvim",
                                  "title": _("BAP Takvim"), "order": 10})
    @route('/takvim', methods=['GET'])
    def bap_takvim():
        anasayfa_formlar = get_anasayfa_formlar()
        satinalma_duyurular = get_satinalma_duyurular()
        bap_duyurular = get_bap_duyurular()

        return render_template("anasayfa_yapim_asamasinda.html",
                               anasayfa_formlar=anasayfa_formlar,
                               satinalma_duyurular=satinalma_duyurular,
                               bap_duyurular=bap_duyurular)


