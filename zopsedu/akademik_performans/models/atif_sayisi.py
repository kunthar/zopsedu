"""
Yoksis Atif Sayisi modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisAtifSayisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Atif Sayisi
    """
    __tablename__ = "yoksis_atif_sayisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    A_ID = Column(String(250))
    DONEM = Column(String(250))
    TUR = deferred(Column(String(250)))
    TUR_AD = Column(String(250))
    ESER_TURU = Column(String(250))
    ESER_ID = deferred(Column(String(250)))
    ULUSLAR_KIT_ATF = Column(String(250))
    ULUSAL_KIT_ATF = Column(String(250))
    SSCI_INDEKS_ATF = Column(String(250))
    ALAN_INDEKS_ATF = Column(String(250))
    DIGER_ATIF = Column(String(250))
    TESV_PUAN = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    ESCI = Column(String(250))
    BESTECI_ESER = Column(String(250))
