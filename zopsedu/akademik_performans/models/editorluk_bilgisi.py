"""
Yoksis Editorluk Bilgisi Modeli
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import deferred

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: Text uzunluklari belirlenmesi gerekiyor.
# todo: id li alanlar kullanilabilir mi ??
class YoksisEditorlukBilgisi(BASE_MODEL, ZopseduBase):
    """
    Yok akademik personel ozgemis servisinden toplanmis verirnin sistemde bulunan ogretim
    uyesine iliskilendirildi editorluk bilgisi
    """
    __tablename__ = "yoksis_editorluk_bilgisi"

    id = Column(Integer, primary_key=True)
    ogretim_elemani_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    YAYIN_ID = Column(String(250))
    KAPSAM_ID = deferred(Column(String(250)))
    KAPSAM_AD = Column(String(250))
    EDITORLUK_TUR = deferred(Column(String(250)))
    EDITORLUK_TUR_AD = Column(String(250))
    EDITOR_GOREV = deferred(Column(String(250)))
    EDITOR_GOREV_AD = Column(String(250))
    YAYIN_ADI = Column(String(250))
    YAZAR_ADI = Column(String(250))
    YAZAR_SAYISI = Column(String(250))
    ULKE = deferred(Column(String(250)))
    ULKE_ADI = Column(String(250))
    SEHIR = Column(String(250))
    YAYIN_EVI = Column(String(250))
    YAYIN_DILI = deferred(Column(String(250)))
    YAYIN_DILI_ADI = Column(String(250))
    ENDEKS_ID = Column(String(250))
    ENDEKS = deferred(Column(String(250)))
    YIL = Column(String(250))
    BAS_TARIH = Column(String(250))
    BIT_TARIH = Column(String(250))
    DOI = Column(String(250))
    ISSN = Column(String(250))
    ISBN = Column(String(250))
    ERISIM_TURU = deferred(Column(String(250)))
    ERISIM_TURU_AD = Column(String(250))
    ERISIM_LINKI = Column(String(250))
    ALAN_BILGISI = Column(String(250))
    ANAHTAR_KELIME = Column(String(250))
    YAZAR_ID = deferred(Column(String(250)))
    GUNCELLEME_TARIHI = Column(String(250))
    AKTIF_PASIF = Column(String(250))
    AKTIF_PASIF_AD = Column(String(250))
    TESV_PUAN = Column(String(250))
