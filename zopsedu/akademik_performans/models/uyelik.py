"""
Yoksis Uyelik Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisUyelik(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Patent Modeli
    """
    __tablename__ = "yoksis_uyelik"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    UYELIK_ID = Column(String(250))

    KURULUS_TURU_AD = Column(String(250))
    KURULUS_ADI = Column(String(250))
    BAS_TAR = Column(String(250))
    BIT_TAR = Column(String(250))
    UYELIK_DURUMU_AD = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    AKTIF_PASIF_AD = deferred(Column(String(250)))
    UYELIK_DURUMU = deferred(Column(String(250)))
    KURULUS_TURU = deferred(Column(String(250)))
