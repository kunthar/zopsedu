"""
Yoksis Arastirma Sertifika Bilgisi Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisArastirmaSertifikaBilgisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi arastirma sertifika bilgisi
    """
    __tablename__ = "yoksis_arastirma_sertifika_bilgisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    S_ID = Column(String(250))
    TUR_ID = deferred(Column(String(250)))
    TUR_ADI = Column(String(250))
    ADI = Column(String(250))
    ICERIK = Column(String(250))
    YER = Column(String(250))
    KAPSAM = deferred(Column(String(250)))
    KAPSAM_AD = Column(String(250))
    SURE = Column(String(250))
    BASTAR = Column(String(250))
    BITTAR = Column(String(250))
    UNVAN_ID = deferred(Column(String(250)))
    UNVAN_AD = Column(String(250))
    KURUM_AD = Column(String(250))
    KURUM_ID = deferred(Column(String(250)))
    KISI_SAYISI = Column(String(250))
    ULKE_SEHIR = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    TESV_PUAN = Column(String(250))
    AKTIF_PASIF = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))
