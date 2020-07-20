"""BAP belge data modeli modulu"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import validates, relationship
from flask_babel import lazy_gettext as _

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from .helpers import PROJE_BELGE_TURLERI, BAPBelgeTipi


class BAPBelge(ZopseduBase, BASE_MODEL):
    """
    Bap Dosya modeli

    adi: dosyanın adı
    aciklama: dosya için gerekli açıklama

    dosya: dosya

    """
    __tablename__ = "bap_belge"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("file.id"))

    adi = Column(String(255))
    aciklama = Column(String(255))
    tur = Column(Enum(BAPBelgeTipi))

    file = relationship("File")

    @staticmethod
    @validates("turler")
    def dosya_turu_format_kontrolu(field_name, field_value):
        """
        Args:
            field_name (str): turler
            field_value (str): format {},{},{} şeklinde olmalıdır

        Returns:
            (str) validated field value

        """
        # pylint: disable=unused-argument
        if field_value:
            turler = [tur.strip() for tur in field_value.split(",")]
            for tur in turler:
                if tur not in PROJE_BELGE_TURLERI:
                    raise ValueError(
                        _("Dosya turleri tur1,tur2,tur3 formatında olmalıdır.Gecerli dosya "
                          "turleri helper dosyasında PROJE_BELGE_TURLERI degişkeni içerisinde "
                          "belirtilmiştir.Lütfen kontrol ediniz"))
        return field_value
        # pylint: enable=unused-argument
