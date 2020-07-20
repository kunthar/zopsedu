from sqlalchemy import Column, Integer, ForeignKey, Date, Enum, String
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.helpers import SiparisDurumu


class SiparisTakip(BASE_MODEL, ZopseduBase):
    """
    Sipariş Takip modeli
    """
    __tablename__ = "siparis_takibi"

    id = Column(Integer, primary_key=True)
    satinalma_talep_kalemleri_id = Column(Integer, ForeignKey("satinalma_talep_kalemleri.id"))

    kazanan_firma_teklif_id = Column(Integer, ForeignKey("firma_teklif_kalemi.id"))

    siparis_numarasi = Column(String(20), unique=True)
    siparis_tarihi = Column(Date)
    teslim_edilmesi_beklenen_tarih = Column(Date)
    teslim_tarihi = Column(Date)
    # muayene kabul komisyonunun sonucunun(kabul/red) girilme tarihi
    kabul_tarihi = Column(Date)
    muayeneye_gonderilen_tarih = Column(Date)
    siparis_durumu = Column(Enum(SiparisDurumu))
    fatura_no = Column(String(25))
    fatura_tarihi = Column(Date)

    satinalma_talep_kalemleri = relationship("TalepKalemleri", uselist=False)
    kazanan_firma_teklif = relationship("FirmaTeklifKalemi", uselist=False)
