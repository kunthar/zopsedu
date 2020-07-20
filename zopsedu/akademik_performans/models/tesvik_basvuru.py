"""
Yoksis Tesvik Basvuru Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisTesvikBasvuru(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Tesvik Basvuru
    """
    __tablename__ = "yoksis_tesvik_basvuru"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    BASVURU_ID = Column(String(250))
    DONEM_ID = deferred(Column(String(250)))
    DONEM_AD = Column(String(250))
    BASVURU_TARIHI = Column(String(250))
    SON_ISLEM_TARIHI = Column(String(250))

