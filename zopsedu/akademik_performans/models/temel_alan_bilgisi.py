"""
Yoksis Temel Alan Bilgisi Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisTemelAlanBilgisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Temel Alan Bilgisi Modeli
    """
    __tablename__ = "yoksis_temel_alan_bilgisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    T_UAK_ID = Column(String(250))
    TEMEL_ALAN_ID = deferred(Column(String(250)))
    BILIM_ALAN_ID = deferred(Column(String(250)))
    ANAHTARKELIME1_ID = deferred(Column(String(250)))
    ANAHTARKELIME2_ID = deferred(Column(String(250)))
    ANAHTARKELIME3_ID = deferred(Column(String(250)))
    TEMEL_ALAN_AD = Column(String(250))
    BILIM_ALAN_AD = Column(String(250))
    ANAHTARKELIME1_AD = Column(String(250))
    ANAHTARKELIME2_AD = Column(String(250))
    ANAHTARKELIME3_AD = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))
