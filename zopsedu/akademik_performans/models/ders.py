"""
Yoksis Ders modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisDers(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Ders Modeli
    """
    __tablename__ = "yoksis_ders"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    DERS_ID = Column(String(250))

    DERS_ADI = Column(String(250))
    OGRENIM_ADI = Column(String(250))
    AKADEMIK_YIL = Column(String(250))
    DIL_ADI = Column(String(250))
    DERS_SAATI = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    EKLEME_TARIHI = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))

    OGRENIM_ID = deferred(Column(String(250)))
    AKADEMIK_YIL_ID = deferred(Column(String(250)))
    DIL_ID = deferred(Column(String(250)))
