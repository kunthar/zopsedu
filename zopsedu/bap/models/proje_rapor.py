"""Proje modeli ve bağlantılı modellerden oluşur"""
import enum

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship

from zopsedu.bap.models.helpers import ProjeDegerlendirmeSonuc
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class ProjeRaporDurumu(str, enum.Enum):
    """Proje Raporunun tamamlanma durumu"""
    tamamlandi = 'Tamamlandı'
    tamamlanmadi = 'Tamamlanmadı'


class ProjeRaporTipi(str, enum.Enum):
    """Projen Raporunun tipi"""
    ara_rapor = 'Ara Rapor'
    sonuc_raporu = 'Sonuc Raporu'
    proje_basvuru = 'Proje Başvuru'


class ProjeRapor(BASE_MODEL, ZopseduBase):
    """
    Proje Raporlari modeli
    """
    __tablename__ = "proje_rapor"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'))
    proje_id = Column(Integer, ForeignKey('proje.id'))

    rapor_tipi = Column(Enum(ProjeRaporTipi))
    rapor_icerigi = Column(Text)

    rapor_baslangic_tarihi = Column(DateTime)
    rapor_bitis_tarihi = Column(DateTime)

    durumu = Column(Enum(ProjeRaporDurumu), default=ProjeRaporDurumu.tamamlanmadi)
    duzenlenebilir_mi = Column(Boolean, default=False)

    rapor_degerlendirme_durumu = Column(Enum(ProjeDegerlendirmeSonuc),
                                        default=ProjeDegerlendirmeSonuc.degerlendirilmedi)

    file = relationship("File", uselist=False)
    proje = relationship('Proje')
