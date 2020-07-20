"""
Yoksis Birlikte calistigi kisiler modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisBirlikteCalistigiKisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Birlikte Calistigi Kisi Modeli
    """
    __tablename__ = "yoksis_birlikte_calisitigi_kisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    ARASTIRMACI_ID = Column(String(250))
    KADRO_UNVAN_ADI = Column(String(250))
    PERSONEL_ADI = Column(String(250))
    PERSONEL_SOYADI = Column(String(250))
    KADRO_YERI = Column(String(250))
    YOKAKADEMIK_LINK = Column(String(250))
    PERSONEL_RESIM_LINK = Column(String(250))
