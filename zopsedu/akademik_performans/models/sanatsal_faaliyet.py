"""
Yoksis Sanatsal Faaliyet Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisSanatsalFaaliyet(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Sanatsal Faaliyet Modeli
    """
    __tablename__ = "yoksis_sanatsal_faaliyet"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    S_ID = Column(String(250))
    ANA_TUR = deferred(Column(String(250)))
    ANATUR_ADI = Column(String(250))
    KAPSAM = deferred(Column(String(250)))
    KAPSAM_AD = Column(String(250))
    TIP = deferred(Column(String(250)))
    TIP_ADI = Column(String(250))
    ETKINLIK_ADI = Column(String(250))
    ETKINLIK_YERI = Column(String(250))
    ETKINLIK_TURU = Column(String(250))
    BAS_TARIH = Column(String(250))
    BIT_TARIH = Column(String(250))
    DUZENLEYENLER = Column(String(250))
    ULKE = deferred(Column(String(250)))
    ULKE_ADI = Column(String(250))
    SEHIR = Column(String(250))
    ETKINLIK_DILI = Column(String(250))
    DIL_ADI = Column(String(250))
    KISI_SAYISI = Column(String(250))
    KISI_SIRASI = Column(String(250))
    ETKINLIK_SURESI = Column(String(250))
    ETKINLIK_TURU_AD = Column(String(250))
    UNVAN_ID = deferred(Column(String(250)))
    UNVAN_AD = Column(String(250))
    KURUM_ID = deferred(Column(String(250)))
    KURUM_AD = Column(String(250))
    TESV_PUAN = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))
