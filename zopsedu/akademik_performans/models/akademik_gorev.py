"""
Yoksis Akademik Gorev  modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisAkademikGorev(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Akademik Gorev modeli
    """
    __tablename__ = "yoksis_akademik_gorev_listesi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    GOREV_ID = Column(String(250))

    BASTAR1 = Column(String(250))
    BITTAR1 = Column(String(250))
    UNIV_BIRIM_ADI = Column(String(250))
    FAKULTEBILGISI = Column(String(250))
    BOLUMBILGISI = Column(String(250))
    KADRO_UNVAN_ADI = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    ULKE_ID = deferred(Column(String(250)))
    BILIMALAN_ADI = deferred(Column(String(250)))
    UZMANLIK_ALANI = deferred(Column(String(250)))
    UZMANLIK_ALANI_AD = deferred(Column(String(250)))
    ULKE_AD = deferred(Column(String(250)))
    DIGER_UNIVERSITE = deferred(Column(String(250)))
    UNIV_ID = deferred(Column(String(250)))
    BIRIM_ID = deferred(Column(String(250)))
    YER_ID = deferred(Column(String(250)))
    YER_AD = deferred(Column(String(250)))
    ALANBILGISI = deferred(Column(String(250)))
    KADRO_UNVAN_ID = deferred(Column(String(250)))
    ACIKLAMA = deferred(Column(String(250)))
    AKADEMIK_DURUM = deferred(Column(String(250)))
    AKADEMIK_DURUM_ADI = deferred(Column(String(250)))
    AKADEMIK_BIRIM_ADI = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))

