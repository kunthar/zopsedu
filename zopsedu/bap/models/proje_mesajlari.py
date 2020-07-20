"""Sistem bildirimleri icin mesaj modeli"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class ProjeMesaj(BASE_MODEL, ZopseduBase):
    """Proje Mesaj Modeli"""
    __tablename__ = 'proje_mesaj'

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey('proje.id'))
    mesaj_id = Column(Integer, ForeignKey('mesaj.id'), unique=True)
    mesaj = relationship("Mesaj", cascade='save-update, delete')
