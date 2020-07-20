""" Proje turu ve bağlantılı modellerininden oluşur"""
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum, Numeric, Date, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates, relationship
from flask_babel import lazy_gettext as _

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.custom_types import JSONEncodedDict
from zopsedu.bap.models.helpers import ProjeTuruKategorisi, EkTalepTipi, ProjeTipi, \
    ProjeSuresiBirimi
from zopsedu.bap.models.helpers import YardimciArastirmaciSecenekleri
from zopsedu.bap.models.helpers import GorunurlukSecenekleri, ButceTercihleri
from zopsedu.bap.models.helpers import PROJE_TURU_UYARI_MESAJ_TIPLERI
from zopsedu.models.exceptions import ZopseduModelValueError


# pylint: disable=too-few-public-methods
class ProjeTuru(BASE_MODEL, ZopseduBase):
    """
    Proje türü modeli. Proje türü için gerekli alanları içeren bir data modelidir
    tur_kodu: proje turu kodu
    guncel_mi: versiyonlamak için kullanılacak alan. bir instance yaratıldıgında degeri "true" dur.
               veritabanı kaydı guncellenmek istendiginde eldeki verilerle yeni bir instance
               oluşturulur.

    ad: proje türü adı
    kategori: proje türü kategorisi
    basvuru_baslama_tarihi: başvuru başlama tarihi
    basvuru_bitis_tarihi: başvuru bitis tarihi

    hakem_önerilsin_mi: basvuru hakem öneri şartı

    basvuru_hakem_oneri_sayisi: basvuru hakem oneri sayisi alanı en az şu kadar hakem öner olursa
                                kullanıcıdan deger alınması gerekiyor.

    hakem_degerlendirmesi_gerekli_mi:

    sure_alt_limiti: proje süresi alt limiti(ay cinsinden).
    sure_ust_limiti: proje süresi üst limiti(ay cinsinden)

    ek_sure_talep_tipi: EkTalepTipi enum sınıfı alanlarından biri olmalıdır.
    ek_sure_talep_degeri: ek süre talep tipi "en fazla" veya "yuzde" olursa bir değer girilmelidir.
                          eger "yuzde" secilirse bu alanın değeri en fazla 100 olabilir
    ek_sureler_proje_sure_limitine_dahil_mi:

    proje_tipi: ProjeTipi enum sınıfı alanlarından bir değer olmalıdır
    oneri_formu: Oneri formu, birden cok secenek icinden secilir. Aslinda bir form degil,
                 basvurunun gerceklesecegi anda basvurucudan istenecek bilgilerin belirlendiri
                 bir form wizard seklinde onceden hazirlanir. Bu secenekte proje turu icin gecerli
                 form wizard secilmis olur.

    hakem_degerlendirme_formu: hakem degerlendirme formu (on tanimli form wizardlardan secimli)

    bilim_kurulu_degerlendirme_formu: bilim kurulu değerlendirme formu
                                      (on tanimli form wizardlardan secimli)

    raportor_formu: Roportor Form (on tanimli form wizardlardan secimli.)

    hakem_ara_rapor_formu: Hakem Ara Rapor Formu (on tanimli form wizardlardan secimli)
    hakem_sonuc_rapor_formu: Hakem sonuc raporu formu (on tanimli form wizardlardan secimli)

    komisyon_butce_degerlendirme_formu: Komisyon Butce Degerlendirme Formu
                                        (on tanimli form wizardlardan secimli)

    basvuru_aktif_mi: bu alan başvurunun aktif olup olmadığını belirler.
    proje_ek_talepleri_icin_rapor_kontrolu_yapilacak_mi
    herkese_acik_proje_listesinde_yer_alacak_mi

    ara_rapor_gerekli_mi:
    sonuc_raporu_gerekli_mi:
    ara_sonuc_raporu_dosya: ara sonuc raporu gerekli ise rapor dosyası alınmalı
    sonuc_raporu_dosya: sonuc raporu gerekli ise rapor için dosya alınmalı

    proje_yurutucusu_ek_dosyalar_ekleyebilir_mi:
    is_zaman_plani_otomasyon_icerisinde_doldurulsun_mu:
    ek_dosya_yuklenebilir_mi:

    genel_uyari_mesajlari : projeye ilişkin kullanıcı karşısına cıkarılacak bütün uyarı mesajlari
                            bu alanda(JSON) tutulur
    """
    __tablename__ = "proje_turu"

    id = Column(Integer, primary_key=True)

    # Tur Kodu (projeler numaralandirilirken kullanilacak, yil-tur_kodu-fakulte_kodu-sira_no)
    tur_kodu = Column(Integer, nullable=False)
    guncel_mi = Column(Boolean, default=True)

    ad = Column(String(255))
    kategori = Column(Enum(ProjeTuruKategorisi))
    gelir_kasasi_id = Column(Integer, ForeignKey("gelir_kasalari.id"))

    basvuru_baslama_tarihi = Column(Date)
    basvuru_bitis_tarihi = Column(Date)

    proje_turu_aciklama = Column(Text)

    # basvuru hakem oneri sarti ve sayisi
    hakem_onerilsin_mi = Column(Boolean)
    basvuru_hakem_oneri_sayisi = Column(Integer, default=0)
    hakem_degerlendirmesi_gerekli_mi = Column(Boolean)

    # proje süre limitleri
    sure_alt_limiti = Column(Integer)
    sure_ust_limiti = Column(Integer)
    sure_birimi = Column(Enum(ProjeSuresiBirimi), default=ProjeSuresiBirimi.ay.name)
    # ek süre ile ilgili alanlar
    ek_sure_talep_tipi = Column(Enum(EkTalepTipi))
    ek_sure_talep_degeri = Column(Integer)
    ek_sureler_proje_sure_limitine_dahil_mi = Column(Boolean, default=False)

    # Proje tipi yuksek lisans / doktora (uzmanlik) veya belirtilmemis
    proje_tipi = Column(Enum(ProjeTipi))

    # proje türü için gerekli formlar
    oneri_sablon_id = Column(Integer, ForeignKey("sablons.id"))
    hakem_degerlendirme_sablon_id = Column(Integer, ForeignKey("sablons.id"))
    hakem_ara_rapor_sablon_id = Column(Integer, ForeignKey("sablons.id"))
    hakem_sonuc_rapor_sablon_id = Column(Integer, ForeignKey("sablons.id"))
    ara_rapor_sablon_id = Column(Integer, ForeignKey("sablons.id"))
    sonuc_raporu_sablon_id = Column(Integer, ForeignKey("sablons.id"))
    sozlesme_sablon_id = Column(Integer, ForeignKey("sablons.id"))

    # diger alanlardan bagımsız boolean fieldlar
    basvuru_aktif_mi = Column(Boolean)
    proje_ek_talepleri_icin_rapor_kontrolu_yapilacak_mi = Column(Boolean, default=True)
    herkese_acik_proje_listesinde_yer_alacak_mi = Column(Boolean, default=True)

    # Hangi raporlar gerekli? Sadece sonuc, ara ve sonuc, ikisi de gerekli degil
    ara_rapor_gerekli_mi = Column(Boolean, default=False)
    sonuc_raporu_gerekli_mi = Column(Boolean, default=True)
    # ara_sonuc_raporu_dosya_id = Column(Integer, ForeignKey("file.id"))
    # sonuc_raporu_dosya_id = Column(Integer, ForeignKey("file.id"))
    rapor_araligi_suresi = Column(Integer, default=0)
    rapor_araligi_birimi = Column(Enum(ProjeSuresiBirimi),
                                  default=ProjeSuresiBirimi.ay.name)
    sonuc_raporu_icin_ek_sure = Column(Integer, default=0)
    sonuc_raporu_icin_ek_sure_birimi = Column(Enum(ProjeSuresiBirimi),
                                              default=ProjeSuresiBirimi.ay.name)
    rapor_gecikme_mail_suresi = Column(Integer, default=0)
    rapor_gecikme_mail_suresi_birimi = Column(Enum(ProjeSuresiBirimi),
                                              default=ProjeSuresiBirimi.ay.name)
    rapor_gecikmelerinde_satinalma_yapabilecek_mi = Column(Boolean, default=False)
    rapor_gecikmelerinde_yolluk_talebi_yapabilecek_mi = Column(Boolean, default=False)
    rapor_gecikmelerinde_ek_talep_yapabilecek_mi = Column(Boolean, default=False)
    sonuc_raporu_sonrasi_islem_yapilsin_mi = Column(Boolean, default=False)

    # ek dosya ayarları
    proje_yurutucusu_ek_dosyalar_ekleyebilir_mi = Column(Boolean)
    is_zaman_plani_otomasyon_icerisinde_doldurulsun_mu = Column(Boolean)
    ek_dosya_yuklenebilir_mi = Column(Boolean)
    # sadece  yuksek lisan ve doktora/uzmanlık projeleri icin
    proje_mali_destek_suresi = Column(Integer)
    mali_destek_suresi_birimi = Column(Enum(ProjeSuresiBirimi), default=ProjeSuresiBirimi.ay.name)

    # butce tercihi
    butce_tercihi = Column(Enum(ButceTercihleri))

    genel_uyari_mesajlari = Column(JSONEncodedDict)

    butce = relationship("Butce", uselist=False, cascade="save-update, delete")
    personel_ayarlari = relationship("PersonelAyarlari", uselist=False,
                                     cascade="save-update, delete")
    cikti = relationship("Cikti", cascade="save-update, delete, delete-orphan")
    ek_dosyalar = relationship("EkDosya", cascade="save-update, delete, delete-orphan")

    # ara_rapor = relationship("File", foreign_keys=[sonuc_raporu_dosya_id])
    # sonuc_raporu = relationship("File", foreign_keys=[ara_sonuc_raporu_dosya_id])

    butce_kalemleri = relationship("ButceKalemi")

    # pylint: disable=unused-argument
    @validates('ek_sure_talep_degeri')
    def ek_sure_degeri_control(self, field_key, field_value):
        """
        Eğer ek süre talep tipi yüzde olarak seçilmişse ek süre değeri alanının değeri en
        fazla 100 olabilir
        :param field_key: alan ismi
        :param field_value: alan değeri
        :return:
        """
        if self.ek_sure_talep_tipi == EkTalepTipi.yuzde.name:
            if not field_value:
                raise ZopseduModelValueError(
                    _("Ek süre talep değeri alanı boş bırakılamaz"), field_name=field_key)
            elif field_value > 100:
                raise ZopseduModelValueError(
                    _("Ek süre talep tipi yüzde olduğu için ek süre"
                      " talep degeri 100 den büyük olamaz"), field_name=field_key)
        elif self.ek_sure_talep_tipi == EkTalepTipi.en_fazla.name:
            if not field_value or field_value == 0:
                raise ZopseduModelValueError(
                    _("Ek süre talep değeri 0 dan büyük bir değer olmalıdır."),
                    field_name=field_key)
        return field_value

    @staticmethod
    @validates("genel_uyari_mesajlari")
    def uyari_mesaji_icerik_kontrolu(field_name, field_value):
        """
        Uyari mesajlari içerisinde belirli değerler olması gerekiyor. Bu değerler helper dosyasında
        "PROJE_TURU_UYARI_MESAJ_TIPLERI" sabitinde belirtilmiştir.
        :param field_name: "genel_uayri_mesajlari"
        :param field_value: JSON dict
        :return: value
        """
        # pylint: disable=unused-argument
        for key, _ in field_value.items():
            if key not in PROJE_TURU_UYARI_MESAJ_TIPLERI:
                raise ZopseduModelValueError(_("{} alani uyari mesajlari icerisinde yoktur."
                                               " Lütfen kontrol ediniz.").format(key),
                                             field_name=field_name)
        return field_value

    @validates("basvuru_hakem_oneri_sayisi")
    def hakem_oneri_sayisi_kontrolu(self, field_name, field_value):
        """Hakem önerilsin seçeneği işaretlendiyse bu alanın değeri sıfırdan büyük olmalıdır"""
        if self.hakem_onerilsin_mi and (not field_value or field_value) == 0:
            raise ZopseduModelValueError(
                _("Hakem önerilsin şeçeneği işaretlendiği için hakem "
                  "öneri sayısı girmeniz gerekmektedir."), field_name=field_name)
        return field_value

    @validates("basvuru_bitis_tarihi")
    def basvuru_bitis_tarihi_kontrolu(self, field_name, field_value):
        """Başvuru bitiş tarihini kontrol eder.Başvuru başlama tarihinden önceki bir tarih olamaz"""
        if not self.basvuru_baslama_tarihi:
            return field_value
        if self.basvuru_baslama_tarihi >= field_value:
            raise ZopseduModelValueError(
                _("Başvuru Bitiş Tarihi, Başvuru başlama tarihinden önceki bir tarih olmaz"),
                field_name=field_name)
        return field_value

    @validates("basvuru_baslama_tarihi")
    def basvuru_baslama_tarihi_kontrolu(self, field_name, field_value):
        """Başvuru başlama tarihini kontrol eder."""
        if not self.basvuru_bitis_tarihi:
            return field_value
        if field_value >= self.basvuru_bitis_tarihi:
            raise ZopseduModelValueError(
                _("Başvuru Bitiş Tarihi, Başvuru başlama tarihinden önceki bir tarih olmaz"),
                field_name=field_name)
        if field_value < datetime.today().date():
            raise ZopseduModelValueError(
                _("Başvuru başlama tarihi bugünden önceki bir tarih olamaz"),
                field_name=field_name)
        return field_value

    @validates("sure_ust_limiti")
    def sure_ust_limiti_kontrolu(self, field_name, field_value):
        """Süre üst limitini konrol eder."""
        if not self.sure_alt_limiti:
            return field_value
        if self.sure_alt_limiti >= field_value:
            raise ZopseduModelValueError(
                _("Proje süre alt limiti değeri üst limit değerine eşit veya büyük olamaz."),
                field_name=field_name)
        return field_value

    @validates("sure_alt_limiti")
    def sure_alt_limiti_kontrolu(self, field_name, field_value):
        """Süre üst limitini konrol eder."""
        if not self.sure_ust_limiti:
            return field_value
        if self.sure_ust_limiti <= field_value:
            raise ZopseduModelValueError(
                _("Proje süre alt limiti değeri üst limit değerine eşit veya büyük olamaz."),
                field_name=field_name)
        return field_value

    @validates("ara_sonuc_raporu_dosya_id")
    def ara_sonuc_rapor_kontrolu(self, field_name, field_value):
        """

        ara_sonuc_raporu_gerekli?mi alan değeri True ise ara_sonuc_raporu_dosya_id alanı boş olamaz
        (Dosya yüklenmesi gerekir)
        Args:
            field_name: "ara_sonuc_raporu_dosya_id"
            field_value: "ara_sonuc_raporu_dosya_id" alan değeri

        Returns: field_value

        """
        if self.ara_rapor_gerekli_mi and not field_value:
            raise ZopseduModelValueError(
                _("Lütfen Dosya Yükleyiniz"), field_name=field_name)
        return field_value

    @validates("sonuc_raporu_dosya_id")
    def sonuc_rapor_kontrolu(self, field_name, field_value):
        """
        sonuc_raporu_gerekli_mi alan değeri True ise sonuc_raporu_dosya_id alanı boş olamaz
        (Dosya yüklenmesi gerekir)
        Args:
            field_name: "sonuc_raporu_dosya_id"
            field_value: "sonuc_raporu_dosya_id" alan değeri

        Returns: field_value

        """
        if self.sonuc_raporu_gerekli_mi and not field_value:
            raise ZopseduModelValueError(
                _("Lütfen Dosya Yükleyiniz"), field_name=field_name)
        return field_value
        # pylint: enable=unused-argument


