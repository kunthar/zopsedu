"""Proje kalemleri modeli"""
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship

from zopsedu.bap.models.helpers import OlcuBirimi
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class ProjeKalemi(BASE_MODEL, ZopseduBase):
    """
    Proje kalemleri Modeli
    Proje yurutucusunun proje basvurusu esnasinde ekledi malzeme/hizmet vb. kayitlarin tutuldugu
    modeldir. Onerilen alanlar proje yurutucusunun belirledigi alanlardir. Kabul edilen alanlar ise
    komisyonun kabul ettigi alanlardir

    """
    __tablename__ = 'proje_kalemleri'
    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey("proje.id"))
    proje_turu_butce_kalem_id = Column(Integer, ForeignKey("butce_kalemi.id"))

    ad = Column(String)
    gerekce = Column(String)
    birim = Column(Enum(OlcuBirimi))

    # ilgili urunden kac adet olacagi(yurutucunun istedigi sayi)
    onerilen_miktar = Column(Integer)

    # komisyonda kabul edilen sayi
    toplam_miktar = Column(Integer, default=0)
    # kullanilan sayi
    kullanilan_miktar = Column(Integer, default=0)
    # rezerv edilen sayi
    rezerv_edilen_miktar = Column(Integer, default=0)

    onerilen_butce = Column(Numeric(12, 2), default="0.00")
    # islemler kabul edilen butce uzerinden yurutulecektir
    # kabul edilen butce kabul edilen yil1 yil2 yil3 un toplamindan olusur
    toplam_butce = Column(Numeric(12, 2), default="0.00")
    # satinalma sureci baslatildiginda butce rezerv edilir. satinalma basarili bir sekilde
    # tamamlanirsa rezervden kullanilana aktarilir
    rezerv_butce = Column(Numeric(12, 2), default="0.00")
    # harcanan butceyi temsil eder
    kullanilan_butce = Column(Numeric(12, 2), default="0.00")

    onerilen_yil_1 = Column(Numeric(12, 2), default="0.00")
    onerilen_yil_2 = Column(Numeric(12, 2), default="0.00")
    onerilen_yil_3 = Column(Numeric(12, 2), default="0.00")

    kabul_edilen_yil_1 = Column(Numeric(12, 2), default="0.00")
    kabul_edilen_yil_2 = Column(Numeric(12, 2), default="0.00")
    kabul_edilen_yil_3 = Column(Numeric(12, 2), default="0.00")

    proje_turu_butce_kalemi = relationship("ButceKalemi", lazy='joined')
