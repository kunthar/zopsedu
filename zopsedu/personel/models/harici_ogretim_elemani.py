"""HariciOgretimElemani modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.helpers import  PersonelEngellilik


class HariciOgretimElemani(BASE_MODEL, ZopseduBase):
    """
    HariciOgretimElemani modeli

    """
    __tablename__ = "harici_ogretim_elemani"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    unvan = Column(Integer, ForeignKey("hitap_unvan.id"))
    oda_no = Column(String(20))
    oda_tel_no = Column(Integer)

    web_sitesi = Column(String(100))
    yayinlar = Column(Text)
    projeler = Column(Text)

    biyografi = Column(Text)
    notlar = Column(Text)
    engelli_durumu = Column(Boolean)
    engel_grubu = Column(String(50))
    engel_derecesi = Column(Enum(PersonelEngellilik))
    engel_orani = Column(Integer)

    aktif_mi = Column(Boolean)
    hitap_unvan = relationship('HitapUnvan', uselist=False, lazy='joined')
    akademik_yayinlari = Column(Text)
    # verdigi_dersler = field.String(_(u"Verdiği Dersler"), index=True, required=False)

    person = relationship("Person")
    user = relationship("User", secondary="person", uselist=False, lazy='joined')
