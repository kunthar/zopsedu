"""Hakem modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, Integer, ForeignKey, Enum, String, Boolean
from sqlalchemy.orm import relationship
from zopsedu.lib.helpers import WTFormEnum
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class HakemTuru(str, WTFormEnum):
    """HakemTuru Enum Classı"""
    hakem = "Hakem"
    bilim_kurulu_uyesi = "Bilim Kurulu Üyesi"
    alt_komisyon_uyesi = "Alt Komisyon Üyesi"


class Hakem(BASE_MODEL, ZopseduBase):  # pylint: disable=too-many-instance-attributes
    """
    Hakem modeli

    """
    __tablename__ = "hakem"

    id = Column(Integer, primary_key=True)
    kurum_ici = Column(Boolean)
    hakem_turu = Column(Enum(HakemTuru))
    kurum = Column(String(120))
    daire = Column(String(120))
    birim = Column(String(120))

    person_id = Column(Integer, ForeignKey("person.id"))
    personel_id = Column(Integer, ForeignKey("personel.id", ondelete="CASCADE"))
    unvan = Column(Integer, ForeignKey("hitap_unvan.id"))
    universite_id = Column(Integer, ForeignKey("birim.id"))
    fakulte_id = Column(Integer, ForeignKey("birim.id"))
    bolum_id = Column(Integer, ForeignKey("birim.id"))

    hitap_unvan = relationship('HitapUnvan', uselist=False, lazy='joined')
    person = relationship("Person", uselist=False)
    personel = relationship("Personel", uselist=False)
    bolum = relationship("Birim", foreign_keys=[bolum_id], uselist=False, backref='hakem_bolum')
    universite = relationship("Birim", foreign_keys=[universite_id], uselist=False, backref='hakem_universite')
    fakulte = relationship("Birim", foreign_keys=[fakulte_id], uselist=False,
                           backref='hakem_fakulte')


class HakemOneri(BASE_MODEL, ZopseduBase):
    """
    Hakem Önerilerinin tutuldugu model.
    Projeye başvuran kişi tarafından önerilen, hakem olmaya aday kişiler bu modelde tutulur.
    Onerilen kişiler değerlendirmeye alınıp eger uygunsa sisteme hakem olarak kaydedilir ve bu
    tablodaki değerler silinir
    """

    __tablename__ = "hakem_oneri"

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey("proje.id"))
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    ad = Column(String(50))
    soyad = Column(String(50))
    email = Column(String(100))

    proje = relationship("Proje")
    ogretim_elemani = relationship("OgretimElemani", lazy="joined")
