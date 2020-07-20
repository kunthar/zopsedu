from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class TasinirKodlar(BASE_MODEL, ZopseduBase):
    """
    Taşınır Kod Listesi

    """
    __tablename__ = "tasinir_kodlar"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    kodu = Column(String(24))
    aciklama= Column(String(240))
    hesap_kodu=Column(Integer)