"""
Yoksis Ogrenim Bilgisi modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisOgrenimBilgisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Ogrenim Bilgisi modeli
    """
    __tablename__ = "yoksis_ogrenim_bilgisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    ID = Column(String(250))

    BASTAR1 = Column(String(250))
    BITTAR1 = Column(String(250))
    PROGRAM_ADI = Column(String(250))
    UNV_BIRIM_ADI = Column(String(250))
    AKADEMIK_BIRIM_ADI = Column(String(250))
    TEZ_ADI = Column(String(250))
    TEZ_BIT_TAR = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))

    YER_ID = deferred(Column(String(250)))
    YER_AD = deferred(Column(String(250)))
    ULKE_ID = deferred(Column(String(250)))
    DIGER_ALAN = deferred(Column(String(250)))
    BIRIM_YOK = deferred(Column(String(250)))
    ULKE_AD = deferred(Column(String(250)))
    PROGRAM_ID = deferred(Column(String(250)))
    DIGER_UNIVERSITE = deferred(Column(String(250)))
    TEZ_ASAMASI = deferred(Column(String(250)))
    TEZ_ASAMASI_AD = deferred(Column(String(250)))
    UNIV_ID = deferred(Column(String(250)))
    AKADEMIK_BIRIM_ID = deferred(Column(String(250)))
    FAKULTEBILGISI = deferred(Column(String(250)))
    BOLUMBILGISI = deferred(Column(String(250)))
    ALANBILGISI = deferred(Column(String(250)))
    DIPLOMA_NO = deferred(Column(String(250)))
    DIPLOMADENKLIK_TARIH_SAYI = deferred(Column(String(250)))
    DANISMAN_TC = deferred(Column(String(250)))
    TEZ_BAS_TAR = deferred(Column(String(250)))
    DANISMAN_AD_SOYAD = deferred(Column(String(250)))
    C_BIRIM_ID = deferred(Column(String(250)))
    C_BIRIM_AD = deferred(Column(String(250)))