# pylint: disable=too-few-public-methods
class Butce(BASE_MODEL, ZopseduBase):
    """
    Proje türü bütce alanları için gerekli olan alanları içerir

    butce_alt_limiti: butce alt limiti
    butce_ust_limiti: butce ust limiti

    ek_butce_talep_tipi: TalepTipi enum classı değerlerinden biri olabilir

    ek_butce_talep_degeri: ek butce talep tipi "en fazla" veya "yuzde" olursa bir değer
                           girilmelidir. eger "yuzde" secilirse bu alanın değeri en fazla
                           100 olabilir
    ek_butce_proje_butce_limitine_dahil_mi:

    kalemlere_ait_butce_yillara_gore_verilebilecek_mi:

    kalemlere_ait_kdv_girilsin_mi:
    kalemlere_ait_butce_kodlari_girilsin_mi:

    butce_kalemleri: butce ile iliştilendirilmiş butce kalemleri

    """
    __tablename__ = "butce"

    id = Column(Integer, primary_key=True)
    proje_turu_id = Column(Integer, ForeignKey("proje_turu.id"))

    # proje butce limitleri
    butce_alt_limiti = Column(Numeric(14, 2))
    butce_ust_limiti = Column(Numeric(14, 2))
    # ek butce ile ilgili alanlar
    ek_butce_talep_tipi = Column(Enum(EkTalepTipi))
    ek_butce_talep_degeri = Column(Integer)
    ek_butce_proje_butce_limitine_dahil_mi = Column(Boolean, default=False)

    kalemlere_ait_butce_yillara_gore_verilebilecek_mi = Column(Boolean, default=True)

    kalemlere_ait_kdv_girilsin_mi = Column(Boolean, default=False)
    kalemlere_ait_butce_kodlari_girilsin_mi = Column(Boolean)

    proje_turu = relationship("ProjeTuru")

    # pylint: disable=unused-argument
    @validates('ek_butce_talep_degeri')
    def ek_butce_degeri_control(self, key, value):
        """
        Eğer ek butce talep tipi yüzde olarak seçilmişse ek süre değeri alanının değeri en
        fazla 100 olabilir
        :param key: alan ismi
        :param value: alan değeri
        :return:
        """
        if self.ek_butce_talep_tipi == EkTalepTipi.yuzde.name:
            if not value:
                raise ZopseduModelValueError(
                    _("Ek bütçe talep değeri alanı boş bırakılamaz"), field_name=key)
            elif value > 100:
                raise ZopseduModelValueError(
                    _("Ek bütce talep tipi yüzde seçildiği için ek butce talep"
                      " degeri 100 den büyük olamaz"), field_name=key)
        elif self.ek_butce_talep_tipi == EkTalepTipi.en_fazla.name:
            if not value or value == 0:
                raise ZopseduModelValueError(
                    _("Ek bütçe talep değeri 0 dan büyük bir değer olmalıdır."), field_name=key)
        return value

    @validates("butce_ust_limiti")
    def butce_ust_limiti_kontrolu(self, field_name, field_value):
        """Bütce üst limitini kontrol eder. Alt limittinde büyük olmalıdır."""
        if self.butce_alt_limiti >= field_value:
            raise ZopseduModelValueError(
                _("Proje bütçe alt limiti değeri üst limit değerine eşit veya büyük olamaz."),
                field_name=field_name)
        return field_value


