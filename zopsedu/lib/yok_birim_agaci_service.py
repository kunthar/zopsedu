from zeep import Client

from zopsedu.server import app
from zopsedu.lib.db import DB
from zopsedu.models import Birim


class YokBirimAgaciService(object):

    def __init__(self):
        self.service_url = "http://servisler.yok.gov.tr/ws/UniversiteBirimlerv4?WSDL"
        self.client = self.create_soap_client()

    def create_soap_client(self):
        client = Client(self.service_url)
        return client

    def birim_save_or_update(self, birim):
        """
        Servisten donen birim verisini modelde bekledigimiz sekilde formatlayip sessiona merge ederiz
        İlgili birim db de bulunuyor ise Update eder yok ise kaydeder
        :param birim:
        :return:
        """
        birim_data = self.data_format_mapper(birim)

        birim = Birim(**birim_data)

        DB.session.merge(birim)
        DB.session.commit()

    def data_format_mapper(self, data):
        """
        Servisden gelen birim verisini sistemde bulunan 'Birim' modeline kaydedilecek formata
        cevirir. Örnek data formati asagida gosterilmistir
        {
            'BIRIM_UZUN_ADI': 'ADIYAMAN ÜNİVERSİTESİ/KAHTA MESLEK YÜKSEKOKULU/OTEL, LOKANTA VE İKRAM HİZMETLERİ BÖLÜMÜ/AĞIRLAMA HİZMETLERİ PR./',
            'BIRIM_ADI_INGILIZCE': 'ENTERTAINMENT SERVICES PR.',
            'BAGLI_OLDUGU_BIRIM_ID': 151099,
            'OGRENIM_SURESI': 2,
            'KILAVUZ_KODU': None,
            'UNIVERSITE': { 'KOD': 100259, 'AD': 'ADIYAMAN ÜNİVERSİTESİ', 'ACIKLAMA': '-' },
            'FAKULTE_YO_MYO_ENSTITU': { 'KOD': 100453, 'AD': 'KAHTA MESLEK YÜKSEKOKULU', 'ACIKLAMA': '-' },
            'BIRIM': { 'KOD': 151102, 'AD': 'AĞIRLAMA HİZMETLERİ PR.', 'ACIKLAMA': '-' },
            'BIRIM_TURU': { 'KOD': 13, 'AD': 'Önlisans/Lisans Programı', 'ACIKLAMA': '-' },
            'UNIVERSITE_TURU': { 'KOD': 1, 'AD': 'DEVLET ÜNİVERSİTELERİ', 'ACIKLAMA': '-' },
            'AKTIFLIK': { 'KOD': 3, 'AD': 'Kapatılmış', 'ACIKLAMA': '-' },
            'OGRENIM_DILI': { 'KOD': 1, 'AD': 'Türkçe', 'ACIKLAMA': '-' },
            'OGRENIM_TURU': { 'KOD': 1, 'AD': 'BİRİNCİ ÖĞRETİM', 'ACIKLAMA': '-' },
            'IL': { 'KOD': 2, 'AD': 'ADIYAMAN', 'ACIKLAMA': '-' },
            'ILCE': { 'KOD': 1425, 'AD': 'KAHTA', 'ACIKLAMA': '-' },
            'KOD_BID': { 'KOD': 1729, 'AD': 'AĞIRLAMA HİZMETLERİ', 'ACIKLAMA': '-' }
        }
        :param data: OrderedDict
        :return: Dict
        """
        return {
            "id": data["BIRIM"]["KOD"],
            "ust_birim_id": data["BAGLI_OLDUGU_BIRIM_ID"],
            "universite_id": data["UNIVERSITE"]["KOD"],
            "fakulte_yo_myo_enstitu_id": data["FAKULTE_YO_MYO_ENSTITU"]["KOD"],
            "ad": data["BIRIM"]["AD"],
            "uzun_ad": data["BIRIM_UZUN_ADI"],
            "ingilizce_birim_adi": data["BIRIM_ADI_INGILIZCE"],
            "birim_tipi": data["BIRIM_TURU"]["AD"],
            "birim_tipi_kodu": data["BIRIM_TURU"]["KOD"],
            "ogrenim_dili": data["OGRENIM_DILI"]["AD"],
            "ogrenim_dili_kodu": data["OGRENIM_DILI"]["KOD"],
            "ogrenme_tipi": data["OGRENIM_TURU"]["AD"],
            "ogrenme_tipi_kodu": data["OGRENIM_TURU"]["KOD"],
            "universite_turu_kodu": data["UNIVERSITE_TURU"]["KOD"],
            "sehir_kodu": data["IL"]["KOD"],
            "sehir_adi": data["IL"]["AD"],
            "semt_kodu": data["ILCE"]["KOD"],
            "semt_adi": data["ILCE"]["AD"],
            "kod_bid_ad": data["KOD_BID"]["AD"],
            "kod_bid_kodu": data["KOD_BID"]["KOD"],
            "aktif_mi": True if data["AKTIFLIK"]["KOD"] == 1 else False,
            "aktiklif_kod": data["AKTIFLIK"]["KOD"],
            "ogrenim_suresi": data["OGRENIM_SURESI"],
            "kilavuz_kodu": data["KILAVUZ_KODU"],
        }

    def birim_getir(self, birim_id):
        """
        Verilen idli birim ile ilgili bilgileri getirir
        :param birim_id: ilgili birimin id si
        :return:
        """
        return self.client.service['IDdenBirimAdiGetirv4'](BIRIM_ID=birim_id)

    def universiteleri_getir(self):
        """
        Yok sisteminde tanimli universiteleri getirir
        :return:
        """
        return self.client.service["UniversiteleriGetirv4"]()

    def alt_birimleri_getir(self, birim_id):
        """
        Verilen id li birimin alt birimlerini getirir
        :param birim_id:
        :return:
        """
        return self.client.service["AltBirimleriGetirv4"](BIRIM_ID=birim_id)

    def alt_birimleri_kaydet(self, root_birim_id):
        """
        Root birim id paramesinde gelen girimin alt birimleri kaydeder. Recursive olarak calisir
        :param root_birim_id: alt birimleri getirilecek root birim
        :return:
        """
        alt_birimler = self.alt_birimleri_getir(root_birim_id)

        if alt_birimler:
            for birim in alt_birimler["BIRIMLER"]:
                if birim["BIRIM"]["KOD"]:
                    self.birim_save_or_update(birim)
                    self.alt_birimleri_kaydet(root_birim_id=birim["BIRIM"]["KOD"])
                else:
                    return True

        return False

    def id_ile_universite_kaydet(self, universite_birim_id):
        """
        Belirli bir universiyi ve universitenin alt birimlerini kaydetmek icin kullanilir
        :return:
        """
        universite_birim_data = self.birim_getir(universite_birim_id)
        self.birim_save_or_update(universite_birim_data["BIRIM"])
        self.alt_birimleri_kaydet(root_birim_id=universite_birim_id)
        print("{} UNIVERSITE VERISI BASARIYLA KAYDEDILDI. Kodu: {}".format(
            universite_birim_data["BIRIM"]["UNIVERSITE"]["AD"],
            universite_birim_data["BIRIM"]["UNIVERSITE"]["KOD"]))

    def butun_universite_birimlerini_kaydet(self, kayit_baslama_index=0):
        """
        Yoksiste bulunan butun universite ve alt birim  verilerini kaydeder
        Gelen universite verisi uzerinden universitenin birim versii getirilip kaydedilir.
        Daha sonra universiteye ait butun birimler "alt_birimleri_kaydet" methodu ile kaydedilir
        :param kayit_baslama_index: universiteler listesindeki hangi indexten devam edilecegini
            belirtir default olarak 0(butun universiteleri kaydetmek icin) dır
        :return:
        """
        universiteler = self.universiteleri_getir()
        if universiteler["SONUC"]["DurumAciklama"] == 'Başarılı':
            for index in range(kayit_baslama_index, len(universiteler["UNIVERSITELER"])):
                self.id_ile_universite_kaydet(universiteler["UNIVERSITELER"][index]["BIRIM_ID"])
                print(universiteler["UNIVERSITELER"][index])
            # for index, universite in enumerate(universiteler["UNIVERSITELER"]):
            #     self.id_ile_universite_kaydet(universite["BIRIM_ID"])
                # en son basarıyla kaydedilen universitenin universiteler listesindeki indexini
                # herhangi bir hatayla karsilasirsak kaldigimiz indexten devam etmek icin
                # kullaniyoruz
                print("SON KAYDEDILEN UNIVERSITENIN INDEXI: {}".format(index))

    def yok_verisi_kaydet(self, birim_id=0):
        """
        Yök butun universitelerin ust birimidir islemler baslamadan once yok un kaydedildiginden
        emin olmamis gerekir.
        :param birim_id: yok birim id si ( default 0)
        :return:
        """
        yok_birim_data = self.birim_getir(birim_id)
        self.birim_save_or_update(yok_birim_data["BIRIM"])

    def yoksis_birim_agaci_kaydet(self):
        with app.app_context():
            try:
                self.yok_verisi_kaydet()
                self.butun_universite_birimlerini_kaydet()
                print("ISLEM BASARIYLA TAMAMLANDI.")
            except Exception as exc:
                print("BIR HATA MEYDANA GELDİ. HATA: {}".format(exc))
                DB.session.rollback()
