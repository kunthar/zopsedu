"""Firma teklif modeli"""
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Enum, Boolean
from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from sqlalchemy.orm import relationship

from zopsedu.lib.helpers import WTFormEnum


class DosyaKategori(str, WTFormEnum):
    """
        Firmanin satinalmaya yapacagi teklife yukleyebilecegi dosyların turlerini belirtir
    """
    teklif_mektubu = "Teklif Mektubu"
    teknik_sartname_cevap_metni = "Teknik Şartname Cevap Metni"
    urun_katalog = "Ürün Kataloğu"
    teknik_ozellik = "Teknik Özellik"
    diger = "Diğer"


class TeknikSartnameUygunlukDegerlendirmesi(str, WTFormEnum):
    """Firma teklif kaleminin teknik şartnameye uygunluk durumlarinin tutuldugu enum class"""
    degerlendirilmedi = "Değerlendirilmedi"
    uygun = "Teknik Şartnameye Uygundur"
    uygun_degil = "Teknik Şartnameye Uygun Değil"


class FirmaSatinalmaTeklif(BASE_MODEL, ZopseduBase):
    """
    Firmanin satinalmatalebine yaptigi teklifin kaydedildigi modeldir
    """
    __tablename__ = 'firma_satinalma_teklif'
    id = Column(Integer, primary_key=True)
    firma_id = Column(Integer, ForeignKey('bap_firma.id'))
    satinalma_id = Column(Integer, ForeignKey("proje_satinalma_talepleri.id"))
    aciklama = Column(String(500))
    teklif_tamamlandi_mi = Column(Boolean, default=False)

    teklif_kalemleri = relationship("FirmaTeklifKalemi", lazy="joined")
    teklif_dosyalari = relationship("FirmaTeklifDosya", lazy="joined")
    satinalma = relationship("ProjeSatinAlmaTalebi", lazy="joined")
    firma = relationship("BapFirma", lazy="joined")


class FirmaTeklifKalemi(BASE_MODEL, ZopseduBase):
    """
    Firma teklifi modeli
    Firmalarin bir satinalma talep kalemine yaptigi teklifin tutuldugu modeldir
    """
    __tablename__ = 'firma_teklif_kalemi'
    id = Column(Integer, primary_key=True)
    satinalma_talep_kalemi_id = Column(Integer, ForeignKey("satinalma_talep_kalemleri.id"))
    teklif_id = Column(Integer, ForeignKey('firma_satinalma_teklif.id'))

    marka_model = Column(String(255))
    kdv_orani = Column(Numeric(5, 2))
    teklif = Column(Numeric(12, 2))
    # teslimat suresi gun cinsindendir.
    teslimat_suresi = Column(Integer)
    teknik_sartname_uygunlugu = Column(Enum(TeknikSartnameUygunlukDegerlendirmesi),
                                       default=TeknikSartnameUygunlukDegerlendirmesi.degerlendirilmedi)

    satinalma_talep_kalemi = relationship("TalepKalemleri")
    satinalma_teklif = relationship("FirmaSatinalmaTeklif")


class FirmaTeklifDosya(BASE_MODEL, ZopseduBase):
    """
    Satinalmaya yapilan firma teklifine eklenmis dosyalarin tutuldugu model
    """
    __tablename__ = 'firma_teklif_dosya'
    id = Column(Integer, primary_key=True)
    teklif_id = Column(Integer, ForeignKey('firma_satinalma_teklif.id'))
    file_id = Column(Integer, ForeignKey('file.id'))

    aciklama = Column(String(100))
    dosya_kategori = Column(Enum(DosyaKategori))
