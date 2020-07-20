"""Proje detay modeli"""
import enum

from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, String, Boolean, Enum, \
    UniqueConstraint, DateTime
from sqlalchemy.orm import validates, relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.custom_types import JSONEncodedDict
from zopsedu.bap.models.helpers import ProjeDegerlendirmeSonuc


class ProjeDetay(BASE_MODEL, ZopseduBase):
    """
    Proje detay modeli
    """
    __tablename__ = "proje_detay"

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey('proje.id'), unique=True)

    butce_fazlaligi = Column(Numeric(12, 2), default=0.00)
    konu_ve_kapsam = Column(Text)
    literatur_ozeti = Column(Text)
    ozgun_deger = Column(Text)
    hedef_ve_amac = Column(Text)
    yontem = Column(Text)
    basari_olcutleri = Column(Text)
    b_plani = Column(Text)

    universite_disi_uzmanlar = Column(JSONEncodedDict)
    universite_disi_destekler = Column(JSONEncodedDict)
    arastirma_olanaklari = Column(Text)

    @staticmethod
    @validates('konu_ve_kapsam', 'literatur_ozeti', 'ozgun_deger', 'hedef_ve_amac', 'yontem',
               'basari_olcutleri', 'b_plani')
    def min_value_validator(key, value):
        """
        validates içerisinde belirtilen string alanlar en az 650 karakter içermelidir
        :param key: alan ismi
        :param value: alan değeri
        :return:
        """
        # pylint: disable=unused-argument
        if len(value) < 650:
            raise ValueError("Alan uzunluğu en az 650 karakter olmalıdır!")


class ProjeBelgeleri(BASE_MODEL, ZopseduBase):
    """Proje belgelerinin tutulduğu modeldir."""

    __tablename__ = "proje_belgeleri"

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey('proje.id'))
    belge_id = Column(Integer, ForeignKey('file.id'))
    proje_turu_ek_dosya_id = Column(Integer, ForeignKey("dosya.id"))
    baslik = Column(String(59))
    aciklama = Column(Text)

    belge = relationship("File")


class ProjeCalisanlari(BASE_MODEL, ZopseduBase):
    """
    Proje çalışanlarının tutulduğu modeldir.

    Proje çalışanı kurum personeli olabildiği gibi, kurum dışı harici bir kişi olabilir.
    Kurum personeli ise personel_id fieldi kullanılarak ilişkili tablo ile bağlantı sağlanılır.
    Kurum dışı bir kişi ise person_id fieldi kullanılarak ilişkili tablo ile bağlantı sağlanılır
    """

    __tablename__ = "proje_calisanlari"
    __table_args__ = (
        UniqueConstraint('proje_id', 'personel_id', name='proje_calisan_personel_uc'),
        UniqueConstraint('proje_id', 'ogrenci_id', name='proje_calisan_ogrenci_uc'),
    )
    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey('proje.id'))
    personel_id = Column(Integer, ForeignKey('personel.id'), nullable=True)
    ogrenci_id = Column(Integer, ForeignKey('ogrenci.id'), nullable=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    hitap_unvan_id = Column(Integer, ForeignKey('hitap_unvan.id'))
    fakulte_id = Column(Integer, ForeignKey('birim.id'))
    bolum_id = Column(Integer, ForeignKey('birim.id'))
    ozgecmis_id = Column(Integer, ForeignKey("ozgecmis.id"))

    is_telefonu = Column(String(16))
    projedeki_gorevi = Column(String(50))
    projeye_katkisi = Column(Numeric(12, 2))
    projeye_bilimsel_katkisi = Column(String(255))
    yonetici_yetkisi_varmi = Column(Boolean())

    universite_disindan_mi = Column(Boolean)
    # iban numarası en fazla 32 haneli olabiliyor(dünya genelinde)
    banka_bilgisi = Column(String(32))

    ogrenci = relationship("Ogrenci", lazy="joined")
    personel = relationship("Personel", lazy="joined")
    person = relationship("Person", lazy="joined")
    hitap_unvan = relationship("HitapUnvan", uselist=False)
    fakulte = relationship("Birim", foreign_keys=[fakulte_id], uselist=False)
    bolum = relationship("Birim", foreign_keys=[bolum_id], uselist=False)
    ozgecmis = relationship("Ozgecmis", cascade="save-update, delete", lazy='joined')


class ProjeHakemDavetDurumlari(str, enum.Enum):
    """
    ProjeHakemDavetDurumlari
    """
    gonderildi = "Hakemlik Daveti Gönderildi"
    kabul_edildi = "Hakemlik Daveti Kabul Edildi"
    reddedildi = "Hakemlik Daveti Reddedildi"
    cikarildi = "Proje Hakemleri Arasından Çıkarıldı"


class DegerlendirmeTipi(str, enum.Enum):
    """
    Degerlendirme tipleri
    """
    ara_rapor = "Ara Rapor"
    sonuc_raporu = "Sonuc Raporu"
    proje_basvuru = "Proje Başvuru"


class ProjeHakemleri(BASE_MODEL, ZopseduBase):
    """
    Projeye atanan hakemlerin tutuldugu modeldir
    """

    __tablename__ = 'proje_hakem'
    __table_args__ = (
        UniqueConstraint('proje_id', 'hakem_id', name='proje_hakem_uc'),
    )

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey('proje.id'))
    hakem_id = Column(Integer, ForeignKey('hakem.id'))

    # default deger degistirilmemelidir.
    # degistirildigi taktirde viewlardaki logicler duzeltilmelidir.
    davet_durumu = Column(Enum(ProjeHakemDavetDurumlari),
                          default=ProjeHakemDavetDurumlari.gonderildi)

    tamamlanan_proje_degerlendirmeleri = relationship(
        "ProjeDegerlendirmeleri",
        primaryjoin="and_(ProjeDegerlendirmeleri.proje_hakem_id==ProjeHakemleri.id,"
                    "and_(ProjeDegerlendirmeleri.degerlendirme_sonuclandi_mi==True))",
        lazy="joined")
    hakem = relationship("Hakem", lazy="joined")
    proje = relationship("Proje")


class ProjeDegerlendirmeleri(BASE_MODEL, ZopseduBase):
    """
    Proje değerlendirmelerinin tutulduğu modeldir.
    Proje degerlendirmesi ara, sonuc raporu olabildigi gibi herhangi bir raporla baglantili olmayan
    (proje başvurusu degerlendirme gibi) bir degerlendirmede olabilir
    """

    __tablename__ = 'proje_degerlendirmeleri'

    id = Column(Integer, primary_key=True)
    proje_hakem_id = Column(Integer, ForeignKey('proje_hakem.id'))
    rapor_id = Column(Integer, ForeignKey('proje_rapor.id'))
    ek_dosya_id = Column(Integer, ForeignKey('file.id'))

    degerlendirme = Column(Text)

    degerlendirme_gonderim_tarihi = Column(DateTime())
    degerlendirme_sonuclandi_mi = Column(Boolean, default=False)
    degerlendirme_incelendi_mi = Column(Boolean, default=False)

    sonuc = Column(Enum(ProjeDegerlendirmeSonuc), default=ProjeDegerlendirmeSonuc.degerlendirilmedi)

    rapor = relationship("ProjeRapor", lazy="joined")
    degerlendirme_hakemi = relationship("ProjeHakemleri")
