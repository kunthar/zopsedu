"""HitapUnvan Kayıtlarının tutulduğu model"""
from sqlalchemy import Column, Integer, String
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class HitapUnvan(BASE_MODEL, ZopseduBase):
    """HitapUnvan modeli"""
    __tablename__ = 'hitap_unvan'
    id = Column(Integer, primary_key=True)
    ad = Column(String(255))
    kod = Column(Integer)
