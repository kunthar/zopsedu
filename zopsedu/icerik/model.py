"""İcerik ana modeli."""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models import WTFormEnum


class IcerikTipi(WTFormEnum):
    """Icerik tipini belirleyen enum class"""
    haber = "Haber"
    duyuru = "Duyuru"
    ozel_duyuru = "Özel Duyuru"
    etkinlik = "Etkinlik"
    satinalma = "Satın Alma"


class IcerikBirimTipi(WTFormEnum):
    """Icerigin birim tipini belirleyen enum class"""
    bap = "BAP"
    rektorluk = "Rektörlük"


class Icerik(BASE_MODEL, ZopseduBase):
    """
    Haber ve duyurular icin  kullanilacak icerik modeli.
    """
    __tablename__ = "icerik"

    id = Column(Integer, primary_key=True)
    ekleyen_id = Column(Integer, ForeignKey('users.id'))

    tipi = Column(Enum(IcerikTipi))
    birim_tipi = Column(Enum(IcerikBirimTipi))

    baslik = Column(String(255), nullable=False)
    icerik = Column(Text)
    # on sayfa gorunurlugu icerigin ana sayfada icerik ozeti kisminda gorunme durumunu belirler.
    on_sayfa_gorunurlugu = Column(Boolean, default=False)
    # aktiflik icerigin genel icerik listesinde gosterilme halini belirler.
    aktif_mi = Column(Boolean, default=True)

    # duyurunun listede son gorunme tarihi. bu tarihden sonra listeden kaldırılacaktır.
    bitis_tarihi = Column(DateTime)
    # duyurunun listede ilk gorunme tarihi. bu tarihten itibaren listede aktif olacaktir.
    baslangic_tarihi = Column(DateTime)

    ek_dosyalar = relationship("IcerikEkDosya")

    def __init__(self, *args, **kwargs):
        super(Icerik, self).__init__(*args, **kwargs)


class IcerikEkDosya(BASE_MODEL, ZopseduBase):
    """
    İcerigi iliskin ek dosyalarin tutuldugu modeldir.
    """
    __tablename__ = "icerik_ek_dosya"

    id = Column(Integer, primary_key=True)

    adi = Column(String(100))
    file_id = Column(Integer, ForeignKey("file.id"))
    icerik_id = Column(Integer, ForeignKey("icerik.id"))

    file = relationship("File")
