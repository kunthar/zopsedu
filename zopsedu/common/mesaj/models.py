"""Sistem bildirimleri icin mesaj modeli"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class MesajTipleri(str, enum.Enum):
    """
    Mesaj Tipleri
    """
    sistem = "Sistem"
    sms = "SMS"
    eposta = "EPOSTA"


class Mesaj(BASE_MODEL, ZopseduBase):
    """Mesaj Modeli"""
    __tablename__ = 'mesaj'

    id = Column(Integer, autoincrement=True, primary_key=True)
    proje_id = Column(Integer, ForeignKey('proje.id'))
    firma_id = Column(Integer, ForeignKey('bap_firma.id'))
    gonderen = Column(ForeignKey('person.id'))
    alici = Column(ForeignKey('person.id'))
    baslik = Column(String(150))
    metin = Column(Text)
    gonderim_zamani = Column(DateTime(), default=datetime.now())
    okunma_zamani = Column(DateTime())
    okunma_ip_adresi = Column(String(100))
    okundu = Column(Boolean, default=False)
    mesaj_tipi = Column(Enum(MesajTipleri))
    proje = relationship("Proje", uselist=False)
    firma = relationship("BapFirma", uselist=False)
    gonderen_kisi = relationship("Person", backref='gonderen_kisi', foreign_keys='Mesaj.gonderen')
    alici_kisi = relationship("Person", backref='alici_kisi', foreign_keys='Mesaj.alici')
    mesajek = relationship("MesajEk", backref='mesaj', lazy='joined', cascade='save-update, delete')
    #sadece proje mesajlari icin gecerlidir.


class MesajEk(BASE_MODEL, ZopseduBase):
    """Şablon dosyalarının saklandığı veri modeli"""
    __tablename__ = 'mesaj_ekleri'
    id = Column(Integer, autoincrement=True, primary_key=True)
    belge = Column(ForeignKey("file.id"))
    mesaj_id = Column(Integer, ForeignKey('mesaj.id'))
    belge_r = relationship("File", backref='belges', lazy='joined')
