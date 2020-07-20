"""Ayar modelleri"""

from depot.fields.sqlalchemy import UploadedFileField
from flask import current_app
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import FernetEngine

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.lib.helpers import UploadedImageWithMaxDimensions
from zopsedu.models.custom_types import JSONEncodedDict


def get_key():
    return current_app.config["SECRET_KEY"]


class UploadedLogo(UploadedImageWithMaxDimensions):
    """
    Yuklenen resmin sizena gore kontrol yapar
    """

    max_width = 300
    max_height = 300


class SiteAyarlari(BASE_MODEL, ZopseduBase):
    """
    Site ayarlarının tutulduğu model.

    `params` şunun gibi olmalıdır:
    {
        "genel": {
            "site_adi": "Necmettin Erbakan Üniversitesi BAP Otomasyonu",
            "universite_adi": "Necmettin Erbakan Üniversitesi",
            "bap_kisa_adi": "N.E.Ü.",
            "sehir": "KONYA",
            "adres": "Necmettin Erbakan Üniversitesi Merap Tıp Fakültesi Morfoloji Binası Zemin Kat
                        Akyokuş/Meram/KONYA",
            "telefon": "03322237278",
            "faks": "03322237911",
        },
        "sozlesme_yetkilisi": {
            "gorevi": "Rektor Yardımcısı",
            "adi_soyadi": "Prof. Dr. Fevzi Tümsek",
            "eposta_imza": "\n\t\t\t\t\t----------------",
        },
        "diger": {
            "arastirmaci_unvanlari": ["Prof.Dr.", "Doç.Dr", "Dr.Öğr.Üyesi", "Dr."],
            "bilim_dallari": ["Fen Bilimleri", "Sağlık Bilimleri", "Sosyal Bilimler",
                                "Eğitim Bilimleri"],
            "proje_ilgili_alanlar": []
        }
    }

    """
    __tablename__ = 'site_ayar'
    id = Column(Integer, primary_key=True)
    module = Column(String)
    universite_id = Column(Integer)
    sub_module = Column(String)
    params = Column(JSONEncodedDict)

    # mail sunucusunun password u plaintext tutulamayacagi icin 'params'tan ayri konulmustur
    mail_password = Column(EncryptedType(String, get_key, FernetEngine))

    yoksis_password = Column(EncryptedType(String, get_key, FernetEngine))
    yoksis_kullanici_no = Column(String(30))

    deleted_at = Column(DateTime)
    deleted = Column(Boolean)
    logo = Column(UploadedFileField(
        upload_type=UploadedLogo))


class GenelAyarlar(BASE_MODEL, ZopseduBase):
    """
    Uygulama içerisinde kullanılacak ayarların tutuldugu model
    Ayarlar bölümlere ayrılarak json biciminde tutulur.
    Her bir modul icin icin mudul ismi + konu seklinde field eklenir.
    """
    __tablename__ = 'genel_ayarlar'
    id = Column(Integer, primary_key=True)
    universite_id = Column(Integer)
    bap_hakem = Column(JSON)
    bap_rapor = Column(JSON)
    bap_satinalma = Column(JSON)
    # ayarların proje ile ilgili olan bölümü
    # (destekleyen bilgileri, onaylayan bilgileri gibi fieldlarini icerir
    # genel proje turu ile bir baglantisi yoktur)
    bap_proje = Column(JSON)
    bap_sms = Column(JSON)
    bap_butce = Column(JSON)
    bap_email = Column(JSON)
    bap_ek_talep = Column(JSON)
    bap_diger = Column(JSON)

    aktif_mi = Column(Boolean, default=True)
