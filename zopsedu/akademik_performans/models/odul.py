"""
Yoksis Odul Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class YoksisOdul(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Odul Modeli
    """
    __tablename__ = "yoksis_odul"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    ODUL_ID = Column(String(250))

    ODUL_ADI = Column(String(250))
    ODUL_TARIH = Column(String(250))
    KURULUS_ADI = Column(String(250))
    ISYERI_TURU_ADI = Column(String(250))
    ULKE_AD = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))

    FAAL_DETAY_ADI = deferred(Column(String(250)))
    KURUM_ADI = deferred(Column(String(250)))
    ODUL_TURU = deferred(Column(String(250)))
    P_UNVAN_AD = deferred(Column(String(250)))
    P_KURUM_AD = deferred(Column(String(250)))
    ODUL_ACIKLAMA = deferred(Column(String(250)))
    KISI_SAYISI = deferred(Column(String(250)))
    ODUL_KISI_SIRA = deferred(Column(String(250)))
    TESV_PUAN = deferred(Column(String(250)))
    FAAL_DETAY_ID = deferred(Column(String(250)))
    ODUL_TUR_ID = deferred(Column(String(250)))
    P_UNVAN_ID = deferred(Column(String(250)))
    P_KURUM_ID = deferred(Column(String(250)))
    ISYERI_TURU_ID = deferred(Column(String(250)))
    KURUM_ID = deferred(Column(String(250)))
    ULKE_ID = deferred(Column(String(250)))
