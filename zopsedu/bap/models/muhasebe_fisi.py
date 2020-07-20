"""Muhasebe fisi modeli"""

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Numeric, Date

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class MuhasebeFisi(BASE_MODEL, ZopseduBase):
    """Muhasebe fisi modeli"""
    __tablename__ = 'muhasebe_fisleri'
    id = Column(Integer, primary_key=True)
    satinalma_talep_id = Column(Integer, ForeignKey("proje_satinalma_talepleri.id"))

    # logic icerisine otomatik olarak uretilmesi gerekiyor
    muhasebe_fis_no = Column(String(30))
    muhasebe_fis_tarihi = Column(Date)
    # ayarlardan gelecek
    muhasebe_birim_adi = Column(String(255))
    muhasebe_birim_kodu = Column(String(20))
    butce_yili = Column(String(4))
    # ayarlardan gelecek
    birim_adi = Column(String(255))
    birim_kodu = Column(String(20))
    # ayarlardan gelecek
    kurum_adi = Column(String(255))
    kurum_kodu = Column(String(20))
    # yetkilinin muhasebe fisi olustururken ekledigi birim
    proje_no = Column(String(20))
    # yurutucu ad soyad
    proje_yurutucusu = Column(String(255))
    # projenin yurutuldugu fakulte bolum
    fakulte_bolum = Column(String(500))

    # muhasebe fisi firma(dogrudan alim var ise bir kisi olabilir) alanlari
    # bu alanlar firmanin hesap bilgileri ile doldurulur. o anki hesap bilgilerinin
    # bir snapshot udur.
    ad_soyad = Column(String(50))
    unvan = Column(String(100))
    vergi_kimlik_no = Column(String(20))
    banka_sube = Column(String(50))
    banka_iban = Column(String(40))
    bagli_oldugu_vergi_dairesi = Column(String(255))

    fatura_no = Column(String(30))
    fatura_tarihi = Column(Date())
    fatura_aciklama = Column(String(1000))
    # odeme emrinin ciktisinin alinip alinmama durumunu gosterir. bu alan degeri true ise
    # guncelleme yapilamaz
    fis_tutari = Column(Numeric(14, 2))
    odeme_emri_tamamlandi = Column(Boolean, default=False)

    fis_maddeleri = relationship("MuhasebeFisMaddesi", lazy="joined")
    satinalma = relationship("ProjeSatinAlmaTalebi")


class MuhasebeFisMaddesi(BASE_MODEL, ZopseduBase):
    """Muhasebe fis maddesi modeli"""
    __tablename__ = 'muhasebe_fisi_maddeleri'

    id = Column(Integer, primary_key=True)
    muhasebe_fis_id = Column(Integer, ForeignKey("muhasebe_fisleri.id"))

    # hesap kodu 630, 600, 830, 150,255, 253 vb.
    hesap_kodu = Column(String(5))
    # 03.02.00.00, 03.07.00.00 vb.
    ekonomik_hesap_kodu = Column(String(30))

    # ayarlardan gelecek
    kurumsal_kod = Column(String(30))
    # ayarlardan gelecek
    fonksiyonel_kod = Column(String(30))
    # ayarlardan gelecek
    finans_kodu = Column(String(30))
    borc = Column(Numeric(14, 2), default=0.00)
    alacak = Column(Numeric(14, 2), default=0.00)
    # ilgili ozel butce detayli hesap planindan
    hesap_ayrinti_adi = Column(String(255))
