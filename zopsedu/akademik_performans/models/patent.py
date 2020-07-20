"""
Yoksis Patent Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class YoksisPatent(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Patent Modeli
    """
    __tablename__ = "yoksis_patent"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    PATENT_ID = Column(String(250))

    PATENT_NO = Column(String(250))
    PATENT_ADI = Column(String(250))
    BASVURU_SAHIPLERI = Column(String(250))
    BULUS_SAHIPLERI = Column(String(250))
    KATEGORI = Column(String(250))
    DOSYA_TIPI = Column(String(250))
    KAPSAM = Column(String(250))

    AKTIF_PASIF = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))

    PATENT_TARIHI = deferred(Column(String(250)))
    KATEGORI_ID = deferred(Column(String(250)))
    DOSYA_TIPI_ID = deferred(Column(String(250)))
    KAPSAM_ID = deferred(Column(String(250)))
    PATENT_SINIF = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))
    UNVAN_AD = deferred(Column(String(250)))
    KURUM_AD = deferred(Column(String(250)))
    KISI_SAYISI = deferred(Column(String(250)))
    TESV_PUAN = deferred(Column(String(250)))
    UNVAN_ID = deferred(Column(String(250)))
    KURUM_ID = deferred(Column(String(250)))
