"""
Yoksis Makele modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisMakale(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Makele Modeli
    """
    __tablename__ = "yoksis_makale"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    YAYIN_ID = Column(String(250))

    KAPSAM_AD = Column(String(250))
    HAKEM_TUR_AD = Column(String(250))
    ENDEKS = Column(String(250))
    MAKALE_ADI = Column(String(250))
    YAZAR_ADI = Column(String(250))
    DERGI_ADI = Column(String(250))
    ERISIM_LINKI = Column(String(250))
    ATIF_SAYISI = Column(String(250))
    MAKALE_TURU_AD = Column(String(250))
    YIL = Column(String(250))
    CILT = Column(String(250))
    SAYI = Column(String(250))
    ILK_SAYFA = Column(String(250))
    SON_SAYFA = Column(String(250))
    DOI = Column(String(250))
    ENDEKS_ID = Column(String(250))

    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))

    KAPSAM_ID = deferred(Column(String(250)))
    HAKEM_TUR = deferred(Column(String(250)))
    YAZAR_SAYISI = deferred(Column(String(250)))
    ULKE = deferred(Column(String(250)))
    ULKE_ADI = deferred(Column(String(250)))
    SEHIR = deferred(Column(String(250)))
    YAYIN_DILI = deferred(Column(String(250)))
    YAYIN_DILI_ADI = deferred(Column(String(250)))
    AY = deferred(Column(String(250)))
    ISSN = deferred(Column(String(250)))
    ERISIM_TURU = deferred(Column(String(250)))
    ERISIM_TURU_AD = deferred(Column(String(250)))
    ALAN_BILGISI = deferred(Column(String(250)))
    ANAHTAR_KELIME = deferred(Column(String(250)))
    OZEL_SAYI = deferred(Column(String(250)))
    OZEL_SAYI_AD = deferred(Column(String(250)))
    SPONSOR = deferred(Column(String(250)))
    YAZAR_ID = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))
    MAKALE_TURU_ID = deferred(Column(String(250)))
    TESV_PUAN = deferred(Column(String(250)))
