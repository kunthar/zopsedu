"""Bap ile ilgili querylerin bulundugu module"""
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import joinedload, aliased, lazyload

from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif, FirmaTeklifKalemi
from zopsedu.bap.models.muhasebe_fisi import MuhasebeFisi
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_turu import ProjeTuru
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.models.toplanti import BapToplanti
from zopsedu.common.app.sablon.forms import FirmaSelectForm
from zopsedu.lib.db import DB
from zopsedu.lib.sessions import SessionHandler
from zopsedu.models import Proje, Birim, Person
from zopsedu.lib.query_helpers import BaseQueryHelper
from zopsedu.models import TalepKalemleri, ProjeSatinAlmaTalebi
from zopsedu.models.helpers import BapIdariUnvan
from zopsedu.personel.models.hakem import Hakem
from zopsedu.personel.models.idari_personel import BapIdariPersonel
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class BapQueryHelpers(BaseQueryHelper):
    module_name = "BAP"
    sub_module_name = "BAP"

    @staticmethod
    def get_proje_with_id(proje_id):
        proje = DB.session.query(Proje).filter_by(
            id=proje_id).one()
        return proje

    @staticmethod
    def get_satinalma_with_related_field(satinalma_id):
        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                TalepKalemleri.proje_kalemi)).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()
        return satinalma

    @staticmethod
    def get_satinalma_with_related_field_with_mkk(satinalma_id):
        """
        Satinalma talebi ve ilgili related tablolarini getirir.
        Mkk uyelerini getirir cogu yerde gereksiz veridir kullanirken dikkat edilmelidir.
        """
        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.proje).joinedload(Proje.proje_yurutucu),
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                TalepKalemleri.proje_kalemi),
            joinedload(ProjeSatinAlmaTalebi.mkk_baskan),
            joinedload(ProjeSatinAlmaTalebi.mkk_uye1),
            joinedload(ProjeSatinAlmaTalebi.mkk_uye2),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_baskan),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_uye1),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_uye2),
        ).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()
        return satinalma

    @staticmethod
    def get_firma_teklif_with_related_field(teklif_id):
        # todo: guvenlik !!!
        firma_teklif = DB.session.query(FirmaSatinalmaTeklif).filter(
            FirmaSatinalmaTeklif.id == teklif_id).options(
            joinedload(FirmaSatinalmaTeklif.firma).joinedload(BapFirma.vergi_dairesi),
            joinedload(FirmaSatinalmaTeklif.teklif_kalemleri).joinedload(
                FirmaTeklifKalemi.satinalma_talep_kalemi).joinedload(
                TalepKalemleri.proje_kalemi).lazyload("*"),
            joinedload(FirmaSatinalmaTeklif.satinalma).joinedload(
                ProjeSatinAlmaTalebi.proje).lazyload("*")
        ).first()
        # jinja2 uzerinde matematik islemi yapmak istenmediginden veri sablonda
        # kullanilacak hale burda getirildi
        firma_teklif_data = {
            "proje_no": firma_teklif.satinalma.proje.proje_no,
            "talep_numarasi": firma_teklif.satinalma.talep_numarasi,
            "firma": firma_teklif.firma,
            "teklif_aciklama": firma_teklif.aciklama,
            "teklif_kalemleri": [],
            "toplam_kdv_tutari": Decimal("0.00"),
            "kdvsiz_toplam": Decimal("0.00"),
            "firma_yetkilisi_ad": firma_teklif.firma.yetkili_adi,
            "firma_yetkilisi_soyad": firma_teklif.firma.yetkili_soyadi
        }

        for firm_teklif_kalemi in firma_teklif.teklif_kalemleri:
            firma_teklif_data["teklif_kalemleri"].append({
                "kalem_adi": firm_teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.ad,
                "talep_miktari": firm_teklif_kalemi.satinalma_talep_kalemi.talep_miktari,
                "birimi": firm_teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.birim.value,
                "marka_model": firm_teklif_kalemi.marka_model,
                "kdv_haric_birim_fiyat": firm_teklif_kalemi.teklif / firm_teklif_kalemi.satinalma_talep_kalemi.talep_miktari,
                "kdv_orani": firm_teklif_kalemi.kdv_orani,
                "kdv_haric_tutar": firm_teklif_kalemi.teklif
            })
            firma_teklif_data[
                "toplam_kdv_tutari"] += firm_teklif_kalemi.kdv_orani * firm_teklif_kalemi.teklif / Decimal(
                "100.00")

            firma_teklif_data["kdvsiz_toplam"] += firm_teklif_kalemi.teklif

        firma_teklif_data["toplam_kdv_tutari"] = firma_teklif_data["toplam_kdv_tutari"].quantize(
            Decimal(".01"))
        firma_teklif_data["kdvsiz_toplam"] = firma_teklif_data["kdvsiz_toplam"].quantize(
            Decimal(".01"))
        return firma_teklif_data

    @staticmethod
    def get_satinalma_for_yaklasik_maaliyet_icmal_sablonu(satinalma_id):
        """
        Satinalma yaklasik maaliyet icmal tablosu sablonu icin yazilmistir
        """
        # todo: gerceklestirme gorevlisi ??
        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.proje).joinedload(Proje.proje_yurutucu),
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                TalepKalemleri.proje_kalemi)).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()

        data = {
            "talep_kalemleri": [],
            "toplam_kdv_haric": Decimal("0.00"),
            "yurutucu_ad_soyad": "{} {}".format(satinalma.proje.proje_yurutucu.person.ad,
                                                satinalma.proje.proje_yurutucu.person.soyad),
            "proje_no": satinalma.proje.proje_no,
            "proje_kalemi_adi": ""

        }

        for talep_kalemi in satinalma.talep_kalemleri:
            tutar = (
                            talep_kalemi.proje_kalemi.toplam_butce / talep_kalemi.proje_kalemi.toplam_miktar) * talep_kalemi.talep_miktari
            talep_kalemi_data = {
                "ad": talep_kalemi.proje_kalemi.ad,
                "birim": talep_kalemi.proje_kalemi.birim.value,
                "miktar": talep_kalemi.talep_miktari,
                "tutar": tutar,
            }
            data["toplam_kdv_haric"] += tutar
            data["talep_kalemleri"].append(talep_kalemi_data)
            data[
                "proje_kalemi_adi"] = talep_kalemi.proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama
        return data

    @staticmethod
    def get_satinalma_for_piyasa_fiyat_arastirma_tutanagi(satinalma_id):
        """
        Satinalma piyasa fiyat arastirma tutanak sablonu icin eklenmistir
        """
        # todo: gerceklestirme gorevlisi ??
        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.proje).joinedload(Proje.proje_yurutucu),
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).options(joinedload(
                TalepKalemleri.proje_kalemi))).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()

        data = {
            "talep_kalemleri": [],
            "toplam_kdv_haric": Decimal("0.00"),
            "yurutucu_ad_soyad": "{} {}".format(satinalma.proje.proje_yurutucu.person.ad,
                                                satinalma.proje.proje_yurutucu.person.soyad),
            "proje_no": satinalma.proje.proje_no,
            "proje_basligi": satinalma.proje.proje_basligi,
            "proje_kalemi_adi": ""

        }

        for talep_kalemi in satinalma.talep_kalemleri:
            talep_kalemi_data = {
                "ad": talep_kalemi.proje_kalemi.ad,
                "birim": talep_kalemi.proje_kalemi.birim.value,
                "miktar": talep_kalemi.talep_miktari
            }
            data["talep_kalemleri"].append(talep_kalemi_data)
            data[
                "proje_kalemi_adi"] = talep_kalemi.proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama
        return data

    @staticmethod
    def get_satinalma_for_malzeme_dilekcesi(satinalma_id):
        """
        Satinalma malzeme listesi sablonu icin eklenmistir
        """

        # todo: toplam butce ve kalan ??
        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.proje).joinedload(Proje.proje_yurutucu),
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                TalepKalemleri.proje_kalemi),
            joinedload(ProjeSatinAlmaTalebi.mkk_baskan),
            joinedload(ProjeSatinAlmaTalebi.mkk_uye1),
            joinedload(ProjeSatinAlmaTalebi.mkk_uye2),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_baskan),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_uye1),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_uye2),
        ).join(TalepKalemleri, TalepKalemleri.satinalma_id == ProjeSatinAlmaTalebi.id). \
            join(Proje, ProjeSatinAlmaTalebi.proje_id == Proje.id).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()

        data = {
            "proje": satinalma.proje,
            "talep_kalemleri": satinalma.talep_kalemleri,
            "mkk_baskan": satinalma.mkk_baskan,
            "mkk_uye1": satinalma.mkk_uye1,
            "mkk_uye2": satinalma.mkk_uye2,
            "mkk_yedek_baskan": satinalma.mkk_yedek_baskan,
            "mkk_yedek_uye1": satinalma.mkk_yedek_uye1,
            "mkk_yedek_uye2": satinalma.mkk_yedek_uye2

        }
        return data

    @staticmethod
    def get_satinalma_for_olur_formu(satinalma_id):
        """
        Satinalma malzeme listesi sablonu icin eklenmistir
        """
        # todo: bap kordinatörü ??
        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.proje).joinedload(Proje.proje_yurutucu),
            joinedload(ProjeSatinAlmaTalebi.mkk_baskan),
            joinedload(ProjeSatinAlmaTalebi.mkk_uye1),
            joinedload(ProjeSatinAlmaTalebi.mkk_uye2),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_baskan),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_uye1),
            joinedload(ProjeSatinAlmaTalebi.mkk_yedek_uye2),
        ).join(TalepKalemleri, TalepKalemleri.satinalma_id == ProjeSatinAlmaTalebi.id). \
            filter(ProjeSatinAlmaTalebi.id == satinalma_id).one()

        data = {
            "proje": satinalma.proje,
            "mkk_baskan": satinalma.mkk_baskan,
            "mkk_uye1": satinalma.mkk_uye1,
            "mkk_uye2": satinalma.mkk_uye2,
            "mkk_yedek_baskan": satinalma.mkk_yedek_baskan,
            "mkk_yedek_uye1": satinalma.mkk_yedek_uye1,
            "mkk_yedek_uye2": satinalma.mkk_yedek_uye2
        }
        return data

    # todo: proje türü tertibi ödenek
    @staticmethod
    def get_satinalma_for_onay_formu(satinalma_id):
        """

        Satinalma onay sablonu icin eklenmistir
        """

        odenek = DB.session.query(
            func.sum((ProjeKalemi.toplam_butce - (
                    ProjeKalemi.rezerv_butce + ProjeKalemi.kullanilan_butce))).label(
                "kullanilabilir_butce"),
            (func.sum((
                              ProjeKalemi.toplam_butce / ProjeKalemi.toplam_miktar) * TalepKalemleri.talep_miktari)).label(
                "yaklasik_maliyet"), TalepKalemleri.satinalma_id.label("satinalma_id")). \
            join(TalepKalemleri,
                 TalepKalemleri.proje_kalemi_id == ProjeKalemi.id). \
            filter(TalepKalemleri.satinalma_id == satinalma_id). \
            group_by(TalepKalemleri.satinalma_id).subquery('odenek')

        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.proje).joinedload(Proje.proje_yurutucu)). \
            join(TalepKalemleri, TalepKalemleri.satinalma_id == ProjeSatinAlmaTalebi.id). \
            join(odenek, odenek.c.satinalma_id == ProjeSatinAlmaTalebi.id). \
            filter(ProjeSatinAlmaTalebi.id == satinalma_id).add_columns(
            odenek.c.yaklasik_maliyet.label("yaklasik_maliyet"),
            odenek.c.kullanilabilir_butce.label("kullanilabilir_butce")
        ).one()

        data = {
            "isin_niteligi": "{} kalem malzeme alımı".format(
                len(satinalma.ProjeSatinAlmaTalebi.talep_kalemleri)),
            "yaklasik_maliyet": satinalma.yaklasik_maliyet.quantize((Decimal('.01'))) * 90 / 100,
            "kalan_odenek": satinalma.kullanilabilir_butce.quantize(
                (Decimal('.01'))) - satinalma.yaklasik_maliyet.quantize(
                (Decimal('.01'))) * 90 / 100,
            "ihale_usulu": "4734 Sayılı K.İ.K 3/f bendine istinaden 2003/6554 Sayılı Bak.Kur.Kararının 6.mad. 21/d usulüne göre",
            "satinalma": satinalma.ProjeSatinAlmaTalebi,
            "proje": satinalma.ProjeSatinAlmaTalebi.proje
        }

        return data

    @staticmethod
    def get_satinalma_for_komisyon_tutanagi(satinalma_id):
        """
            Satinalma komisyon tutanağı için eklenmiştir
        """

        teklifler = DB.session.query(TalepKalemleri, BapFirma.adi.label("firma_adi"),
                                     func.count(BapFirma.adi).label("firma_sayisi"),
                                     ProjeKalemi.ad.label("malzeme_adi"),
                                     FirmaTeklifKalemi.teklif.label("teklif")). \
            join(SiparisTakip, SiparisTakip.satinalma_talep_kalemleri_id == TalepKalemleri.id). \
            join(ProjeKalemi, ProjeKalemi.id == TalepKalemleri.proje_kalemi_id). \
            join(FirmaTeklifKalemi, FirmaTeklifKalemi.id == SiparisTakip.kazanan_firma_teklif_id). \
            join(FirmaSatinalmaTeklif, FirmaSatinalmaTeklif.id == FirmaTeklifKalemi.teklif_id). \
            join(BapFirma, BapFirma.id == FirmaSatinalmaTeklif.firma_id). \
            group_by(TalepKalemleri.id, BapFirma.id, FirmaTeklifKalemi.id, ProjeKalemi.id).subquery(
            "teklifler")

        satinalma = DB.session.query(ProjeSatinAlmaTalebi, teklifler). \
            join(teklifler, teklifler.c.satinalma_id == ProjeSatinAlmaTalebi.id).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).all()

        data = {'satinalma': satinalma[0].ProjeSatinAlmaTalebi,
                'proje': satinalma[0].ProjeSatinAlmaTalebi.proje,
                "tutanak_aciklama": "{} kalem malzeme alımı".format(
                    len(satinalma[0].ProjeSatinAlmaTalebi.talep_kalemleri)),
                "teklifler": satinalma,
                "firma_sayisi": satinalma[0].firma_sayisi}

        return data

    @staticmethod
    def get_satinalma_for_siparis_formu(satinalma_id):
        """

            Satinalma siparis formu için eklenmiştir.
        """

        proje = DB.session.query(Proje, ProjeSatinAlmaTalebi.talep_numarasi).join(
            ProjeSatinAlmaTalebi, ProjeSatinAlmaTalebi.proje_id == Proje.id).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()

        form = FirmaSelectForm(satinalma_id)

        uni_adi = \
            DB.session.query(Birim.ad).filter(Birim.id == SessionHandler.universite_id()).first()[0]

        universite_adi = uni_adi if uni_adi else 'ilgili üniversite'

        data = {
            'form': form,
            'satinalma_id': satinalma_id,
            'proje': proje[0],
            'talep_numarasi': proje[1],
            'universite_adi': universite_adi
        }

        return data

    @staticmethod
    def get_muhasebe_fisi_bilgileri(muhasebe_fis_id):
        """
            Ödeme emri sablonu icin kullanılacak
        """

        def get_fis_maddesi_data(fis_maddesi):
            fis_maddesi_data = {
                "hesap_kodu": fis_maddesi.hesap_kodu,
                "kurumsal_kod": kod_parser(fis_maddesi.kurumsal_kod),
                "fonksiyonel_kod": kod_parser(fis_maddesi.fonksiyonel_kod),
                "ekonomik_hesap_kodu": kod_parser(fis_maddesi.ekonomik_hesap_kodu),
                "finans_kodu": fis_maddesi.finans_kodu,
                "borc": decimal_parser(fis_maddesi.borc),
                "alacak": decimal_parser(fis_maddesi.alacak),
                "hesap_ayrinti_adi": fis_maddesi.hesap_ayrinti_adi
            }

            return fis_maddesi_data

        def kod_parser(kod):
            """
            150 veya 150.01.00.00 gibi gelen kodlari "." ya gore parse eder
            :param kod: strint --> 150.00.01.00
            :return: dict --> {
                1: "150",
                2: "00",
                3: "01",
                4: "00"
            }
            """
            kod_data = {
                1: "",
                2: "",
                3: "",
                4: ""
            }
            for index, data in enumerate(kod.split("."), start=1):
                kod_data[index] = data

            return kod_data

        def decimal_parser(decimal_value):
            """
            123123.22 seklinde gelen decimal degeri virgulden onceki ve sonraki kisim olarak ayirir
            :param decimal_value: decimal
            :return: dict --> {
                             "tr": "123123",
                             "kr": "22"
                            }
            """
            string_value_list = str(decimal_value).split(".")
            return {
                "tl": string_value_list[0],
                "kr": string_value_list[1],
            }

        muhasebe_fisi = DB.session.query(MuhasebeFisi).options(
            joinedload(MuhasebeFisi.satinalma).joinedload(ProjeSatinAlmaTalebi.proje).joinedload(
                Proje.proje_yurutucu),
            joinedload(MuhasebeFisi.satinalma).joinedload(ProjeSatinAlmaTalebi.proje).joinedload(
                Proje.fakulte),
            joinedload(MuhasebeFisi.satinalma).joinedload(ProjeSatinAlmaTalebi.proje).joinedload(
                Proje.bolum),
        ).filter(
            MuhasebeFisi.id == muhasebe_fis_id).first()
        muhasebe_fisi_data = {
            "muhasebe_birim_adi": muhasebe_fisi.muhasebe_birim_adi,
            "muhasebe_birim_kodu": muhasebe_fisi.muhasebe_birim_kodu,
            "kurum_adi": muhasebe_fisi.kurum_adi,
            "kurum_kod": kod_parser(muhasebe_fisi.kurum_kodu),
            "birim_adi": muhasebe_fisi.birim_adi,
            "birim_kodu": muhasebe_fisi.birim_kodu,
            "muhasebe_fis_no": muhasebe_fisi.muhasebe_fis_no,
            "muhasebe_fis_tarihi": muhasebe_fisi.muhasebe_fis_tarihi,
            "fis_tutari": decimal_parser(muhasebe_fisi.fis_tutari),
            "tutar": muhasebe_fisi.fis_tutari,
            "butce_yili": muhasebe_fisi.butce_yili,
            "ilgili_kisi_bilgileri": {
                "adi_soyadi": "{}".format(muhasebe_fisi.ad_soyad),
                "vergi_kimlik_no": muhasebe_fisi.vergi_kimlik_no,
                "banka_sube": muhasebe_fisi.banka_sube,
                "banka_iban": muhasebe_fisi.banka_iban,
                "bagli_oldugu_vergi_dairesi": muhasebe_fisi.bagli_oldugu_vergi_dairesi
            },
            "proje_bilgileri": {
                "proje_no": muhasebe_fisi.satinalma.proje.proje_no,
                "yurutucu_ad_soyad": "{} {}".format(
                    muhasebe_fisi.satinalma.proje.proje_yurutucu.person.ad,
                    muhasebe_fisi.satinalma.proje.proje_yurutucu.person.soyad),
                "fakulte_bolum": muhasebe_fisi.fakulte_bolum,
            },
            "fis_maddeleri": []
        }

        for fis_maddesi in muhasebe_fisi.fis_maddeleri:
            muhasebe_fisi_data["fis_maddeleri"].append(get_fis_maddesi_data(fis_maddesi))

        return muhasebe_fisi_data

    @staticmethod
    def get_gundem_sablon_proje_data_query():
        """
        Gündem şablonlarında kullanılacak proje verisinin getirildigi queryi olusturur.
        Filtre queryinin kullanildigi yerde eklenecektir."

        :return: BaseQuery object
        """
        bolum = aliased(Birim)
        fakulte = aliased(Birim)
        ogretim_elemani_1 = aliased(OgretimElemani)
        ogretim_elemani_2 = aliased(OgretimElemani)

        proje_data_query = DB.session.query(
            Proje.id.label("proje_id"),
            Proje.proje_no.label("proje_no"),
            Proje.proje_basligi.label("proje_basligi"),
            Proje.teklif_edilen_baslama_tarihi.label("teklif_edilen_baslama_tarihi"),
            Proje.proje_suresi.label("proje_suresi"),
            Proje.proje_suresi_birimi.label("proje_suresi_birimi"),
            Proje.teklif_edilen_butce.label("teklif_edilen_butce"),
            ProjeTuru.ad.label("proje_turu_ad"),
            Person.ad.label("yurutucu_ad"),
            Person.soyad.label("yurutucu_soyad"),
            HitapUnvan.ad.label("yurutucu_hitap_unvan_ad"),
            fakulte.ad.label("fakulte_ad"),
            bolum.ad.label("bolum_ad"),
        ).join(
            ogretim_elemani_1, Proje.yurutucu == ogretim_elemani_1.id
        ).join(
            Personel, ogretim_elemani_1.personel_id == Personel.id
        ).join(
            Person, Personel.person_id == Person.id
        ).join(
            ogretim_elemani_2, Proje.yurutucu == ogretim_elemani_2.id
        ).join(
            HitapUnvan, ogretim_elemani_2.unvan == HitapUnvan.id
        ).join(
            ProjeTuru, Proje.proje_turu == ProjeTuru.id
        ).join(
            bolum, Proje.proje_bolum == bolum.id
        ).join(
            fakulte, Proje.proje_fakulte == fakulte.id
        ).options(
            lazyload("*")
        )
        return proje_data_query

    @staticmethod
    def get_toplanti_with_gundem(toplanti_id):
        toplanti = DB.session.query(
            BapToplanti
        ).filter(
            BapToplanti.id == toplanti_id
        ).options(
            joinedload(BapToplanti.gundemler).lazyload("*"),
            joinedload(BapToplanti.katilimcilar).lazyload("*")
        ).first()

        katilimci_listesi_data = None
        if toplanti.katilimcilar:
            toplanti_katilimcilari_data = {
                "yk_baskani": [],
                "bap_koordinatoru": [],
                "diger": []
            }
            toplanti_katilimcilari = DB.session.query(
                BapIdariPersonel.id.label("id"),
                BapIdariPersonel.gorevi.label("gorevi"),
                Person.ad.label("person_ad"),
                Person.soyad.label("person_soyad")
            ).filter(
                BapIdariPersonel.id.in_(toplanti.katilimcilar.katilimcilar)
            ).join(
                Personel, BapIdariPersonel.personel_id == Personel.id
            ).join(
                Person, Personel.person_id == Person.id
            ).all()
            katilimci_listesi_data = []
            for katilimci in toplanti_katilimcilari:
                if katilimci.gorevi == BapIdariUnvan.yk_baskan:
                    toplanti_katilimcilari_data["yk_baskani"].append(katilimci)
                elif katilimci.gorevi == BapIdariUnvan.bap_koordinatoru:
                    toplanti_katilimcilari_data["bap_koordinatoru"].append(katilimci)
                else:
                    toplanti_katilimcilari_data["diger"].append(katilimci)

            katilimci_listesi_data.extend(toplanti_katilimcilari_data.get("yk_baskani"))
            katilimci_listesi_data.extend(toplanti_katilimcilari_data.get("bap_koordinatoru"))
            katilimci_listesi_data.extend(toplanti_katilimcilari_data.get("diger"))

        toplanti_data = {
            "toplanti": toplanti,
            "toplanti_katilimcilari": katilimci_listesi_data
        }
        return toplanti_data

    @staticmethod
    def get_proje_oneri_formu_info(proje_id):
        proje = DB.session.query(Proje).filter_by(
            id=proje_id).one()
        proje_data = {
            "proje": proje,
            "proje_butce": {},
            "toplam_onerilen_yil_1": 0,
            "toplam_onerilen_yil_2": 0,
            "toplam_onerilen_yil_3": 0,
            "toplam_kabul_edilen_yil_1": 0,
            "toplam_kabul_edilen_yil_2": 0,
            "toplam_kabul_edilen_yil_3": 0,
        }

        for proje_kalemi in proje.proje_kalemleri:
            butce_kalemi_adi = "{} {}".format(
                proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.kodu,
                proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama)
            if not proje_data["proje_butce"].get(butce_kalemi_adi):
                proje_data["proje_butce"][butce_kalemi_adi] = {
                    "proje_kalemleri": [],
                    "toplam_onerilen_yil_1": 0,
                    "toplam_onerilen_yil_2": 0,
                    "toplam_onerilen_yil_3": 0,
                    "toplam_kabul_edilen_yil_1": 0,
                    "toplam_kabul_edilen_yil_2": 0,
                    "toplam_kabul_edilen_yil_3": 0,
                }

            proje_data["proje_butce"][butce_kalemi_adi]["proje_kalemleri"].append({
                "proje_kalemi_ad": proje_kalemi.ad,
                "onerilen_miktar": proje_kalemi.onerilen_miktar,
                "birim": proje_kalemi.birim.value,
                "onerilen_yil_1": proje_kalemi.onerilen_yil_1,
                "onerilen_yil_2": proje_kalemi.onerilen_yil_2,
                "onerilen_yil_3": proje_kalemi.onerilen_yil_3,
                "kabul_edilen_yil_1": proje_kalemi.kabul_edilen_yil_1,
                "kabul_edilen_yil_2": proje_kalemi.kabul_edilen_yil_2,
                "kabul_edilen_yil_3": proje_kalemi.kabul_edilen_yil_3,
            })
            # proje butce kalemi toplam onerilen/kabul edilen butce guncellenir
            proje_data["proje_butce"][butce_kalemi_adi][
                "toplam_onerilen_yil_1"] += proje_kalemi.onerilen_yil_1
            proje_data["proje_butce"][butce_kalemi_adi][
                "toplam_onerilen_yil_2"] += proje_kalemi.onerilen_yil_2
            proje_data["proje_butce"][butce_kalemi_adi][
                "toplam_onerilen_yil_3"] += proje_kalemi.onerilen_yil_3
            proje_data["proje_butce"][butce_kalemi_adi][
                "toplam_kabul_edilen_yil_1"] += proje_kalemi.kabul_edilen_yil_1
            proje_data["proje_butce"][butce_kalemi_adi][
                "toplam_kabul_edilen_yil_2"] += proje_kalemi.kabul_edilen_yil_2
            proje_data["proje_butce"][butce_kalemi_adi][
                "toplam_kabul_edilen_yil_3"] += proje_kalemi.kabul_edilen_yil_3
            # proje butce toplam onerilen kabul edilen yillar guncellenir
            proje_data["toplam_onerilen_yil_1"] += proje_kalemi.onerilen_yil_1
            proje_data["toplam_onerilen_yil_2"] += proje_kalemi.onerilen_yil_2
            proje_data["toplam_onerilen_yil_3"] += proje_kalemi.onerilen_yil_3
            proje_data["toplam_kabul_edilen_yil_1"] += proje_kalemi.kabul_edilen_yil_1
            proje_data["toplam_kabul_edilen_yil_2"] += proje_kalemi.kabul_edilen_yil_2
            proje_data["toplam_kabul_edilen_yil_3"] += proje_kalemi.kabul_edilen_yil_3

        return proje_data

    @staticmethod
    def get_proje_with_butce(proje_id):
        proje = DB.session.query(Proje).filter_by(
            id=proje_id).one()
        proje_data = {
            "proje": proje,
            "proje_butce": {},
            "toplam_butce": 0,
            "harcanan_butce": 0,
            "kalan_butce": 0
        }

        for proje_kalemi in proje.proje_kalemleri:
            butce_kalemi_adi = "{} {}".format(
                proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.kodu,
                proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama)
            if not proje_data["proje_butce"].get(butce_kalemi_adi):
                proje_data["proje_butce"][butce_kalemi_adi] = {
                    "toplam_butce": 0,
                    "harcanan_butce": 0,
                    "kalan_butce": 0
                }

            # butce kalemlerinin butce hesabini yapar
            proje_data["proje_butce"][butce_kalemi_adi]["toplam_butce"] += proje_kalemi.toplam_butce
            proje_data["proje_butce"][butce_kalemi_adi][
                "harcanan_butce"] += proje_kalemi.kullanilan_butce
            proje_data["proje_butce"][butce_kalemi_adi][
                "kalan_butce"] += proje_kalemi.toplam_butce - proje_kalemi.kullanilan_butce

            # projenin butce hesabini yapar
            proje_data["toplam_butce"] += proje_kalemi.toplam_butce
            proje_data["harcanan_butce"] += proje_kalemi.kullanilan_butce
            proje_data["kalan_butce"] += proje_kalemi.toplam_butce - proje_kalemi.kullanilan_butce

        return proje_data

    @staticmethod
    def get_proje_with_hakem(proje_id, hakem_id):
        proje = DB.session.query(Proje).filter_by(
            id=proje_id).one()

        hakem = DB.session.query(Hakem).filter(Hakem.id == hakem_id).first()

        proje_data = {
            "proje": proje,
            "hakem": hakem
        }

        return proje_data
