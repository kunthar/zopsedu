"""Proje modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, String, Integer, ForeignKey
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class ProjeDestekleyenKurulus(BASE_MODEL, ZopseduBase):
    """
    Proje Destekleyen Kurulus Modeli
    """
    __tablename__ = "proje_destekleyen_kurulus"

    id = Column(Integer, primary_key=True)
    # proje türü ile alakalı fieldlar
    proje_id = Column(Integer, ForeignKey('proje.id'))

    adi = Column(String(100))
    adres = Column(String(300))
    telefon = Column(String(25))
    eposta = Column(String(100))
    yetkili_ad_soyad = Column(String(100))
    yetkili_gorev = Column(String(100))
