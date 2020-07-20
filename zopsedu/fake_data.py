"""Modeller icin basit fake data ureteci"""
import os
import random
import sys
from datetime import datetime

from faker import Faker
from sqlalchemy.exc import IntegrityError

from zopsedu.bap.models.analitik_kodlar import GelirSiniflandirma, GiderSiniflandirma
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif, FirmaTeklifKalemi
from zopsedu.bap.models.gelir_kasasi import GelirKasasi, ButceGirdi
from zopsedu.bap.models.helpers import GorunurlukSecenekleri, ButceTercihleri, SablonKategori, \
    ProjeBasvuruDurumu, NotTipi, OlcuBirimi
from zopsedu.bap.models.helpers import ProjeDegerlendirmeSonuc
from zopsedu.bap.models.helpers import ProjeSuresiBirimi
from zopsedu.bap.models.helpers import ProjeTuruKategorisi, EkTalepTipi
from zopsedu.bap.models.helpers import YardimciArastirmaciSecenekleri

from zopsedu.bap.models.helpers import KararDurumu, ToplantiDurumu, GundemTipi
from zopsedu.bap.models.muhasebe_fisi import MuhasebeFisMaddesi, MuhasebeFisi
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_rapor import ProjeRaporTipi, ProjeRaporDurumu
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.common.mesaj.models import Mesaj, MesajEk, MesajTipleri
from zopsedu.lib.db import DB
from zopsedu.models import AppState, AppStateTracker
from zopsedu.models import Hakem, Ogrenci, HitapUnvan, Sablon, SablonTipi
from zopsedu.models import Personel, OgretimElemani, BAPBelge, File
from zopsedu.models import ProjeBelgeleri, ProjeCalisanlari, ProjeDegerlendirmeleri, ProjeDetay, \
    ProjeHakemleri,SiparisTakip
from zopsedu.models import ProjeTuru, Proje, PersonelAyarlari, Butce, Cikti, EkDosya, ButceKalemi, \
    ProjeNot, SabitButceKalemi
from zopsedu.models import User, Birim, HariciOgretimElemani, Adres, Person, ProjeRapor, ProjeMesaj
from zopsedu.models import ToplantiKatilimci, GundemSablon, IcerikEkDosya, Icerik
from zopsedu.models.helpers import JobTypes, SiparisDurumu
from zopsedu.models.helpers import PersonelEngellilik, PersonelStatu, PersonelTuru, HizmetSinifi
from zopsedu.models.odeme_bilgileri import OdemeBilgileri
from zopsedu.models.person import KanGrubu, Cinsiyet, MedeniHali
from zopsedu.ogrenci.models.ogrenci import OgrenimDurumu, MasrafSponsor, OzurDurumu
from zopsedu.personel.models.hakem import HakemTuru
from zopsedu.icerik.model import IcerikTipi, IcerikBirimTipi
from zopsedu.models import BapToplanti, BapGundem, Ozgecmis, BapFirma, FirmaMesaj
from zopsedu.server import app

# pylint: disable=invalid-name
f = Faker('tr_TR')
f_path = os.path.abspath('.') + '/fixture/z.jpg'

# pylint: enable=invalid-name


APP_STATE_PARAMS = [{"proje_id": 1}, {"proje_id": 2}, {"proje_id": 3}, {"proje_id": 4},
                    {"proje_id": 5},
                    {"proje_id": 6}, {"proje_id": 7}, {"proje_id": 8}, {"proje_id": 9},
                    {"proje_id": 10}]


def hitap_unvan(hid=None):  # pylint: disable=unused-argument
    """Hakem Modeli olusturur"""

    return HitapUnvan(
        ad=f.word(),
        kod=f.numerify()
    )


def user(uid=None):  # pylint: disable=unused-argument
    """User Modeli olusturur"""

    with open(f_path, 'br') as sample_file:
        return User(
            username=f.user_name(),
            password=f.password(),
            email=f.email(),
            profile_photo=None,
            avatar=None
        )


def file(fid=None):
    """File Modeli olusturur"""

    with open(f_path, 'br') as sample_file:
        return File(
            user_id=fid,
            content=sample_file,
            uploaded_at=f.date()
        )


def birim(bid=None):
    """Birim Modeli olusturur"""

    return Birim(
        ust_birim_id=bid,
        ad=random.choice([
            'Bilgisayar Muh.',
            'Muhendislik Fak.',
            'Insaat Muh',
            'Docentlik'
        ]),
        uzun_ad=random.choice([
            'Bilgisayar Muh.',
            'Muhendislik Fak.',
            'Insaat Muh',
            'Docentlik'
        ]),
        birim_tipi=f.word(),
        ogrenim_dili='Turkce',
        ogrenme_tipi=f.word(),
        ogrenim_suresi=random.choice(range(1, 6)),
        ingilizce_birim_adi=random.choice([
            'Bilgisayar Muh.',
            'Muhendislik Fak.',
            'Insaat Muh',
            'Docentlik'
        ]),
        sehir_kodu=random.choice(range(1, 82)),
        semt_kodu=random.choice(range(1, 82)),
        aktif_mi=random.choice([False, True])
    )


