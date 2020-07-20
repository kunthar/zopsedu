"""Helper Siniflari"""

import enum

from zopsedu.lib.helpers import WTFormEnum


class AkademikUnvan(str, WTFormEnum):
    """AkademikUnvan Enum Class ı"""
    profesor = "Profesör"
    docent = "Doçent"
    arastirma_gorevlisi = "Araştırma Görevlisi"
    ogretim_gorevlisi = "Öğretim Görevlisi"

class BapIdariUnvan(str, WTFormEnum):
    """Bap idari unvan Enum Class ı"""

    yk_baskan = "Yönetim Kurulu Başkanı"
    yk_uyesi = "Yönetim Kurulu Üyesi"
    raportor = "Raportör"
    bap_alt_komisyon_baskani = "Bap Alt Komisyon Başkanı"
    bap_alt_komisyon_uyesi = "Bap Alt Komisyon Üyesi"
    bap_koordinatoru = "Bap Koordinatörü"
    bap_idari_koordinatoru = "Bap İdari Koordinatör"
    bap_memuru = "Bap Memuru"



class PersonelEngellilik(str, enum.Enum):
    """Person medeni halini temsil eden enum class"""

    engelli_degil = "Engelli Değil"
    birinci_derece = "1. Derece %80-%100"
    ikinci_derece = "2. Derece %60-%79"
    ucuncu_derece = "3. Derece %40-%59"


class PersonelTuru(str, enum.Enum):
    """Person medeni halini temsil eden enum class"""

    akademik = "Akademik"
    idari = "İdari"
    yabanci_uyruklu = "Yabancı Uyruklu"
    gecici = "Geçici"


class PersonelStatu(str, enum.Enum):
    """Person medeni halini temsil eden enum class"""

    kadrolu = "Kadrolu"
    kadrosuz = "Kadrosuz"
    kismi = "Kısmi"
    madde_35 = "35.Madde"
    sozlesmeli = "Sözleşmeli"
    yedi_l = "7/L"
    bakanlik_personeli = "Bakanlık Personeli"


class HizmetSinifi(str, enum.Enum):
    """Person medeni halini temsil eden enum class"""
    genel_idari_hizmetleri = "Genel İdare Hizmetleri"
    mulki_idari_amirligi_hizmetleri = "Mülki İdare Amirliği Hizmetleri"
    saglik_hizmetleri = "Sağlık Hizmetleri"
    teknik_hizmetler = "Teknik Hizmetler"
    egitim_ogretim_hizmetleri = "Eğitim Öğretim Hizmetleri"
    avukatlik_hizmetleri = "Avukatlık Hizmetleri"
    emniyet_hizmetleri = "Emniyet Hizmetleri"
    din_hizmetleri = "Din Hizmetleri"
    yardimci_hizmetler = "Yardımcı Hizmetler"
    milli_istihbarat_teskilati = "Milli İstihbarat Teşkilatı"
    askeri_hakim_ve_savcilar = "Askeri Hakim Ve Savcılar"
    belediye_baskani = "Belediye Başkanı"
    cumhurbaskani = "Cumhurbaşkanı"
    cumhurbaskanligi_personeli = "Cumhurbaşkanlığı Personeli"
    denetim_elemanlari = "Denetim Elemanları"
    devlet_sanatcilari = "Devlet Sanatçıları"
    hakim_ve_savcilar = "Hakim Ve Savcılar"
    merkez_bankasi = "Merkez Bankası"
    milletvekili = "Milletvekili"
    ogretim_uyeleri = "Öğretim Üyeleri"
    sayistay_uyeleri_ve_meslek_mensuplari = "Sayıştay Üyeleri Ve Meslek Mensupları"
    tbmm_personeli = "Türkiye Büyük Millet Meclisi Personeli"
    turkiye_radyo_televizyon_kurumu = "Türkiye Radyo Televizyon Kurumu"
    turk_silahli_kuvvetleri = "Türk Silahlı Kuvvetleri"
    yardimci_saglik_hizmetleri = "Yardımcı Sağlık Hizmetleri"
    ogretim_gorevlileri_ve_okutmanlari = "Öğretim Görevlileri Ve Okutmanlar"
    ogretim_yardimcilari = "Öğretim Yardımcıları"
    sozlezmeli_personel = "Sözleşmeli Personel"


class AppStates(str, enum.Enum):
    """
    Uygulama içerisinde iş akışının durumlarını temsil eden enum class.

    """
    basvuru_kabul = "Başvuru / Kabul"
    devam = "Sürmekte Olan"
    son = "Sonlanmış"


class JobTypes(str, enum.Enum):
    """
    Uygulama içerisinde oluşan işleri temsil eden enum class.

    """
    sms = "Sms"
    email = "Eposta"
    project_state_change = "Proje Durum Değişimi"
    project_action = "Proje İşlemi"
    satinalma_state_change= "Satınalma Durum Değişimi"
    satinalma_action = "Satınalma İşlemi"


class StateTypes(str, enum.Enum):
    """
    Uygulama içerisinde oluşan işleri temsil eden enum class.

    """
    proje = "Proje"
    satinalma= "Satınalma"
    yolluk = "Yolluk"


class ActionTypes(str,enum.Enum):
    proje = "Proje"
    satinalma = "Satınalma"
    yolluk = "Yolluk"


class BirimTipiEnum(enum.Enum):
    """
    Uygulama içerisinde kullanılan birimleri temsil eden enum class.

    """

    fakulte = "Fakülte"
    ana_bilim_dali = "Anabilim Dalı"
    bolum = "Bölüm"
    universite = "Üniversite"
    bilim_dali = "Bilim Dalı"


class SiparisDurumu(enum.Enum):
    """
    Uygulama içerisinde kullanılan sipariş takibini temsil eden enum class.

    """
    firma_bekleniyor = "Firma Bekleniyor"
    teslim_alindi = "Teslim Alındı"
    muayeneye_gonderildi = "Muayene Komisyonuna Gönderildi"
    muayene_onayladi = "Muayene Komisyonu Onayladı"
    muayene_reddetti = "Muayene Komisyonu Reddetti"
    fatura_teslim_alindi = "Firma Faturası Teslim Alındı"
    siparis_tamamlandi = "Sipariş Tamamlandı"
    siparis_iptal_edildi = "Sipariş İptal Edildi"
