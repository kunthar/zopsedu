"""
Helpers modülü bap modellerinde kullanılacak enum sınıflarını içerir
"""
import enum
from zopsedu.lib.helpers import WTFormEnum



class BAPBelgeTipi(str, WTFormEnum):
    faaliyet_raporlari = "Faaliyet Raporları"
    mevzuat = "Mevzuat"
    formlar_ve_belgeler = "Formlar ve Belgeler"
    bap_hakkinda = "BAP Hakkında"


class EkTalepTipi(str, WTFormEnum):
    """
    "Proje türü" ek süre talep ve ek butce talep alanı için oluşturulmuş enum sınıf
    """
    yok = "Yok"
    en_fazla = "En Fazla"
    yuzde = "Yüzde"
    sinirsiz = "Sınırsız"


class ProjeTipi(str, WTFormEnum):
    """
    "Proje türü" proje tipi alanı için oluşturulmuş enum sınıf
    """
    yuksek_lisans = "Yüksek Lisans"
    doktora = "Doktora"
    belirtilmemis = "Belirtilmemiş"


class ProjeTuruKategorisi(str, WTFormEnum):
    """
    "Proje türü"  kategori alanı için oluşturulmuş enum sınıf
    """
    bilimsel_arastirma_projesi = 'Bilimsel Araştırma Projesi'
    kapsamli_bilimsel_arastirma = 'Kapsamlı Bilimsel Araştırma Projesi'
    sanayi_isbirligi = 'Sanayi İşbirliği Projesi'
    es_finansman_proje_destegi = 'Eş Finansman Projesi Desteği'
    uluslararasi_isbirligi_faaliyet = 'Uluslararası İşbirliği Faaliyetleri Destekleme Projesi'
    fikri_sinai_mulkiyet = 'Fikri ve Sınai Mülkiyet Hakları Destek Projesi'
    lisans_ogrencisi_katilimli_arastirma = 'Lisans Öğrencisi Katılımlı Araştırma Projesi'
    lisans_ogrenci_arastirma = 'Lisans Öğrenci Araştırma Projesi'
    yayin_tesvik_destek = 'Yayın Teşvik Destek Projesi'
    kurum_disi_ortak_katilimli_arastirma = 'Kurum Dışı Ortak Katılımlı Araştırma Projesi'
    doktora_tezi_arastirma = 'Doktora Tezi Araştırma Projesi'
    tipta_uzmanlik = 'Tıpta Uzmanlık Projesi'
    hizli_destek = 'Hızlı Destek Projesi'
    bilimsel_toplanti_duzenleme = 'Bilimsel Toplantı Düzenleme Projesi'
    bilimsel_toplanti_destek = 'Bilimsel Toplantı Desteği Projesi'
    bilimsel_alt_yapi = 'Bilimsel Alt Yapı Projesi'
    temel_arastirma = 'Temel Araştırma Projesi'
    baslangic_destek = 'Başlangıç Destek Projesi'
    yurt_dizi_arastirma = 'Yurt Dışı Araştırma Projesi'
    lisansustu_tez = 'Lisansüstü Tez Projesi'
    arastirma_baslangic_destek = 'Araştırma Başlangıç Destek Projesi'
    arastirma_tesvik = 'Araştırma Teşvik Projesi'
    oncelikli_alanlar_arastirma = 'Öncelikli Alanlar Araştırma Projesi'
    kurumsal_alt_yapi = 'Kurumsal Alt yapı Projesi'
    diger_kurumlarca_fonlanmis_arastirma_destekleme = 'Diğer Kurumlarca Fonlanmış Araştırmaları Destekleme Projesi'
    katilimli_arastirma = 'Katılımlı Araştırma Projesi'
    gudumlu_proje = 'Güdümlü Proje'


class YardimciArastirmaciSecenekleri(str, WTFormEnum):
    """
    "Proje türü personel ayarları" modeli yardimci arastirmaci secenekleri alanı
     için oluşturulmuş enum sınıf
    """
    sadece_proje_yurutucusu = "Sadece proje yürütücüsü"
    sadece_danisman_ve_tez_ogrencisi = "Sadece danışman ve tez öğrencisi"
    sinirsiz_yardimci_arastirmaci = "Sınırsız yardımcı araştırmacı"
    sinirli = "Sınırlı"


class GorunurlukSecenekleri(str, WTFormEnum):
    """
    "Proje cıktı" modeli gorunurluk alanı için olusturulmuş enum sınıf
    """
    sadece_yonetici = "Sadece Yönetici"
    yurutucu_ve_yonetici = "Yürütücü ve Yönetici"


class ButceTercihleri(str, WTFormEnum):
    """
    Proje türünün bütçesinin nasıl belirleneceğini belirten seçenekler.
    """
    proje_yurutucusu_onersin = "Proje yürütücüsü önersin"
    # sabit_seceneklerden_birini_secsin = "Sabit seçeneklerden birini seçsin"
    butce_ile_ilgili_islem_yapmasin = "Bütçe ile ilgili işlem yapmasın"




class ProjeDegerlendirmeSecenekleri(str, enum.Enum):
    """
    Proje değerlendirme formu secenekleri
    """
    evet = 'Evet'
    hayir = 'Hayır'
    kismen = 'Kısmen'


class ProjeDegerlendirmeSonuc(str, WTFormEnum):
    """Proje hakem değerlendirmelerinin sonuçlarını temsil eden enum class"""

    olumlu = "Olumlu. Proje desteklenmelidir."
    olumsuz = "Olumsuz. Proje desteklenmemelidir."
    revizyon = "Revizyon gerekli."
    degerlendirilmedi = "Değerlendirilmedi"