def adres(aid=None):  # pylint: disable=unused-argument
    """Adres Modeli olusturur"""

    return Adres(
        posta_kodu=f.postalcode(),
        adres=f.address(),
        ilce=f.city(),
        il=f.city()
    )


def person(pid=None):
    """Person Modeli olusturur"""

    return Person(
        user_id=pid,
        ikametgah_adresi_id=pid,
        ikincil_adres_id=pid,
        ad=random.choice([f.first_name_male(), f.first_name_female()]),
        soyad=random.choice([f.last_name_male(), f.last_name_female()]),
        birincil_eposta=f.email(),
        ikincil_eposta=f.email(),
        tckn=str(random.choice(range(10000000000, 99999999999))),
        kimlik_cuzdani_seri=f.ssn(),
        kimlik_cuzdani_seri_no=random.choice(range(1000, 9999)),

        kayitli_oldugu_il=f.city(),
        kayitli_oldugu_ilce=f.city(),
        kayitli_oldugu_mahalle_koy=f.state(),
        kayitli_oldugu_cilt_no=random.choice(range(1000, 9999)),
        kayitli_oldugu_aile_sira_no=random.choice(range(1000, 9999)),
        kayitli_oldugu_sira_no=random.choice(range(1000, 9999)),

        kimlik_cuzdani_verildigi_yer=f.city(),
        kimlik_cuzdani_verilis_nedeni=f.word(),
        kimlik_cuzdani_kayit_no=random.choice(range(1000, 9999)),
        kimlik_cuzdani_verilis_tarihi=f.date(),

        ana_adi=f.first_name_female(),
        baba_adi=f.first_name_male(),
        dogum_tarihi=f.date(),
        dogum_yeri=f.city(),

        uyruk=f.word(),
        cinsiyet=random.choice([c.name for c in Cinsiyet]),
        kan_grubu=random.choice([c.name for c in KanGrubu]),
        medeni_hali=random.choice([c.name for c in MedeniHali]),
        cep_telefonu=random.choice(range(10000000, 99999999)),
        ev_tel_no=random.choice(range(10000000, 99999999)),
        ehliyet=random.choice(['Var', 'Yok'])
    )


def personel(pid=None):
    """Personel Modeli olusturur"""

    return Personel(
        person_id=pid,
        birim=pid,
        unvan=pid,

        kurum_sicil_no=f.numerify(),

        web_sitesi=f.profile()['website'][0],
        yayinlar=f.word(),
        projeler=f.word(),
        biyografi=f.word(),
        notlar=f.word(),

        oda_no=f.numerify(),
        oda_tel_no=random.choice(range(10000000, 99999999)),

        # verdigi_dersler = field.String(_(u"Verdiği Dersler"))
        engelli_durumu=f.boolean(),
        engel_grubu=f.word()[0:45],
        engel_derecesi=random.choice([pe.name for pe in PersonelEngellilik]),
        engel_orani=random.choice(range(0, 100)),
        bakmakla_yukumlu_kisi_sayisi=random.choice(range(0, 10)),
        #
        kazanilmis_hak_derece=random.choice(range(0, 10)),
        kazanilmis_hak_kademe=random.choice(range(0, 10)),
        kazanilmis_hak_ekgosterge=random.choice(range(0, 10)),
        #
        gorev_ayligi_derece=random.choice(range(0, 10)),
        gorev_ayligi_kademe=random.choice(range(0, 10)),
        gorev_ayligi_ekgosterge=random.choice(range(0, 10)),
        #
        emekli_muktesebat_derece=random.choice(range(0, 10)),
        emekli_muktesebat_kademe=random.choice(range(0, 10)),
        emekli_muktesebat_ekgosterge=random.choice(range(0, 10)),
        # Kazanılmış Hak Sonraki Terfi Tarihi
        kh_sonraki_terfi_tarihi=f.date(),
        # Görev Aylığı Sonraki Terfi Tarihi
        ga_sonraki_terfi_tarihi=f.date(),
        # Emekli Müktesebat Sonraki Terfi Tarihi
        em_sonraki_terfi_tarihi=f.date(),
        #
        #
        #
        # # Aşağıdaki bilgiler atama öncesi kontrol edilecek, Doldurulması istenecek
        emekli_sicil_no=f.word()[0:45],
        emekli_giris_tarihi=f.date(),

        personel_turu=random.choice([pt.name for pt in PersonelTuru]),
        hizmet_sinifi=random.choice([hs.name for hs in HizmetSinifi]),
        statu=random.choice([ps.name for ps in PersonelStatu]),
        #
        # # akademik personeller icin sozlesme sureleri
        gorev_suresi_baslama=f.date(),
        gorev_suresi_bitis=f.date()
    )


