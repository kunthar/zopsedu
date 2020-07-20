"""Öğrenci Modellerinden ve Bağlantılı Modellerinden Oluşur"""
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class OzurDurumu(str, enum.Enum):
    """OzurDurumu Enum Class ı"""
    yok = "Yok"
    gorme_engelliler = "Görme Engelliler"
    isitme_engelliler = "İşitme Engelliler"
    fiziksel_engelliler = "Fiziksel Engelliler"
    dil_konusma_problemliler = "Dil ve Konuşma Problemliler"
    dikkat_eksikligi = "Dikkat Eksikliği (Hiperaktif)"
    psikolojik_problemler = "Psikolojik Problemliler"
    zihinsel_engelliler = "Zihinsel Engelliler"
    ogrenme_guclugu = "Öğrenme Güçlüğü"
    kronik_saglik_sorunlari = "Kronik Sağlık Sorunları"
    asperger_yuksek_fonksiyonlu_otistik = "Asperger veya Yüksek Fonksiyonlu Otistik Bireyler"
    gecici_yetersizlik = "Geçici Yetersizlikleri Olanlar"
    diger = "Diğer"


class OgrenimDurumu(str, enum.Enum):
    """OgrenimDurumu Enum Class ı"""
    okur_yazar = "Okuryazar"
    ilk_okul = "İlkokul"
    orta_okul = "Ortaokul"
    ilk_ogretim = "İlköğretim"
    lise = "Lise"
    meslek_lisesi = "Meslek Lisesi"
    yuksek_okul = "Yüksekokul"
    lisans_tamamlama = "Lisans Tamamlama"
    universite = "Üniversite"


class MasrafSponsor(str, enum.Enum):
    """MasrafSporsor Enum Class ı"""
    anne = "Anne"
    baba = "Baba"
    diger = "Diğer"


class Ogrenci(BASE_MODEL, ZopseduBase):
    """Ogrenci data model"""
    __tablename__ = 'ogrenci'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    aile_adres_id = Column(Integer, ForeignKey("adres.id"))

    baba_ogrenim_durumu = Column(Enum(OgrenimDurumu))
    baba_meslek = Column(String(50))
    baba_aylik_kazanc = Column(Integer)

    anne_ogrenim_durumu = Column(Enum(OgrenimDurumu))
    anne_meslek = Column(String(50))
    anne_aylik_kazanc = Column(Integer)

    masraf_sponsor = Column(Enum(MasrafSponsor))
    veli_emeklilik_durumu = Column(String(50))
    kiz_kardes_sayisi = Column(Integer)
    erkek_kardes_sayisi = Column(Integer)
    ogrenim_goren_kardes_sayisi = Column(Integer)
    burs_kredi_no = Column(Integer)
    aile_ev_tel = Column(String(25))
    aile_cep_telefonu = Column(String(25))
    ozur_durumu = Column(Enum(OzurDurumu))
    ozur_oran = Column(Integer, default=0)

    person = relationship("Person")
    aile_adresi = relationship("Adres")
    user = relationship("User", secondary="person", uselist=False, lazy='joined')
