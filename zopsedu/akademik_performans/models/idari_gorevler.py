"""
Yoksis İdari Gorevler Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisIdariGorev(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi İdari Gorevler Modeli
    """
    __tablename__ = "yoksis_idari_gorevler"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    IDGOR_ID = Column(String(250))

    BAS_TAR = Column(String(250))
    BIT_TAR = Column(String(250))
    FAKULTEMYOENST = Column(String(250))
    GOREV_ADI = Column(String(250))
    UNV_BIRIM_ADI = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    BOLUM = deferred(Column(String(250)))
    ABD = deferred(Column(String(250)))
    YER_ADI = deferred(Column(String(250)))
    ULKE_ADI = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))
    YER_ID = deferred(Column(String(250)))
    ULKE_ID = deferred(Column(String(250)))
    GOREV_ID = deferred(Column(String(250)))
    UNV_BIRIM_ID = deferred(Column(String(250)))