def ogrenci(oid=None):
    """Ogrenci Modeli olusturur"""

    return Ogrenci(
        person_id=oid,
        aile_adres_id=oid,

        baba_ogrenim_durumu=random.choice([od.name for od in OgrenimDurumu]),
        baba_meslek=f.job()[0:50],
        baba_aylik_kazanc=f.numerify(),

        anne_ogrenim_durumu=random.choice([od.name for od in OgrenimDurumu]),
        anne_meslek=f.job()[0:50],
        anne_aylik_kazanc=f.numerify(),

        masraf_sponsor=random.choice([ms.name for ms in MasrafSponsor]),
        veli_emeklilik_durumu=f.word(),
        kiz_kardes_sayisi=random.choice(range(0, 10)),
        erkek_kardes_sayisi=random.choice(range(0, 10)),
        ogrenim_goren_kardes_sayisi=random.choice(range(0, 10)),
        burs_kredi_no=f.numerify(),
        aile_ev_tel=random.choice(range(10000000, 99999999)),
        aile_cep_telefonu=random.choice(range(10000000, 99999999)),
        ozur_durumu=random.choice([ozd.name for ozd in OzurDurumu]),
        ozur_oran=random.choice(range(0, 100)),
    )


def hakem(hid=None):
    """Hakem Modeli olusturur"""

    return Hakem(
        person_id=hid,
        personel_id=hid,
        unvan=hid,
        hakem_turu=random.choice([ht.name for ht in HakemTuru]),
        kurum_ici=random.choice([True, False]),
        universite_id=hid,
        fakulte_id=hid,
        bolum_id=hid
    )


def harici_ogretim_elemani(hid=None):
    """HariciOgretimElemani Modeli olusturur"""

    return HariciOgretimElemani(
        person_id=hid,

        oda_no=random.choice(range(0, 100)),
        oda_tel_no=random.choice(range(10000000, 99999999)),

        web_sitesi=f.profile()['website'][0],
        yayinlar=f.text(),
        projeler=f.text(),

        biyografi=f.text(),
        notlar=f.text(),
        engelli_durumu=f.boolean(),
        engel_grubu=f.word(),
        engel_derecesi=random.choice([pe.name for pe in PersonelEngellilik]),
        engel_orani=random.choice(range(0, 100)),
        aktif_mi=f.boolean(),
        unvan=hid,
        akademik_yayinlari=f.text()
    )


def ogretim_elemani(oid=None):
    """OgretimElemani Modeli olusturur"""

    return OgretimElemani(
        personel_id=oid,
        harici_ogretim_elamani_id=oid,
        unvan=oid
    )


def bap_belge(fid=None):
    """BAPBelge Modeli olusturur"""

    return BAPBelge(
        file_id=fid,
        adi=f.word(),
        aciklama=f.word(),
        turler=f.word()
    )


def sablon_tipi(pid):
    return SablonTipi(adi="Örnek Şablon Tipi {}".format(pid),
                      module_name="BAP")


def sablon(pid):
    return Sablon(adi="Örnek Sablon Tipi {}".format(pid),
                  sablon_tipi_id=pid,
                  sablon_text="Fake data sablon",
                  module_name="BAP",
                  kullanilabilir_mi=True)