class ProjeSuresiBirimi(str, WTFormEnum):
    """Proje Süresi birimlerini temsil eden enum class"""
    gun = "Gün"
    ay = "Ay"
    yil = "Yıl"


class ProjeBasvuruDurumu(str, WTFormEnum):
    """Proje Basvuru Durumunu temsil eden enum class"""
    tamamlandi = "Tamamlandi"
    revizyon_bekleniyor = "Revizyon Bekleniyor"
    taslak = "Taslak"


class GundemTipi(str, WTFormEnum):
    """Gündem tipini temsil eden enum class"""
    projenin_desteklenmesi = "Projenin Desteklenmesi"
    nitelik_gelistirme_ust_projesi = "Nitelik Geliştirme Üst Projesi"
    projenin_hakeme_gonderilmesi = "Projenin Hakeme Gönderilmesi"
    projenin_ara_raporunun_degerlendirilmesi = "Projenin Ara Raporunun Değerlendirilmesi"
    ara_raporunun_hakem_deg_birlikte_degerlendirilmesi = "Projenin Ara Raporunun Hakem Değerlendirmesiyle Birlikte Değerlendirilmesi"
    projenin_sonuc_raporunun_degerlendirilmesi = "Projenin Sonuç Raporunun Değerlendirilmesi"
    sonuc_raporunun_hakem_deg_birlikte_degerlendirilmesi = "Projenin Sonuç Raporunun Hakem Değerlendirmesiyle Birlikte Değerlendirilmesi"
    proje_yurutucu_degisikligi = "Proje Yürütücü Değişikliği"
    projenin_butce_kalemleri_arasinda_aktarim_yapilmasi = "Bütçe Kalemleri Arası Aktarım Yapılması"
    projeye_ek_sure_verilmesi = "Projeye Ek Süre Verilmesi"
    projeye_ek_malzeme_verilmesi = "Projeye Ek Malzeme Verilmesi"
    projeye_ek_butce_ve_ek_malzeme_verilmesi = "Projeye Ek Malzeme ve Bütçe Verilmesi"
    projeye_ek_odenek_verilmesi = "Projeye Ek Ödenek Verimesi"
    proje_baslik_degistirme_talebi = "Proje Başlığı Değiştirme Talebi"
    proje_turu_degistirme_talebi = "Proje Türü Değiştirme Talebi"
    projenin_kapatilmasi = "Projenin Kapatılması"
    projenin_iptal_edilmesi = "Projenin İptal Edilmesi"
    projeye_personel_ekleme_ve_cikarma = "Projeye Peronel Ekleme/Çıkarma Talebi"
    hizli_destek_butce_talebi = "Hızlı Destek Bütçe Talebi"
    proje_dondurma_talebi = "Proje Dondurma Talebi"
    proje_malzeme_degistirilmesi = "Proje Malzeme Değiştirilmesi"
    diger_taleplerin_gorusulmesi = "Diğer Talepler"
    avans_kredi_taleplerinin_gorulmesi = "Avans Kredi Talepleri"
    proje_yayin_degerlendirilmesi = "Proje Yayın Değerlendirilmesi"
    projenin_geri_cekilmesi_yururlukten_kaldirilmasi = "Projenin Geri Çekilmesi / Yürürlüktek Kaldırılması"
    genel = "Genel"


class GundemDurumu(str, WTFormEnum):
    degerlendirilmedi = "Değerlendirilmedi"
    atanmamis = "Atanmamış"


class KararDurumu(str, WTFormEnum):
    """Gündem Karar Durumunu temsil eden enum class"""
    kabul = "Kabul"
    ret = "Ret"
    degerlendirilmedi = "Değerlendirilmedi"
    revizyon = "Revizyon"


class ToplantiDurumu(str, WTFormEnum):
    """Gündem Karar Durumunu temsil eden enum class"""
    gerceklestirildi = "Gerçekleştirildi"
    gerceklestirilmedi = "Gerçekleştirilmedi"


class SablonKategori(str, WTFormEnum):
    """Gündem Karar Durumunu temsil eden enum class"""
    genel = "Genel"


PROJE_TURU_UYARI_MESAJ_TIPLERI = {
    "proje_yurutucusu_icin_yardim_mesaji",
    "basvuru_yapilmadan_gelecek_uyari",
    "basvuru_tamamlandiktan_sonra_bilgilendirme",
    "gonder_islemi_yapilirken_yurutucuye_gosterilecek_uyari",
    "ek_dosyalar_ekrani_bilgilendirme",
    "hakem_onerisi_bilgilendirme",
    "ara_rapor_uyari",
    "sonuc_raporu_uyari",
    "butce_ekrani_bilgilendirme",
    "personel_ekrani_bilgilendirme_mesaji",
    "degerlendirme_sonunda_bilgi_notu",
    "degerlendirme_ekraninda_bilgi_notu",
    "yurutucu_proje_sozlesme_bekleme_mesaji"
}

PROJE_BELGE_TURLERI = {
    "pdf",
    "odt"
}


class NotTipi(str, enum.Enum):
    """
    Yetkili tarafından oluşturulan notları temsil eden enum class.

    """
    proje_notu = "Projeye Özel Not"
    proje_yurutucu_notu = "Proje Yürütücüsüne Özel Not"


class OlcuBirimi(str, WTFormEnum):
    adet = 'Adet'
    gram = 'Gram'
    kg = 'Kg'
    kutu = 'Kutu'
    litre = 'Litre'
    mg = 'Miligram'
    ml = 'Mililitre'
    diger = 'Diğer'
