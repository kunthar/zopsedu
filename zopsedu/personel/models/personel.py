"""Personel modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.helpers import PersonelEngellilik, PersonelStatu, PersonelTuru, HizmetSinifi


# pylint: disable=too-few-public-methods
class Personel(BASE_MODEL, ZopseduBase):
    """
    Personel modeli

    Personelin özlük ve iletişim bilgilerini içerir.
    """
    __tablename__ = "personel"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    birim = Column(Integer, ForeignKey("birim.id"))
    unvan = Column(Integer, ForeignKey("hitap_unvan.id"))

    kurum_sicil_no = Column(Integer)

    web_sitesi = Column(String(100))
    yayinlar = Column(Text)
    projeler = Column(Text)
    biyografi = Column(Text)
    notlar = Column(Text)

    oda_no = Column(String(20))
    oda_tel_no = Column(Integer)

    # verdigi_dersler = field.String(_(u"Verdiği Dersler"))
    engelli_durumu = Column(Boolean)
    engel_grubu = Column(String(50))
    engel_derecesi = Column(Enum(PersonelEngellilik))
    engel_orani = Column(Integer)
    bakmakla_yukumlu_kisi_sayisi = Column(Integer)
    #
    kazanilmis_hak_derece = Column(Integer)
    kazanilmis_hak_kademe = Column(Integer)
    kazanilmis_hak_ekgosterge = Column(Integer)
    #
    gorev_ayligi_derece = Column(Integer)
    gorev_ayligi_kademe = Column(Integer)
    gorev_ayligi_ekgosterge = Column(Integer)
    #
    emekli_muktesebat_derece = Column(Integer)
    emekli_muktesebat_kademe = Column(Integer)
    emekli_muktesebat_ekgosterge = Column(Integer)
    # Kazanılmış Hak Sonraki Terfi Tarihi
    kh_sonraki_terfi_tarihi = Column(Date)
    # Görev Aylığı Sonraki Terfi Tarihi
    ga_sonraki_terfi_tarihi = Column(Date)
    # Emekli Müktesebat Sonraki Terfi Tarihi
    em_sonraki_terfi_tarihi = Column(Date)
    #
    #
    #
    # # Aşağıdaki bilgiler atama öncesi kontrol edilecek, Doldurulması istenecek
    emekli_sicil_no = Column(String(50))
    emekli_giris_tarihi = Column(Date)

    personel_turu = Column(Enum(PersonelTuru))
    hizmet_sinifi = Column(Enum(HizmetSinifi))
    statu = Column(Enum(PersonelStatu))
    #
    # # akademik personeller icin sozlesme sureleri
    gorev_suresi_baslama = Column(Date)
    gorev_suresi_bitis = Column(Date)
    #
    # # todo: durum_degisikligi yonetimi
    # # kurumda ilk goreve baslama bilgileri, atama modelinden elde edilip
    # # edilemeyecegini soracagiz. mevcut otomasyonda ayrilmalar da burada tutuluyor.
    # # bunu tarih ve durum_degisikligi fieldlarindan olusan bir listnode seklinde tutabiliriz.
    # goreve_baslama_tarihi = field.Date(_(u"Göreve Başlama Tarihi"), index=True, format="%d.%m.%Y")
    # baslama_sebep = HitapSebep()
    #
    # # aday ve idari memurlar icin mecburi hizmet suresi
    # mecburi_hizmet_suresi = field.Date(_(u"Mecburi Hizmet Süresi"), index=True, format="%d.%m.%Y")
    #
    # # Arama için kullanılacak Flaglar
    # kadro_derece = field.Integer(default=0)
    # aday_memur = field.Boolean()
    # arsiv = field.Boolean()  # ayrilmis personeller icin gecerlidir.

    hitap_unvan = relationship('HitapUnvan', uselist=False, lazy='joined')
    person = relationship("Person", uselist=False)
    birimi = relationship("Birim", uselist=False, lazy='joined')
    user = relationship("User", secondary="person", uselist=False, lazy='joined', viewonly=True)