def proje_turu(pid=None):
    """ProjeTuru Modeli olusturur"""

    return ProjeTuru(
        tur_kodu=f.numerify(),
        guncel_mi=None,

        ad=f.word(),
        kategori=random.choice([pk.name for pk in ProjeTuruKategorisi]),

        basvuru_baslama_tarihi=f.date_time_between(start_date='now', end_date='+10y'),
        basvuru_bitis_tarihi=f.date_time_between(start_date='+11y', end_date='+20y'),

        # basvuru hakem oneri sarti ve sayisi
        hakem_onerilsin_mi=f.boolean(),
        basvuru_hakem_oneri_sayisi=f.numerify(),
        hakem_degerlendirmesi_gerekli_mi=f.boolean(),

        # proje süre limitleri
        sure_alt_limiti=random.choice(range(0, 10)),
        sure_ust_limiti=random.choice(range(11, 20)),
        sure_birimi=random.choice([ps.name for ps in ProjeSuresiBirimi]),
        # ek süre ile ilgili alanlar
        ek_sure_talep_tipi=random.choice([et.name for et in EkTalepTipi]),
        ek_sure_talep_degeri=random.choice(range(1, 100)),
        ek_sureler_proje_sure_limitine_dahil_mi=f.boolean(),

        proje_mali_destek_suresi=random.choice(range(0, 10)),
        mali_destek_suresi_birimi=random.choice([ps.name for ps in ProjeSuresiBirimi]),

        # Proje tipi yuksek lisans / doktora (uzmanlik) veya belirtilmemis
        # proje_tipi=random.choice([pt.name for pt in ProjeTipi]),

        # proje türü için gerekli formlar
        oneri_sablon_id=None,
        hakem_degerlendirme_sablon_id=None,
        hakem_ara_rapor_sablon_id=None,
        hakem_sonuc_rapor_sablon_id=None,
        ara_rapor_sablon_id=None,
        sonuc_raporu_sablon_id=None,

        # diger alanlardan bagımsız boolean fieldlar
        basvuru_aktif_mi=f.boolean(),
        proje_ek_talepleri_icin_rapor_kontrolu_yapilacak_mi=f.boolean(),
        herkese_acik_proje_listesinde_yer_alacak_mi=f.boolean(),

        # Hangi raporlar gerekli? Sadece sonuc, ara ve sonuc, ikisi de gerekli degil
        ara_rapor_gerekli_mi=f.boolean(),
        sonuc_raporu_gerekli_mi=f.boolean(),

        # ek dosya ayarları
        proje_yurutucusu_ek_dosyalar_ekleyebilir_mi=f.boolean(),
        is_zaman_plani_otomasyon_icerisinde_doldurulsun_mu=f.boolean(),
        ek_dosya_yuklenebilir_mi=f.boolean(),

        # butce tercihi
        butce_tercihi=ButceTercihleri.butce_ile_ilgili_islem_yapmasin,

        genel_uyari_mesajlari={}
    )


def butce(bid=None):
    """Butce Modeli olusturur"""

    return Butce(
        proje_turu_id=bid,

        # proje butce limitleri
        butce_alt_limiti=random.uniform(10000, 499999),
        butce_ust_limiti=random.uniform(500000, 999999),
        # ek butce ile ilgili alanlar
        ek_butce_talep_tipi=random.choice([et.name for et in EkTalepTipi]),
        ek_butce_talep_degeri=random.choice(range(1, 100)),
        ek_butce_proje_butce_limitine_dahil_mi=f.boolean(),

        kalemlere_ait_butce_yillara_gore_verilebilecek_mi=f.boolean(),

        kalemlere_ait_kdv_girilsin_mi=f.boolean(),
        kalemlere_ait_butce_kodlari_girilsin_mi=f.boolean()
    )


def cikti(cid=None):
    """Cikti Modeli olusturur"""

    return Cikti(
        proje_turu_id=cid,
        sablon_id=cid,
        adi=f.word(),
        gorunurluk=random.choice([gs.name for gs in GorunurlukSecenekleri]),
        belge_ciktisi_alinacak_mi=f.boolean()
    )


def ek_dosya(eid=None):
    """EkDosya Modeli olusturur"""

    return EkDosya(
        proje_turu_id=eid,
        dosya_id=eid,

        zorunlu_mu=f.boolean(),
        proje_icerik_dosyasi_mi=f.boolean(),
        belgenin_ciktisi_alinacak_mi=f.boolean()
    )


def butce_kalemi(bid=None):
    """ButceKalemi Modeli olusturur"""

    return ButceKalemi(
        proje_turu_id=bid,
        # sabit_butce_kalemi_id=bid,
        butce_alt_limiti=random.uniform(10000, 499999),
        butce_ust_limiti=random.uniform(500000, 999999),
    )


