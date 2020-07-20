from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class FinansmanTipi(BASE_MODEL, ZopseduBase):
    """
    Finansman Tipi modeli
    """
    __tablename__ = "finansman_tipi"

    id = Column(Integer, primary_key=True)
    kodu = Column(Integer)
    aciklama = Column(String(120))