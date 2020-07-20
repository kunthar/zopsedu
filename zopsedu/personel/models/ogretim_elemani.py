"""Ogretim Elemani modeli ve bağlantılı modellerden oluşur"""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


# todo: ozgecmis verileri cekildimi fieldi ekle ??
# pylint: disable=too-few-public-methods
class OgretimElemani(BASE_MODEL, ZopseduBase):
    """
    Ogretim Elemani modeli
    """
    __tablename__ = "ogretim_elemani"

    id = Column(Integer, primary_key=True)
    personel_id = Column(Integer, ForeignKey("personel.id", ondelete="CASCADE"))
    harici_ogretim_elamani_id = Column(Integer, ForeignKey("harici_ogretim_elemani.id"))
    unvan = Column(Integer, ForeignKey("hitap_unvan.id"))

    yok_ozgecmis_bilgileri_var_mi = Column(Boolean, default=False)
    ebys_id = Column(Integer)
    ozgemis_bilgileri_guncelleme_tarihi = Column(DateTime)

    personel = relationship('Personel', uselist=False, lazy='joined')
    hitap_unvan = relationship('HitapUnvan', uselist=False, lazy='joined')

    person = relationship('Person', secondary="personel", lazy="joined", uselist=False)

    akademik_gorevler = relationship("YoksisAkademikGorev",
                                     primaryjoin="and_(YoksisAkademikGorev.ogretim_elemani_id==OgretimElemani.id,"
                                                 "and_(YoksisAkademikGorev.AKTIF_PASIF== '1'))",
                                     lazy="raise")
    arasirma_sertifika_bilgileri = relationship("YoksisArastirmaSertifikaBilgisi",
                                                primaryjoin="and_(YoksisArastirmaSertifikaBilgisi.ogretim_elemani_id==OgretimElemani.id,"
                                                            "and_(YoksisArastirmaSertifikaBilgisi.AKTIF_PASIF== '1'))",
                                                lazy="raise")
    atiflari = relationship("YoksisAtifSayisi", lazy="raise")
    bildirileri = relationship("YoksisBildiri",
                               primaryjoin="and_(YoksisBildiri.ogretim_elemani_id==OgretimElemani.id,"
                                           "and_(YoksisBildiri.AKTIF_PASIF== '1'))",
                               lazy="raise")
    birlikte_calistigi_kisiler = relationship("YoksisBirlikteCalistigiKisi",
                                              lazy="raise")
    dersleri = relationship("YoksisDers",
                            primaryjoin="and_(YoksisDers.ogretim_elemani_id==OgretimElemani.id,"
                                        "and_(YoksisDers.AKTIF_PASIF== '1'))",
                            lazy="raise")
    editorlukleri = relationship("YoksisEditorlukBilgisi",
                                 primaryjoin="and_(YoksisEditorlukBilgisi.ogretim_elemani_id==OgretimElemani.id,"
                                             "and_(YoksisEditorlukBilgisi.AKTIF_PASIF== '1'))",
                                 lazy="raise")
    hakemlikleri = relationship("YoksisHakemlikBilgisi",
                                primaryjoin="and_(YoksisHakemlikBilgisi.ogretim_elemani_id==OgretimElemani.id,"
                                            "and_(YoksisHakemlikBilgisi.AKTIF_PASIF== '1'))",
                                lazy="raise")
    idari_gorevleri = relationship("YoksisIdariGorev",
                                   primaryjoin="and_(YoksisIdariGorev.ogretim_elemani_id==OgretimElemani.id,"
                                               "and_(YoksisIdariGorev.AKTIF_PASIF== '1'))",
                                   lazy="raise")
    kitaplari = relationship("YoksisKitap",
                             primaryjoin="and_(YoksisKitap.ogretim_elemani_id==OgretimElemani.id,"
                                         "and_(YoksisKitap.AKTIF_PASIF== '1'))",
                             lazy="raise")
    makaleleri = relationship("YoksisMakale",
                              primaryjoin="and_(YoksisMakale.ogretim_elemani_id==OgretimElemani.id,"
                                          "and_(YoksisMakale.AKTIF_PASIF== '1'))",
                              lazy="raise")
    odulleri = relationship("YoksisOdul")
    ogrenim_bilgileri = relationship("YoksisOgrenimBilgisi",
                                     primaryjoin="and_(YoksisOgrenimBilgisi.ogretim_elemani_id==OgretimElemani.id,"
                                                 "and_(YoksisOgrenimBilgisi.AKTIF_PASIF== '1'))",
                                     lazy="raise")
    patentleri = relationship("YoksisPatent",
                              primaryjoin="and_(YoksisPatent.ogretim_elemani_id==OgretimElemani.id,"
                                          "and_(YoksisPatent.AKTIF_PASIF== '1'))",
                              lazy="raise")
    projeleri = relationship("YoksisProje",
                             primaryjoin="and_(YoksisProje.ogretim_elemani_id==OgretimElemani.id,"
                                         "and_(YoksisProje.AKTIF_PASIF== '1'))",
                             lazy="raise")
    sanatsal_faaliyetleri = relationship("YoksisSanatsalFaaliyet",
                                         primaryjoin="and_(YoksisSanatsalFaaliyet.ogretim_elemani_id==OgretimElemani.id,"
                                                     "and_(YoksisSanatsalFaaliyet.AKTIF_PASIF== '1'))",
                                         lazy="raise")
    tasarim_bilgileri = relationship("YoksisTasarimBilgisi",
                                     primaryjoin="and_(YoksisTasarimBilgisi.ogretim_elemani_id==OgretimElemani.id,"
                                                 "and_(YoksisTasarimBilgisi.AKTIF_PASIF== '1'))")
    temel_alan_bilgileri = relationship("YoksisTemelAlanBilgisi",
                                        primaryjoin="and_(YoksisTemelAlanBilgisi.ogretim_elemani_id==OgretimElemani.id,"
                                                    "and_(YoksisTemelAlanBilgisi.AKTIF_PASIF== '1'))",
                                        lazy="raise")
    tesvik_basvurulari = relationship("YoksisTesvikBasvuru",
                                      lazy="raise")
    tesvik_beyanlari = relationship("YoksisTesvikBeyan",
                                    lazy="raise")
    uni_disi_deneyimleri = relationship("YoksisUniDisiDeneyim",
                                        primaryjoin="and_(YoksisUniDisiDeneyim.ogretim_elemani_id==OgretimElemani.id,"
                                                    "and_(YoksisUniDisiDeneyim.AKTIF_PASIF== '1'))",
                                        lazy="raise")
    uyelikleri = relationship("YoksisUyelik",
                              primaryjoin="and_(YoksisUyelik.ogretim_elemani_id==OgretimElemani.id,"
                                          "and_(YoksisUyelik.AKTIF_PASIF== '1'))",
                              lazy="raise")
    yabanci_dilleri = relationship("YoksisYabanciDil",
                                   primaryjoin="and_(YoksisYabanciDil.ogretim_elemani_id==OgretimElemani.id,"
                                               "and_(YoksisYabanciDil.AKTIF_PASIF== '1'))",
                                   lazy="raise")
    yazarliklari = relationship("YoksisYazar",
                                lazy="raise")
    yonettigi_tezler = relationship("YoksisYonetilenTez",
                                    primaryjoin="and_(YoksisYonetilenTez.ogretim_elemani_id==OgretimElemani.id,"
                                                "and_(YoksisYonetilenTez.AKTIF_PASIF== '1'))",
                                    lazy="raise")
