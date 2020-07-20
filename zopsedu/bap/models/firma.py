"""Firma modelinden oluşur"""
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class BapFirma(BASE_MODEL, ZopseduBase):
    """
    Firma modeli
    """
    __tablename__ = "bap_firma"

    id = Column(Integer, primary_key=True)
    firma_faaliyet_belgesi_id = Column(ForeignKey("file.id"))
    vergi_dairesi_id = Column(ForeignKey("vergi_dairesi.id"))
    user_id = Column(Integer, ForeignKey('users.id'))

    adres = Column(String(500))
    adi = Column(String(500))
    telefon = Column(String(25))
    email = Column(String(80))
    vergi_kimlik_numarasi = Column(String(20))
    faaliyet_belgesi_verilis_tarihi = Column(Date)

    iban = Column(String(30))
    banka_sube_adi = Column(String(255))

    yetkili_adi = Column(String(50))
    yetkili_soyadi = Column(String(50))

    onaylandi = Column(Boolean, default=False)
    faaliyet_durumu = Column(Boolean, default=False)
    reddedildi_mi = Column(Boolean, default=False)

    user = relationship('User', uselist=False)
    firma_mesajlari = relationship('Mesaj', secondary='firma_mesaj')
    firma_teklifleri = relationship('FirmaSatinalmaTeklif', lazy="joined")

    vergi_dairesi = relationship("VergiDairesi")

    @property
    def yetkili_ad_soyad(self):
        return self.yetkili_adi + ' ' + self.yetkili_soyadi
