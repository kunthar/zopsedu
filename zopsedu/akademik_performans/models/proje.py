"""
Yoksis Proje modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisProje(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Proje Modeli
    """
    __tablename__ = "yoksis_proje"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    PROJE_ID = Column(String(250))
    PROJE_AD = Column(String(250))
    PROJE_KONUSU = Column(String(250))
    PROJE_DURUMU_ID = deferred(Column(String(250)))
    PROJE_DURUMU_AD = Column(String(250))
    BAS_TAR = Column(String(250))
    BIT_TAR = Column(String(250))
    BUTCE = Column(String(250))
    PROJE_KONUMU_ID = deferred(Column(String(250)))
    PROJE_KONUMU_AD = Column(String(250))
    PROJE_TURU_ID = deferred(Column(String(250)))
    PROJE_TURU_AD = Column(String(250))
    PARA_BIRIMI_ID = deferred(Column(String(250)))
    PARA_BIRIMI_AD = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = deferred(Column(String(250)))
    AKTIF_PASIF_AD = Column(String(250))
    KAPSAM = deferred(Column(String(250)))
    KAPSAM_AD = Column(String(250))
    UNVAN_ID = deferred(Column(String(250)))
    UNVAN_AD = Column(String(250))
    KURUM_ID = deferred(Column(String(250)))
    KURUM_AD = Column(String(250))
    TESV_PUAN = Column(String(250))
