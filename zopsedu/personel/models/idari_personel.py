# todo: ozgecmis verileri cekildimi fieldi ekle ??
# pylint: disable=too-few-public-methods

from sqlalchemy import Column, Integer, ForeignKey, Enum, String, Boolean

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.helpers import BapIdariUnvan


class BapIdariPersonel(BASE_MODEL, ZopseduBase):
    """
    Ogretim Elemani modeli
    """
    __tablename__ = "bap_idari_personel"

    id = Column(Integer, primary_key=True)
    ebys_id = Column(Integer)
    personel_id = Column(Integer, ForeignKey("personel.id"))
    gorevi = Column(Enum(BapIdariUnvan))
    gorev_aciklamasi = Column(String(255))
    gorevde_mi = Column(Boolean, default=True)



