"""
Yoksis Yonetilen Tez modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisYonetilenTez(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Yonetilen Tez Modeli
    """
    __tablename__ = "yoksis_yonetilen_tez"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    YIL = Column(String(250))
    YAZAR_ADI = Column(String(250))
    YAZAR_SOYADI = Column(String(250))
    UNIVERSITE_AD = Column(String(250))
    TEZ_ADI = Column(String(250))
    TUR_ADI = Column(String(250))
    ENSTITU_AD = Column(String(250))
    ABD_AD = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    VERIKAYNAK = deferred(Column(String(250)))
    YER_ADI = deferred(Column(String(250)))
    ULKE = deferred(Column(String(250)))
    KAYIT_ID = deferred(Column(String(250)))
    DURUM_ADI = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))
    YER_ID = deferred(Column(String(250)))
    TUR_ID = deferred(Column(String(250)))
