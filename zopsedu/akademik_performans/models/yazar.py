"""
Yoksis Yazar Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisYazar(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Yazar modeli
    """
    __tablename__ = "yoksis_yazar"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    Y_ID = Column(String(250))
    TC_KIMLIK_NO = Column(String(250))
    ARASTIRMACI_ID = deferred(Column(String(250)))
    YAZARAD = Column(String(250))
    YAZARSOYAD = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    YAZAR_SIRA = Column(String(250))
    KADRO_UNVAN_ID = deferred(Column(String(250)))
    KADRO_UNVAN_ADI = Column(String(250))
    YAZAR_FORM_ID = deferred(Column(String(250)))
    UNIVERSITE = Column(String(250))
    UNIV_ID = deferred(Column(String(250)))
    KULLANICININ_ARS_ID = Column(String(250))
    YAZAR_TUR = deferred(Column(String(250)))
    YAZAR_TUR_AD = Column(String(250))
