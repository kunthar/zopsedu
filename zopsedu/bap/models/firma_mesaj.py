"""Sistem bildirimleri icin mesaj modeli"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class FirmaMesaj(BASE_MODEL, ZopseduBase):
    """Proje Mesaj Modeli"""
    __tablename__ = 'firma_mesaj'

    id = Column(Integer, primary_key=True)
    firma_id = Column(Integer, ForeignKey('bap_firma.id'))
    mesaj_id = Column(Integer, ForeignKey('mesaj.id'), unique=True)
    mesaj = relationship("Mesaj", cascade='save-update, delete')
