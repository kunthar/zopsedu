"""
Yoksis Bilgiri modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisBildiri(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Bildiri Modeli
    """
    __tablename__ = "yoksis_bildiri"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    YAYIN_ID = Column(String(250))

    KAPSAM_AD = Column(String(250))
    BILDIRI_ADI = Column(String(250))
    YAZAR_ADI = Column(String(250))
    ETKINLIK_ADI = Column(String(250))
    BILDIRI_TUR = Column(String(250))
    ETKINLIK_BAS_TARIHI = Column(String(250))
    ETKINLIK_BIT_TARIHI = Column(String(250))
    ULKE_ADI = Column(String(250))
    SEHIR = Column(String(250))

    AKTIF_PASIF = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))

    YAZAR_SAYISI = deferred(Column(String(250)))
    ULKE = deferred(Column(String(250)))
    YAYIN_DILI = deferred(Column(String(250)))
    YAYIN_DILI_ADI = deferred(Column(String(250)))
    YAYIN_DURUMU_AD = deferred(Column(String(250)))
    BASIM_TARIHI = deferred(Column(String(250)))
    CILT = deferred(Column(String(250)))
    SAYI = deferred(Column(String(250)))
    ILK_SAYFA = deferred(Column(String(250)))
    SON_SAYFA = deferred(Column(String(250)))
    DOI = deferred(Column(String(250)))
    ISSN = deferred(Column(String(250)))
    PRINT_ISBN = deferred(Column(String(250)))
    SPONSOR = deferred(Column(String(250)))
    BASIM_TURU = deferred(Column(String(250)))
    BASIM_TURU_AD = deferred(Column(String(250)))
    ERISIM_LINKI = deferred(Column(String(250)))
    ATIF_SAYISI = deferred(Column(String(250)))
    ALAN_BILGISI = deferred(Column(String(250)))
    ANAHTAR_KELIME = deferred(Column(String(250)))
    OZEL_SAYI = deferred(Column(String(250)))
    OZEL_SAYI_AD = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))
    TESV_PUAN = deferred(Column(String(250)))
    BILDIRI_SUNUM_TURU_AD = deferred(Column(String(250)))
    BILDIRI_TUR_ID = deferred(Column(String(250)))
    KAPSAM_ID = deferred(Column(String(250)))
    YAYIN_DURUMU = deferred(Column(String(250)))
    YAZAR_ID = deferred(Column(String(250)))
    BILDIRI_SUNUM_TURU = deferred(Column(String(250)))
