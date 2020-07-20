"""
Yoksis Tasarim Bilgisi Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisTasarimBilgisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi tasarim bilgisi
    """
    __tablename__ = "yoksis_tasarim_bilgisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    P_TASARIM_ID = Column(String(250))
    TASARIM_SAHIPLERI = Column(String(250))
    TASARIM_TURU = deferred(Column(String(250)))
    TASARIM_TURU_ADI = Column(String(250))
    TASARIM_TURU_DETAY = Column(String(250))
    TASARIM_TURU_DETAY_AD = Column(String(250))
    KAPSAM = deferred(Column(String(250)))
    KAPSAM_AD = Column(String(250))
    TASARIM_ADI = Column(String(250))
    TASARIM_OZETI = Column(String(250))
    BAS_TARIHI = Column(String(250))
    BITIS_TARIHI = Column(String(250))
    UNVAN_ID = deferred(Column(String(250)))
    UNVAN_AD = Column(String(250))
    KURUM_ID = deferred(Column(String(250)))
    KURUM_AD = Column(String(250))
    TESV_PUAN = Column(String(250))
    KISI_SAYISI = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))
