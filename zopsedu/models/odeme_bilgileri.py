from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class OdemeBilgileri(BASE_MODEL, ZopseduBase):
    __tablename__ = 'odeme_bilgileri'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))

    banka_adi = Column(String(100))
    sube_adi = Column(String(100))
    sube_kod = Column(Integer)
    hesap_no = Column(Integer)
    iban_no = Column(String(100))

    person = relationship("Person", uselist=False)