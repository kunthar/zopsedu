"""
Yoksis Kitap modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisKitap(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi Kitap Modeli
    """
    __tablename__ = "yoksis_kitap"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    YAYIN_ID = Column(String(250))

    KITAP_TUR = Column(String(250))
    KITAP_ADI = Column(String(250))
    YAZAR_ADI = Column(String(250))
    YAZAR_SAYISI = Column(String(250))
    EDITOR_ADI = Column(String(250))
    YAYIN_EVI = Column(String(250))
    YIL = Column(String(250))
    ISBN = Column(String(250))
    KACINCI_BASIM = Column(String(250))
    SAYFA_SAYISI = Column(String(250))
    TESV_PUAN = Column(String(250))

    AKTIF_PASIF = Column(String(250))
    GUNCELLEME_TARIHI = Column(String(250))

    KAPSAM_ID = deferred(Column(String(250)))
    KAPSAM_AD = deferred(Column(String(250)))
    KITAP_TUR_ID = deferred(Column(String(250)))
    KATKI_DUZEYI = deferred(Column(String(250)))
    KATKI_DUZEYI_AD = deferred(Column(String(250)))
    BOLUM_ADI = deferred(Column(String(250)))
    ULKE = deferred(Column(String(250)))
    ULKE_ADI = deferred(Column(String(250)))
    SEHIR = deferred(Column(String(250)))
    YAYIN_DILI = deferred(Column(String(250)))
    YAYIN_DILI_ADI = deferred(Column(String(250)))
    BOLUM_ILK_SAYFA = deferred(Column(String(250)))
    BOLUM_SON_SAYFA = deferred(Column(String(250)))
    BASIM_TURU = deferred(Column(String(250)))
    BASIM_TURU_AD = deferred(Column(String(250)))
    ERISIM_LINKI = deferred(Column(String(250)))
    ATIF_SAYISI = deferred(Column(String(250)))
    ALAN_BILGISI = deferred(Column(String(250)))
    ANAHTAR_KELIME = deferred(Column(String(250)))
    YAZAR_ID = deferred(Column(String(250)))
    AKTIF_PASIF_AD = deferred(Column(String(250)))
