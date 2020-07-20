"""
Yoksis Yabanci Dil modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisYabanciDil(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Yabanci Dil
    """
    __tablename__ = "yoksis_yabanci_dil"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    Y_ID = Column(String(250))
    DIL_ID = deferred(Column(String(250)))
    DIL_AD = Column(String(250))
    DIL_SINAV_ID = deferred(Column(String(250)))
    DIL_SINAV_AD = Column(String(250))
    PUAN = Column(String(250))
    ESDEGERPUAN = Column(String(250))
    YIL = Column(String(250))
    DONEM_ID = deferred(Column(String(250)))
    DONEM_AD = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))
    SINAVBILGISIYOK = Column(String(250))