# pylint: disable=too-few-public-methods
class PersonelAyarlari(BASE_MODEL, ZopseduBase):
    """
    Proje türü personel ayarlari için gerekli olan alanları içerir
    proje_turu: baglantılı proje turu

    yardimci_arastirmaci_secenekleri:
         YardimciArastirmaciSecenekleri enum alanı degerlerinden biri olmalıdır.
         "sadece_proje_yurutucusu" veya "sadece_danisman_ve_tez_ogrencisi" seceneklerinden birisi
         secilirse yardimci arastirmaci alt ve ust limiti alanları önemsiz olmalıdır.

    yardimci_arastirmaci_alt_limiti: eger yardimci_arastirmaci_secenekleri alan
                                     degeri "sinirli" ise alt limit girilmelidir

    yardimci_arastirmaci_ust_limiti: eger yardimci_arastirmaci_secenekleri alan
                                     degeri "sinirli" ise ust limit girilmelidir

    ozgecmis_yuklenmesi_zorunlu_mu:
    dosya_olarak_ozgecmis_yuklenebilir_mi:
    banka_bilgilerini_girmek_zorunlu_mu:



    """
    __tablename__ = "proje_turu_personel_ayarlari"

    id = Column(Integer, primary_key=True)
    proje_turu_id = Column(Integer, ForeignKey("proje_turu.id"))

    yardimci_arastirmaci_secenekleri = Column(Enum(YardimciArastirmaciSecenekleri))
    yardimci_arastirmaci_alt_limiti = Column(Integer, default=0)
    yardimci_arastirmaci_ust_limiti = Column(Integer, default=0)

    ozgecmis_yuklenmesi_zorunlu_mu = Column(Boolean)
    dosya_olarak_ozgecmis_yuklenebilir_mi = Column(Boolean)
    banka_bilgilerini_girmek_zorunlu_mu = Column(Boolean)

    proje_turu = relationship("ProjeTuru")

    # pylint: disable=invalid-name
    # pylint: disable=unused-argument
    @validates("yardimci_arastirmaci_ust_limiti")
    def yardimci_arastirmaci_ust_limit_kontrolu(self, field_name, field_value):
        """Yardimci araştirmaci üst limitini kontrol eder."""
        if self.yardimci_arastirmaci_secenekleri == YardimciArastirmaciSecenekleri.sinirli.name:
            if self.yardimci_arastirmaci_alt_limiti > field_value:
                raise ZopseduModelValueError(
                    _("Yardımcı Araştırmacı Alt Limiti Üst Limitten Büyük Olamaz"),
                    field_name=field_name)
        return field_value

    # @validates("yardimci_arastirmaci_alt_limiti")
    # def yardimci_arastirmaci_alt_limit_kontrolu(self, _, field_value):
    #     """Yardimci araştırmacı alt limitini kontrol eder."""
    #     if self.yardimci_arastirmaci_secenekleri != YardimciArastirmaciSecenekleri.sinirli.name:
    #         field_value = 0
    #     return field_value
    #     # pylint: enable=invalid-name


