"""Proje modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Numeric, Enum, Date, Text
from sqlalchemy.orm import relationship

from zopsedu.bap.models.proje_detay import ProjeHakemDavetDurumlari
from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.bap.models.helpers import  ProjeSuresiBirimi, ProjeBasvuruDurumu


class Proje(BASE_MODEL, ZopseduBase):
    """
    Proje modeli
    """
    __tablename__ = "proje"

    id = Column(Integer, primary_key=True)
    gelir_kasasi_id = Column(Integer, ForeignKey("gelir_kasalari.id"))
    # proje türü ile alakalı fieldlar
    user_id = Column(Integer, ForeignKey("users.id"))
    proje_turu = Column(Integer, ForeignKey("proje_turu.id"))
    proje_basvuru_durumu = Column(Enum(ProjeBasvuruDurumu))
    proje_turu_numarasi = Column(Integer)
    # proje_turu_kategorisi = Column(Enum(ProjeTuruKategorisi))

    proje_sozlesme_id = Column(Integer, ForeignKey("file.id"))
    proje_durumu_id = Column(Integer, ForeignKey("app_state.id"))

    proje_fakulte = Column(Integer, ForeignKey("birim.id"))
    proje_bolum = Column(Integer, ForeignKey("birim.id"))
    proje_ana_bilim_dali = Column(Integer, ForeignKey("birim.id"))
    proje_bilim_dali = Column(Integer, ForeignKey("birim.id"))

    # Başvuruda doldurulacak alanlar
    yurutucu = Column(Integer, ForeignKey("ogretim_elemani.id"))
    gerceklestirme_gorevlisi = Column(Integer, ForeignKey("personel.id"))
    harcama_yetkilisi = Column(Integer, ForeignKey("personel.id"))
    muhasebe_yetkilisi = Column(Integer, ForeignKey("personel.id"))

    onaylayan_yetkili_id = Column(Integer, ForeignKey("personel.id"))
    onay_tarihi = Column(Date)

    proje_disiplinler_arasi_mi = Column(Boolean)
    proje_suresi = Column(Integer)
    proje_suresi_birimi = Column(Enum(ProjeSuresiBirimi), default=ProjeSuresiBirimi.ay.name)
    etik_kurulu_izin_belgesi = Column(Boolean)

    # Komisyon kararıyla doldurulacak alanlar
    proje_no = Column(String(20))
    kabul_edilen_baslama_tarihi = Column(Date)
    kabul_edilen_butce = Column(Numeric(12, 2))
    klasor_sira_no = Column(Integer)

    proje_basligi = Column(String(250))
    project_title = Column(String(250), nullable=True)
    anahtar_kelimeler = Column(String(255))

    # sure = field.Integer(_(u"Süre(Ay Cinsinden Olmalıdır)"))
    teklif_edilen_baslama_tarihi = Column(Date)
    teklif_edilen_butce = Column(Numeric(12, 2))
    bitis_tarihi = Column(Date)

    ozet = Column(Text)
    literatur_ozet = Column(Text)
    amac_kapsam = Column(Text)
    gerec_yontem = Column(Text)
    arastirma_olanaklari = Column(Text)
    beklenen_bilimsel_katki = Column(Text)
    uygulama_plani = Column(Text)

    proje_mesajlari = relationship('Mesaj', secondary='proje_mesaj')
    proje_proje_turu = relationship("ProjeTuru", uselist=False)
    proje_yurutucu = relationship("OgretimElemani", foreign_keys=[yurutucu], uselist=False)
    proje_gerceklestirme_gorevlisi = relationship("Personel",
                                                  foreign_keys=[gerceklestirme_gorevlisi],
                                                  uselist=False)
    proje_harcama_yetkilisi = relationship("Personel", foreign_keys=[harcama_yetkilisi],
                                           uselist=False)
    proje_muhasebe_yetkilisi = relationship("Personel", foreign_keys=[muhasebe_yetkilisi],
                                            uselist=False)

    onaylayan_yetkili = relationship("Personel", foreign_keys=[onaylayan_yetkili_id],
                                     uselist=False)

    proje_durumu = relationship("AppState")
    proje_calisanlari = relationship("ProjeCalisanlari")
    proje_belgeleri = relationship("ProjeBelgeleri")
    proje_detayi = relationship('ProjeDetay', lazy='joined', uselist=False)
    # ProjeHakemleri arasindan proje degerlendirme teklifini kabul eden hakemleri getirir.
    kabul_edilen_proje_hakemleri = relationship(
        'ProjeHakemleri',
        primaryjoin="and_(ProjeHakemleri.proje_id==Proje.id,"
                    "     ProjeHakemleri.davet_durumu=='{}')".format(
            ProjeHakemDavetDurumlari.kabul_edildi.name),
        lazy='joined')
    proje_hakem_onerileri = relationship('HakemOneri', lazy='joined')
    proje_destekleyen_kurulus = relationship("ProjeDestekleyenKurulus",
                                             lazy='joined',
                                             uselist=False)
    proje_raporlari = relationship("ProjeRapor")
    proje_kalemleri = relationship("ProjeKalemi", lazy="joined")
    proje_notlari = relationship("ProjeNot")
    fakulte = relationship("Birim", foreign_keys=[proje_fakulte], uselist=False)
    bilim_dali = relationship("Birim", foreign_keys=[proje_bilim_dali], uselist=False)
    ana_bilim_dali = relationship("Birim", foreign_keys=[proje_ana_bilim_dali], uselist=False)
    bolum = relationship("Birim", foreign_keys=[proje_bolum], uselist=False)
    satinalma_talepleri = relationship("ProjeSatinAlmaTalebi")
    gelir_kasasi = relationship("GelirKasasi")


class EskiProje(BASE_MODEL, ZopseduBase):
    """
    Universitelerde bulunan eski sistemlerinden kalma kullanilmayan projelerin kaydedilecegi
    modeldir.
    """
    __tablename__ = "eski_projeler"

    id = Column(Integer, primary_key=True)
    no = Column(Integer)
    tipi = Column(String(25))
    baslik = Column(String(250))
    # yurutucu ad ve soyadi
    yurutucu_adi = Column(String(100))
    fakulte_ismi = Column(String(300))
    sure = Column(Integer)
    sure_birimi = Column(Enum(ProjeSuresiBirimi), default=ProjeSuresiBirimi.ay.name)
    butce = Column(Numeric(10, 2))
    baslama_tarihi = Column(Date)
