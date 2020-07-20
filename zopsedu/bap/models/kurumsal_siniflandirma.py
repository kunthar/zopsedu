from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class KurumsalSiniflandirma(BASE_MODEL, ZopseduBase):
    """
    Kurumsal Siniflandirma modeli
    """
    __tablename__ = "kurumsal_siniflandirma"

    id = Column(Integer, primary_key=True)
    kodu = Column(String(12))
    aciklama = Column(String(120))