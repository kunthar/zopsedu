"""Proje satinalma talebi ile iliskili modelleri icerir"""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from sqlalchemy.orm import relationship


class ProjeSatinAlmaTalebi(BASE_MODEL, ZopseduBase):
    """
    Proje satın alma talebi
    Proje yurutucusunun proje icerisinde yaptigi satinalma taleplerinin tutuldugu modeldir
    """
    __tablename__ = 'proje_satinalma_talepleri'

    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey("proje.id"))
    durum_id = Column(Integer, ForeignKey("app_state.id"))
    duyuru_id = Column(Integer, ForeignKey("icerik.id"))
    duyuru_duzenlensin_mi = Column(Boolean, default=False)
    talep_numarasi = Column(String(20))

    ilgili_memur_id = Column(Integer, ForeignKey("personel.id"))
    butce_kalem_id = Column(Integer, ForeignKey("butce_kalemi.id"))

    # mkk = muayene ve kabul komisyonu
    mkk_baskan_id = Column(Integer, ForeignKey("ogretim_elemani.id"))
    mkk_uye1_id = Column(Integer, ForeignKey("ogretim_elemani.id"))
    mkk_uye2_id = Column(Integer, ForeignKey("ogretim_elemani.id"))
    mkk_yedek_baskan_id = Column(Integer, ForeignKey("ogretim_elemani.id"))
    mkk_yedek_uye1_id = Column(Integer, ForeignKey("ogretim_elemani.id"))
    mkk_yedek_uye2_id = Column(Integer, ForeignKey("ogretim_elemani.id"))

    talep_kalemleri = relationship("TalepKalemleri", lazy="joined")

    duyuru = relationship("Icerik")
    ilgili_memur = relationship("Personel")
    proje = relationship("Proje")
    durumu = relationship("AppState", lazy='joined')
    butce_kalemi = relationship("ButceKalemi", lazy='joined')

    mkk_baskan = relationship("OgretimElemani", foreign_keys=[mkk_baskan_id])
    mkk_uye1 = relationship("OgretimElemani", foreign_keys=[mkk_uye1_id])
    mkk_uye2 = relationship("OgretimElemani", foreign_keys=[mkk_uye2_id])
    mkk_yedek_baskan = relationship("OgretimElemani", foreign_keys=[mkk_yedek_baskan_id])
    mkk_yedek_uye1 = relationship("OgretimElemani", foreign_keys=[mkk_yedek_uye1_id])
    mkk_yedek_uye2 = relationship("OgretimElemani", foreign_keys=[mkk_yedek_uye2_id])

    def __repr__(self):
        return 'Satinalma Talepleri'


class TalepKalemleri(BASE_MODEL, ZopseduBase):
    """
    Proje satinalma talebi icerisinde bulunan talep kalemleri modeli
    Talep kalemleri satinalma icerisinde bulunan kalemler icin olusturur
    """
    __tablename__ = 'satinalma_talep_kalemleri'

    id = Column(Integer, primary_key=True)
    satinalma_id = Column(Integer, ForeignKey("proje_satinalma_talepleri.id"))
    proje_kalemi_id = Column(Integer, ForeignKey("proje_kalemleri.id"))
    teknik_sartname_file_id = Column(Integer, ForeignKey("file.id"))
    muhasebe_fis_id = Column(Integer, ForeignKey("muhasebe_fisleri.id"))

    talep_miktari = Column(Integer)
    teknik_sartname_duzenlensin_mi = Column(Boolean, default=False)

    satinalma_talebi = relationship("ProjeSatinAlmaTalebi")
    proje_kalemi = relationship("ProjeKalemi", lazy="joined")
    firma_teklif_kalemleri = relationship("FirmaTeklifKalemi")
    siparis_takip = relationship("SiparisTakip", uselist=False)
    muhasebe_fisi = relationship("MuhasebeFisi", uselist=False)
