"""Vergi Daireleri Modeli"""

from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class VergiDairesi(BASE_MODEL, ZopseduBase):
    """Vergi Daireleri veri modeli"""

    __tablename__ = 'vergi_dairesi'
    id = Column(Integer, autoincrement=True, primary_key=True)
    kodu = Column(String(16))
    il = Column(String(100))
    adi = Column(String(255))