def proje(pid=None):
    """Proje Modeli olusturur"""

    return Proje(
        proje_turu=pid,
        proje_basvuru_durumu=ProjeBasvuruDurumu.tamamlandi,
        proje_turu_numarasi=f.numerify(),
        # proje_turu_kategorisi=random.choice([pk.name for pk in ProjeTuruKategorisi]),

        proje_fakulte=pid,
        proje_bolum=pid,
        proje_ana_bilim_dali=pid,
        proje_bilim_dali=pid,

        # Başvuruda doldurulacak alanlar
        proje_durumu_id=pid,
        yurutucu=pid,
        gerceklestirme_gorevlisi=pid,
        harcama_yetkilisi=pid,
        muhasebe_yetkilisi=pid,
        klasor_sira_no=pid,
        onaylayan_yetkili_id=pid,
        onay_tarihi=f.date(),

        proje_disiplinler_arasi_mi=f.boolean(),
        proje_suresi=f.numerify(),
        proje_suresi_birimi=random.choice([ps.name for ps in ProjeSuresiBirimi]),
        etik_kurulu_izin_belgesi=f.boolean(),

        # Komisyon kararıyla doldurulacak alanlar
        proje_no=f.numerify(),
        kabul_edilen_baslama_tarihi=f.date(),
        kabul_edilen_butce=f.numerify(),

        proje_basligi=f.word(),
        project_title=f.word(),
        anahtar_kelimeler=None,

        # sure = field.Integer(_(u"Süre(Ay Cinsinden Olmalıdır)"))
        teklif_edilen_baslama_tarihi=f.date(),
        teklif_edilen_butce=random.uniform(10000, 999999),
        bitis_tarihi=f.date(),

        ozet=f.text(),
        literatur_ozet=f.text(),
        amac_kapsam=f.text(),
        gerec_yontem=f.text(),
        arastirma_olanaklari=f.text(),
        beklenen_bilimsel_katki=f.text(),
        uygulama_plani=f.text()

    )


def mesaj(mid=None):
    """Mesaj Modeli olusturur"""

    return Mesaj(
        gonderen=mid,
        alici=mid,
        baslik=f.word(),
        metin=f.text(),
        mesaj_tipi=random.choice([mt.name for mt in MesajTipleri]),
        gonderim_zamani=f.date(),
        okunma_zamani=f.date(),
        okunma_ip_adresi=f.word(),
        okundu=f.boolean()
    )


def proje_detay(pid=None):
    """ProjeDetay Modeli olusturur"""

    return ProjeDetay(
        proje_id=pid,

        butce_fazlaligi=random.uniform(10000, 999999),
        konu_ve_kapsam=f.text(),
        literatur_ozeti=f.text(),
        ozgun_deger=f.text(),
        hedef_ve_amac=f.text(),
        yontem=f.text(),
        basari_olcutleri=f.text(),
        b_plani=f.text(),

        universite_disi_uzmanlar=None,
        universite_disi_destekler=None,
        arastirma_olanaklari=f.text()
    )


def proje_belgeleri(pid=None):
    """ProjeBelgeleri Modeli olusturur"""

    return ProjeBelgeleri(
        proje_id=pid,
        belge_id=pid,
        proje_turu_ek_dosya_id=pid,
        baslik=f.word(),
        aciklama=f.text()
    )


def proje_calisanlari(pid=None):
    """ProjeCalisanlari Modeli olusturur"""

    return ProjeCalisanlari(
        proje_id=pid,
        personel_id=pid,
        ogrenci_id=pid,
        person_id=pid,
        hitap_unvan_id=pid,
        fakulte_id=pid,
        bolum_id=pid,
        ozgecmis_id=pid,

        is_telefonu=f.word(),
        projedeki_gorevi=f.word(),
        projeye_katkisi=random.uniform(10000, 999999),
        projeye_bilimsel_katkisi=f.word(),
        yonetici_yetkisi_varmi=f.boolean(),

        universite_disindan_mi=f.boolean(),
        # iban numarası en fazla 32 haneli olabiliyor(dünya genelinde)
        banka_bilgisi=f.word()
    )


def proje_hakemleri(pid=None):
    """ProjeHakemleri Modeli olusturur"""
    from zopsedu.bap.models.proje_detay import ProjeHakemDavetDurumlari

    return ProjeHakemleri(
        proje_id=pid,
        hakem_id=pid,
        davet_durumu=ProjeHakemDavetDurumlari.kabul_edildi
    )


def proje_degerlendirmeleri(pid=None):
    """ProjeDegerlendirmeleri Modeli olusturur"""

    return ProjeDegerlendirmeleri(
        proje_hakem_id=pid,
        rapor_id=pid,
        degerlendirme_gonderim_tarihi=f.date(),
        degerlendirme_sonuclandi_mi=f.boolean(),
        degerlendirme=f.text(),
        sonuc=random.choice([pd.name for pd in ProjeDegerlendirmeSonuc])
    )


def personel_ayarlari(pid=None):
    """PersonelAyarlari Modeli olusturur"""

    return PersonelAyarlari(
        proje_turu_id=pid,

        yardimci_arastirmaci_secenekleri=random.choice(
            [ya.name for ya in YardimciArastirmaciSecenekleri]),
        yardimci_arastirmaci_alt_limiti=random.choice(range(0, 10)),
        yardimci_arastirmaci_ust_limiti=random.choice(range(11, 20)),

        ozgecmis_yuklenmesi_zorunlu_mu=f.boolean(),
        dosya_olarak_ozgecmis_yuklenebilir_mi=f.boolean(),
        banka_bilgilerini_girmek_zorunlu_mu=f.boolean()
    )


