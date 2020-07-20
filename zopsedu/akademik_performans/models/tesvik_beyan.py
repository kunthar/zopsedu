"""
Yoksis Tesvik Beyan Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisTesvikBeyan(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Tesvik Beyan
    """
    __tablename__ = "yoksis_tesvik_beyan"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    FB_ID = Column(String(250))
    TUR = deferred(Column(String(250)))
    TUR_AD = Column(String(250))
    ESER_TUR = deferred(Column(String(250)))
    ESER_TUR_AD = Column(String(250))
    ESER_ID = deferred(Column(String(250)))
    GUNCELLEME_TARIHI = Column(String(250))
