"""Sablonlarin bilgilerinin tutuldugu database tablosu"""

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Text

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class Sablon(BASE_MODEL, ZopseduBase):
    """Şablon dosyalarının saklandığı veri modeli"""
    __tablename__ = 'sablons'
    id = Column(Integer, autoincrement=True, primary_key=True)
    file = Column(Integer, ForeignKey('file.id'))
    sablon_tipi_id = Column(Integer, ForeignKey('sablon_type.id'))
    query_id = Column(Integer, ForeignKey('query_helper.id'))

    module_name = Column(String(16))
    sub_module_name = Column(String(16))

    sablon_text = Column(Text())
    adi = Column(String(255))
    kullanilabilir_mi = Column(Boolean, default=True)
    ebys_icin_kullanilabilir_mi = Column(Boolean, default=False)

    file_r = relationship("File")
    sablon_tipi = relationship("SablonTipi", lazy="joined")
    query = relationship("QueryHelper", lazy="joined")


class SablonTipi(BASE_MODEL, ZopseduBase):
    """Şablon dosyalarının saklandığı veri modeli"""
    __tablename__ = 'sablon_type'
    id = Column(Integer, autoincrement=True, primary_key=True)

    adi = Column(String(255))
    module_name = Column(String(16))
    sub_module_name = Column(String(16))
