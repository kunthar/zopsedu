"""Person Modeli ve Bağlantılı Modellerinden Oluşur"""
import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class MedeniHali(str, enum.Enum):
    """Person medeni halini temsil eden enum class"""

    evli = "Evli"
    bekar = "Bekar"


class Cinsiyet(str, enum.Enum):
    """Person cinsiyetini temsil eden enum class"""

    erkek = "Erkek"
    kadin = "Kadın"


class KanGrubu(str, enum.Enum):
    """Person kan grubu temsil eden enum class"""

    sifir_negatif = "0Rh-"
    sifir_pozitif = "0Rh+"
    a_negatif = "ARh-"
    a_pozitif = "ARh+"
    b_negatif = "BRh-"
    b_pozitif = "BRh+"
    ab_negatif = "ABRh-"
    ab_pozitif = "ABRh+"


class Person(BASE_MODEL, ZopseduBase):
    """
    Person data model
    Sistemdeki kişilerin özlük ve iletişim bilgilerinin saklandığı modeldir.

    """
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ikametgah_adresi_id = Column(Integer, ForeignKey("adres.id"))
    ikincil_adres_id = Column(Integer, ForeignKey("adres.id"))

    ad = Column(String(50))
    soyad = Column(String(50))
    birincil_eposta = Column(String(80))
    ikincil_eposta = Column(String(80))

    tckn = Column(String(50))
    kimlik_cuzdani_seri = Column(String(20))
    kimlik_cuzdani_seri_no = Column(Integer)

    kayitli_oldugu_il = Column(String(50))
    kayitli_oldugu_ilce = Column(String(50))
    kayitli_oldugu_mahalle_koy = Column(String(50))
    kayitli_oldugu_cilt_no = Column(Integer)
    kayitli_oldugu_aile_sira_no = Column(Integer)
    kayitli_oldugu_sira_no = Column(Integer)

    kimlik_cuzdani_verildigi_yer = Column(String(50))
    kimlik_cuzdani_verilis_nedeni = Column(String(100))
    kimlik_cuzdani_kayit_no = Column(Integer)
    kimlik_cuzdani_verilis_tarihi = Column(Date())

    ana_adi = Column(String(50))
    baba_adi = Column(String(50))
    dogum_tarihi = Column(Date)
    dogum_yeri = Column(String(50))

    uyruk = Column(String(20))
    cinsiyet = Column(Enum(Cinsiyet))
    kan_grubu = Column(Enum(KanGrubu))
    medeni_hali = Column(Enum(MedeniHali))

    cep_telefonu = Column(String(25))
    ev_tel_no = Column(String(25))

    ehliyet = Column(String(20))

    user = relationship("User")
    personel = relationship("Personel", uselist=False)
    ogrenci = relationship("Ogrenci", uselist=False)
    harici_ogretim_elemani = relationship("HariciOgretimElemani", uselist=False)
    ikametgah_adresi = relationship("Adres", foreign_keys=[ikametgah_adresi_id], lazy='joined')
    ikincil_adres = relationship("Adres", foreign_keys=[ikincil_adres_id], lazy='joined')
    odeme_bilgileri = relationship("OdemeBilgileri")
