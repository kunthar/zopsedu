"""Sistem bildirimleri icin mesaj modeli"""
from sqlalchemy import ForeignKey, Column, Integer, Text, Enum
from sqlalchemy.orm import relationship

from zopsedu.bap.models.helpers import NotTipi
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class ProjeNot(BASE_MODEL, ZopseduBase):
    """Proje Notlari Modeli"""
    __tablename__ = 'proje_not'

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey("proje.id"))
    notu_ekleyen_yetkili = Column(Integer)
    notu=Column(Text)
    not_tipi=Column(Enum(NotTipi))
    proje = relationship('Proje')