def proje_rapor(pid=None):
    """ProjeRapor Modeli olusturur"""

    return ProjeRapor(
        proje_id=pid,
        rapor_tipi=ProjeRaporTipi.proje_basvuru,
        rapor_baslangic_tarihi=f.date_time_between(start_date='now', end_date='now'),
        rapor_bitis_tarihi=f.date_time_between(start_date='+11y', end_date='+20y'),
        rapor_icerigi=f.sentence(),
        durumu=random.choice([durumu.name for durumu in ProjeRaporDurumu]),
        duzenlenebilir_mi=f.boolean(),
        file_id=pid,
    )


def mesaj_ek(mid=None):
    """MesajEk Modeli olusturur"""

    return MesajEk(
        belge=mid,
        mesaj_id=mid
    )


def proje_mesaj(pid=None):
    """ProjeMesaj Modeli olusturur"""

    return ProjeMesaj(
        proje_id=pid,
        mesaj_id=pid
    )


def bap_toplanti(bid=None):
    """BapToplanti Modeli olusturur"""

    return BapToplanti(
        toplanti_tarihi=f.date_time_between(start_date='now', end_date='+120d'),
        toplanti_durumu=ToplantiDurumu.gerceklestirilmedi,
        ekleyen_id=bid,
    )


def toplanti_katilimci(tid=None):
    """ToplantiKatilimci Modeli olusturur"""

    return ToplantiKatilimci(
        toplanti_id=tid,
        katildi_mi=f.boolean(),
        unvan=tid,
        ad=random.choice([f.first_name_male(), f.first_name_female()]),
        soyad=random.choice([f.last_name_male(), f.last_name_female()]),
        email=f.email(),
        cep_telefonu=random.choice(range(10000000, 99999999)),
    )


def bap_gundem(bid=None):
    """BapGundem Modeli olusturur"""

    return BapGundem(
        proje_id=bid,
        toplanti_id=None,  # toplanti id olmayan gundemler gundem listeleme
        # ekranina duser, bu gundemler toplantiya eklenerek yeni toplanti kaydi olusturulur
        ek_dosya_id=bid,
        karar=f.sentence(),
        aciklama=f.sentence(),
        tipi=random.choice([gt for gt in GundemTipi]),
        karar_durum=KararDurumu.degerlendirilmedi,
        gundem_sira_no=1,
        yonetime_bilgi_notu=f.sentence(),
        kisiye_ozel_not=f.sentence(),
    )


def bap_duyuru(pid=None):
    """
        Bap Duyuru Ekler
    """
    return Icerik(
        ekleyen_id=pid,
        tipi=IcerikTipi.duyuru,
        birim_tipi=IcerikBirimTipi.bap,
        baslik="Örnek Duyuru Başlık {}".format(pid),
        icerik="Örnek Duyuru İçeriği {}".format(pid),
        on_sayfa_gorunurlugu=random.choice([True, False]),
        aktif_mi=random.choice([True, False]),
        baslangic_tarihi=f.date_time_between(start_date='-1y', end_date='now'),
        bitis_tarihi=f.date_time_between(start_date='+1y', end_date='+2y'),
    )


def icerik_ek_dosya(pid=None):
    """
        Bap Duyuru Ekler
    """
    return IcerikEkDosya(
        adi=f.word(),
        file_id=pid,
        icerik_id=pid)


def ozgecmis(pid=None):
    """
        Ozgecmis ekler
    """
    return Ozgecmis(
        file_id=pid,
        tecrube=f.text(),
    )


def odeme_bilgileri(pid=None):
    """
    Odeme bilgilerini ekler

    """

    return OdemeBilgileri(
        id=pid,
        banka_adi=f.sentence(),
        sube_adi=f.sentence(),
        sube_kod=random.choice(range(100000, 999999)),
        hesap_no=random.choice(range(100000, 999999)),
        iban_no=f.sentence(),
        person_id=pid
    )


def app_state(pid=None):
    return AppState(
        id=pid
    )


def app_state_tracker(pid=None):
    """
        App State Tracker bilgilerini ekler

        """
    return AppStateTracker(
        state_id=pid,
        params=random.choice([ap for ap in APP_STATE_PARAMS]),
        date=datetime.now(),
        description=f.sentence(),
        job_type=JobTypes.project_state_change,
        triggered_by=pid,
    )