# pylint: disable=too-few-public-methods
class Cikti(BASE_MODEL, ZopseduBase):
    """
    Proje türü ile baglantılı cikti modeli.
    Proje turu modeliyle cikti modeli one-to-many ilişkisine sahiptir.

    proje_turu: baglantılı proje_turu.
    cikti_turu: cikti turu form modeli ile baglantılıdır.
                cikti olarak hangi formdan yararlanılacagını gosterir.

    adi: cikti adi
    gorunurluk: Ciktinin kimler tarafından gorulebilecegini belirler.
    belge_ciktisi_alinacak_mi: belgenin cıktısının alınıp alınmayacagını belirleyen alan.
    """
    __tablename__ = "proje_cikti"
    id = Column(Integer, primary_key=True)
    proje_turu_id = Column(Integer, ForeignKey("proje_turu.id"))
    sablon_id = Column(Integer, ForeignKey("sablons.id"))

    adi = Column(String(255))
    gorunurluk = Column(Enum(GorunurlukSecenekleri))
    belge_ciktisi_alinacak_mi = Column(Boolean)

    proje_turu = relationship("ProjeTuru")
    sablon_belge = relationship("Sablon", lazy="joined")


class EkDosya(BASE_MODEL, ZopseduBase):
    """
    Proje türü ile bağlantılı dosya modeli

    zorunlu_mu:
    proje_icerik_dosyasi_mi:
    belgenin_ciktisi_alinacak_mi:

    """
    __tablename__ = "dosya"

    id = Column(Integer, primary_key=True)
    proje_turu_id = Column(Integer, ForeignKey("proje_turu.id"))
    dosya_id = Column(Integer, ForeignKey("bap_belge.id"))

    zorunlu_mu = Column(Boolean)
    proje_icerik_dosyasi_mi = Column(Boolean)
    belgenin_ciktisi_alinacak_mi = Column(Boolean)

    belge = relationship("BAPBelge", uselist=False, cascade="save-update, delete")

    proje_turu = relationship("ProjeTuru")


class ButceKalemi(BASE_MODEL, ZopseduBase):
    """
    Butce kalemleri modeli
    """
    __tablename__ = "butce_kalemi"

    id = Column(Integer, primary_key=True)
    proje_turu_id = Column(Integer, ForeignKey("proje_turu.id"))
    gider_siniflandirma_id = Column(Integer, ForeignKey("gider_siniflandirma.id"))

    butce_alt_limiti = Column(Numeric(14, 2), default=0.0)
    butce_ust_limiti = Column(Numeric(14, 2))

    gider_siniflandirma_kalemi = relationship("GiderSiniflandirma", lazy="joined")

    __table_args__ = (
        UniqueConstraint('proje_turu_id', 'gider_siniflandirma_id', name='proje_turu_butce_kalemi'),
    )


class SabitButceKalemi(BASE_MODEL, ZopseduBase):
    """
    Sabit butce kalemi modeli.

    adi: butce kaleminin adı. örn: Hizmet Alımı
    analitik_kodu: butce kalemi analitik kodu. örn: 03.05
    """
    __tablename__ = "sabit_butce_kalemi"

    id = Column(Integer, primary_key=True)

    adi = Column(String(255))
    analitik_kodu = Column(String(50))
