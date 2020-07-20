from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class DetayliHesapPlanlari(BASE_MODEL, ZopseduBase):
    """
    Detaylı Hesap Planları

    """
    __tablename__ = "detayli_hesap_planlari"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    hesap_kodu = Column(String(18))
    kurum_turu=Column(Integer)
    ana_hesap_hesap_grubu_yardimci_hesap_adi = Column(String(150))
    kurum_adi = Column(String(120))
    saymanlik_kodu = Column(Integer)