def proje_not(pid=None):
    """
    Proje yetkili tarafından girilen notlari ekler

    """
    return ProjeNot(
        proje_id=pid,
        notu_ekleyen_yetkili=pid,
        notu=f.sentence(),
        not_tipi=random.choice([ap.name for ap in NotTipi])

    )


def bap_firma(bid=None):
    return BapFirma(
        firma_faaliyet_belgesi_id=bid,
        adres=f.address(),
        adi=f.word(),
        telefon=random.choice(range(10000000, 99999999)),
        email=f.email(),
        iban="TR12312312312313",
        banka_sube_adi="ZOPSEdu Bankası / Zopsedu Subesi",
        vergi_kimlik_numarasi=random.choice(range(10000000, 99999999)),
        faaliyet_belgesi_verilis_tarihi=f.date(),
        yetkili_adi=f.first_name_male(),
        yetkili_soyadi=f.last_name_female(),
    )


def firma_mesaj(fid=None):
    return FirmaMesaj(
        firma_id=fid,
        mesaj_id=fid
    )


def gelir_siniflandirma(iid=None):
    return GelirSiniflandirma(
        kodu='05.05',
        aciklama=f.word()
    )


def gider_siniflandirma(iid=None):
    return GiderSiniflandirma(
        kodu='05.05',
        aciklama=f.word()
    )


def gelir_kasalari(gid=None):
    return GelirKasasi(
        adi=f.word(),
        mali_yil=random.choice(range(2017, 2019)),
        toplam_para=50000000,
        harcanan_para=35000000,
        rezerv_para=14000000,
        devreden_para=1000000,
        devredilen_para=0,
    )


def butce_girdi(bid=None):
    return ButceGirdi(
        gelir_kasasi_id=bid,
        tutar=random.choice(range(10000000, 99999999)),
        aciklama=f.sentence(),
    )


def butce_kalemi(pid=None):
    return ButceKalemi(
        proje_turu_id=pid,
        gider_siniflandirma_id=pid,
        butce_alt_limiti=random.choice(range(10000000, 20000000)),
        butce_ust_limiti=random.choice(range(1000000, 9999999))
    )


def sabit_butce_kalemi(sbi=None):
    return SabitButceKalemi(
        adi=f.word(),
        analitik_kodu="03.05.05"
    )


def proje_kalemleri(pid=None):
    return ProjeKalemi(

        proje_id=pid,
        proje_turu_butce_kalem_id=pid,

        ad=f.word(),
        gerekce=f.sentence(),
        birim=random.choice([c.name for c in OlcuBirimi]),
        onerilen_miktar=10,
        toplam_miktar=10,
        kullanilan_miktar=3,
        rezerv_edilen_miktar=2,
        onerilen_butce=random.choice(range(1000, 90000)),
        toplam_butce=90000,
        rezerv_butce=random.choice(range(1000, 80000)),
        kullanilan_butce=10000,
        onerilen_yil_1=random.choice(range(1000, 90000)),
        onerilen_yil_2=random.choice(range(1000, 90000)),
        onerilen_yil_3=random.choice(range(1000, 90000)),
        kabul_edilen_yil_1=random.choice(range(1000, 90000)),
        kabul_edilen_yil_2=random.choice(range(1000, 90000)),
        kabul_edilen_yil_3=random.choice(range(1000, 90000)),
    )


def butce(pid=None):
    return Butce(
        proje_turu_id=pid,
        butce_alt_limiti=1000000,
        butce_ust_limiti=9000000,
        ek_butce_talep_tipi=random.choice([c.name for c in EkTalepTipi]),
        ek_butce_talep_degeri=90,
        ek_butce_proje_butce_limitine_dahil_mi=f.boolean(),
        kalemlere_ait_butce_yillara_gore_verilebilecek_mi=f.boolean(),
        kalemlere_ait_kdv_girilsin_mi=f.boolean(),
        kalemlere_ait_butce_kodlari_girilsin_mi=f.boolean()
    )


def proje_satinalma_talepleri(pid=None):
    return ProjeSatinAlmaTalebi(
        proje_id=pid,
        durum_id=2,
        duyuru_id=pid,
        talep_numarasi=pid,
        butce_kalem_id =pid,
        mkk_baskan_id=pid,
        mkk_uye1_id=pid,
        mkk_uye2_id=pid,
        mkk_yedek_baskan_id=pid,
        mkk_yedek_uye1_id=pid,
        mkk_yedek_uye2_id=pid
    )

def talep_kalemleri(pid=None):
    return TalepKalemleri(
    satinalma_id = pid,
    proje_kalemi_id = pid,
    teknik_sartname_file_id = pid,
    talep_miktari = 2
    )


