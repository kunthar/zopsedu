""" Taslak Modeli"""
import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.custom_types import JSONEncodedDict


class TaslakTipleri(str, enum.Enum):
    """
    Taslak Tipi için oluşturulmuş enum alan
    """
    bap_proje_turu = "Proje Türü Taslağı"
    bap_proje_basvuru = "BAP Proje Başvuru"


class Taslak(BASE_MODEL, ZopseduBase):
    """Taslak Modeli"""
    __tablename__ = 'taslak'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    versiyon = Column(Integer)
    taslak_tipi = Column(Enum(TaslakTipleri))
    taslak = Column(JSONEncodedDict)

    user = relationship("User")
