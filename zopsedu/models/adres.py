"""Adres Modelinden Oluşur"""
from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class Adres(BASE_MODEL, ZopseduBase):
    """Adres Data Model"""
    __tablename__ = 'adres'
    id = Column(Integer, primary_key=True)
    posta_kodu = Column(Integer)
    adres = Column(String(500))
    ilce = Column(String(50))
    il = Column(String(50))