def firma_satinalma_teklif(sid=None):
    return FirmaSatinalmaTeklif(
    firma_id = sid,
    satinalma_id = sid,
    aciklama = f.sentence(),
    teklif_tamamlandi_mi = random.choice([True,False])
    )


def firma_teklif_kalemi(sid=None):
    return FirmaTeklifKalemi(
    satinalma_talep_kalemi_id = sid,
    teklif_id = sid,
    marka_model = f.word(),
    kdv_orani = 18,
    teklif = random.choice(range(201700, 201900)),
    teslimat_suresi = random.choice(range(1, 13))
    )


def siparis_takip(sid=None):
    return SiparisTakip(satinalma_talep_kalemleri_id=sid,
                        kazanan_firma_teklif_id=sid,
                        siparis_numarasi=sid,
                        teslim_edilmesi_beklenen_tarih=f.date(),
                        siparis_tarihi=f.date(),
                        siparis_durumu=SiparisDurumu.firma_bekleniyor.name
                        )



MODELS = {
    'hitap': hitap_unvan,
    'users': user,
    'adres': adres,
    # 'sablon_tipi': sablon_tipi,
    # 'sablon': sablon,
    # 'belge': file,
    'birim': birim,
    'person': person,
    'file': file,
    'personel': personel,
    # 'ogrenci': ogrenci,
    # 'hakem': hakem,
    # 'harici_ogretim_elemani': harici_ogretim_elemani,
    # 'ogretim_elemani': ogretim_elemani,
    # 'sabit_butce_kalemi': sabit_butce_kalemi,
    # 'bap_belge': bap_belge,
    # 'proje_turu': proje_turu,
    # 'butce': butce,
    # 'personel_ayarlari': personel_ayarlari,
    # 'cikti': cikti,
    # 'ek_dosya': ek_dosya,
    # 'butce_kalemi': butce_kalemi,
    # 'app_state': app_state,
    # 'proje': proje,
    # 'mesaj': mesaj,
    'ozgecmis': ozgecmis,
    # 'proje_detay': proje_detay,
    # 'proje_belgeleri': proje_belgeleri,
    # 'proje_calisanlari': proje_calisanlari,
    # 'proje_rapor': proje_rapor,
    # 'proje_hakemleri': proje_hakemleri,
    # 'proje_degerlendirmeleri': proje_degerlendirmeleri,
    # 'mesaj_ekleri': mesaj_ek,
    # 'proje_mesaj': proje_mesaj,
    # 'bap_toplanti': bap_toplanti,
    # 'toplanti_katilimci': toplanti_katilimci,
    # 'bap_gundem': bap_gundem,
    'bap_duyuru': bap_duyuru,
    # 'icerik_ek_dosya': icerik_ek_dosya,
    'odeme_bilgileri': odeme_bilgileri,
    # 'app_state_tracker': app_state_tracker,
    # 'proje_not': proje_not,
    # 'bap_firma': bap_firma,
    # 'firma_mesaj': firma_mesaj,
    # 'gelir_siniflandirma': gelir_siniflandirma,
    # 'gider_siniflandirma': gider_siniflandirma,
    # 'gelir_kasalari': gelir_kasalari,
    # 'butce_girdi': butce_girdi,
    # 'butce_kalemi': butce_kalemi,
    # 'sabit_butce_kalemi': sabit_butce_kalemi,
    # 'proje_kalemleri': proje_kalemleri,
    # 'proje_satinalma_talepleri': proje_satinalma_talepleri,
    # 'talep_kalemleri':talep_kalemleri,
    # 'firma_satinalma_teklif':firma_satinalma_teklif,
    # 'firma_teklif_kalemi':firma_teklif_kalemi,
    # 'siparis_takip':siparis_takip
}


def produce_and_save(model, number):
    """
    Verilen `model` icin belirtilen sayida veri uretip veritabanina kaydeder.

    Args:
        model (str): model adi
        number (int): kayit sayisi

    Returns:

    """
    session = DB.session
    try:
        for i in range(1, number + 1):
            if i == app.config['UNIVERSITE_ID'] and model == 'hakem':
                hakem_obj = Hakem(
                    personel_id=i,
                    hakem_turu=random.choice([ht.name for ht in HakemTuru]),
                    kurum_id=i)
                session.add(hakem_obj)
            else:
                obj = MODELS[model](i)
                session.merge(obj)
        session.commit()
        session.close()
    except IntegrityError as iexc:
        print(str(iexc))


if __name__ == '__main__':
    # pylint: disable=invalid-name
    model_name = sys.argv[1]
    num = int(sys.argv[2])

    if model_name == 'all':
        for key, _ in MODELS.items():
            produce_and_save(key, num)
    else:
        produce_and_save(model_name, num)
    # pylint: enable=invalid-name
