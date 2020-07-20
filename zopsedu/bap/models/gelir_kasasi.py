"""bap gelir kasasi modeli"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class GelirKasasi(BASE_MODEL, ZopseduBase):
    """
    bap gelir kasasi modeli
    Bap a ait ana kasalari temsil eder. bap, dpt vb.
    Otomasyon icerisinde 1 ocak tarihinde var olan kasanin yeni mali yılı ile birlikte yeni instance
    olusturulur. ornegin 2019 yilina girildiginde ismi BAP olan mali yili 2018 olan kasa icin
    ismi BAP olan 2019 yilina ait yeni kasa olusturulur. 2018 yilina ait kasanin kullanilabilir
    butcesi 2019 yilina ait olan kasanin devreden_parasina yazilip ayni zamanda toplam_para fieldina
    eklenir. 2018 yilina ait kasanin parent_id si yeni olusturulan 2019 yili kasasi olur.
    """
    __tablename__ = "gelir_kasalari"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("gelir_kasalari.id"))

    adi = Column(String(100))
    mali_yil = Column(Integer)

    toplam_para = Column(Numeric(14, 2), default=0.00)
    harcanan_para = Column(Numeric(14, 2), default=0.00)
    rezerv_para = Column(Numeric(14, 2), default=0.00)

    # bir onceki mali yildan kalan parayi belirtir
    devreden_para = Column(Numeric(14, 2), default=0.00)
    # bir sonraki yila devredilen para
    devredilen_para = Column(Numeric(14, 2), default=0.00)

    projeler = relationship("Proje")
    girdiler = relationship("ButceGirdi")


class ButceGirdi(BASE_MODEL, ZopseduBase):
    """Bap gelir kasasi butce girdileri modeli"""
    __tablename__ = "butce_girdileri"

    id = Column(Integer, primary_key=True)
    gelir_kasasi_id = Column(Integer, ForeignKey("gelir_kasalari.id"))

    tutar = Column(Numeric(14, 2))
    aciklama = Column(String(255))

    gelir_kasasi = relationship("GelirKasasi")
