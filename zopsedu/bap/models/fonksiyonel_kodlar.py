from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class FonksiyonelKodlar(BASE_MODEL, ZopseduBase):
    """
    Fonksiyonel Kodlar modeli
    """
    __tablename__ = "fonksiyonel_kodlar"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    kodu = Column(String(24))
    aciklama = Column(String(240))