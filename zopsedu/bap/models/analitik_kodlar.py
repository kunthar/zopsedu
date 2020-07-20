from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class GelirSiniflandirma(BASE_MODEL, ZopseduBase):
    """
    Ekonomik Gelir Siniflandirma modeli
    """
    __tablename__ = "gelir_siniflandirma"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    kodu = Column(String(24))
    aciklama = Column(String(240))

class GiderSiniflandirma(BASE_MODEL, ZopseduBase):
    """
    Ekonomik Gider Siniflandirma modeli
    """
    __tablename__ = "gider_siniflandirma"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    kodu = Column(String(24))
    aciklama = Column(String(240))