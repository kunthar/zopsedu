"""BAP ProjeSozlemesi modeli modulu"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class ProjeSozlesmesi(ZopseduBase, BASE_MODEL):
    """
    ProjeSozlesmesi modeli
    """
    __tablename__ = "proje_sozlesmesi"
    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey("proje.id"))
    file_id = Column(Integer, ForeignKey("file.id"))
    file = relationship("File")
    proje = relationship("Proje", uselist=False)
