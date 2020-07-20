"""Birim modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# pylint: disable=too-few-public-methods
class Birim(BASE_MODEL, ZopseduBase):
    """
    Birim modeli
    Kullanıcılara rol tanımlarken kullanılan, kullanıcının hangı birimde
    olduğunu taşıyan modeldir.
    Akademik ve idari birimlerin özelliklerini taşır.
    """
    __tablename__ = "birim"

    id = Column(Integer, primary_key=True)
    ust_birim_id = Column(Integer, ForeignKey("birim.id"))
    universite_id = Column(Integer, ForeignKey("birim.id"))
    fakulte_yo_myo_enstitu_id = Column(Integer, ForeignKey("birim.id"))

    ad = Column(String(300))
    uzun_ad = Column(String(600))
    ingilizce_birim_adi = Column(String(350))

    birim_tipi = Column(String(130))
    birim_tipi_kodu = Column(Integer)

    ogrenim_dili = Column(String(50))
    ogrenim_dili_kodu = Column(Integer)

    ogrenme_tipi = Column(String(40))
    ogrenme_tipi_kodu = Column(Integer)

    universite_turu_kodu = Column(Integer)

    sehir_kodu = Column(Integer)
    sehir_adi = Column(String(30))

    semt_kodu = Column(Integer)
    semt_adi = Column(String(50))

    kod_bid_ad = Column(String(200))
    kod_bid_kodu = Column(Integer)

    aktif_mi = Column(Boolean, default=True)
    aktiklif_kod = Column(Integer)

    ogrenim_suresi = Column(Integer)
    kilavuz_kodu = Column(Integer)

    ust_birim = relationship("Birim", backref=backref('parent', remote_side='Birim.id'),
                             foreign_keys=[ust_birim_id])
