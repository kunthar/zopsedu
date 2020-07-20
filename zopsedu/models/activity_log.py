"""Activity ve Crud Log Modelleri"""
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum

from zopsedu.models.custom_types import JSONEncodedList
from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.lib.decorators import no_crud_log


class CrudLogAction(str, enum.Enum):
    """
    Proje değerlendirme formu secenekleri
    """
    insert = 'Ekleme'
    update = 'Güncelleme'
    delete = 'Silme'


@no_crud_log
class AktiviteKaydi(BASE_MODEL, ZopseduBase):
    """Kullanici aktivite kaydinin tutuldugu model"""
    __tablename__ = 'activity_log'
    id = Column(Integer, primary_key=True)
    context = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    user_role_id = Column(Integer, ForeignKey("user_roles.id"))
    zaman = Column(DateTime)
    nesne = Column(String(50))
    nesne_id = Column(Integer)
    etkilenen_nesne = Column(String(50))
    etkilenen_nesne_id = Column(Integer)
    ekstra_mesaj = Column(String)
    session = Column(String)

    message_type = Column(Integer, nullable=False)
    username = Column(String(80))
    role_name = Column(String(100))

    # request ile alakali alanlar
    remote_ip = Column(String(50))
    tarayici_bilgisi = Column(String)
    host = Column(String(50))
    origin = Column(String(50))
    referer = Column(String)
    cookie = Column(String)
    endpoint_url = Column(String)
    method = Column(String(7))


@no_crud_log
class CrudKaydi(BASE_MODEL, ZopseduBase):
    """Veritabani aktivite kaydinin tutuldugu model"""
    __tablename__ = 'crud_log'
    id = Column(Integer, primary_key=True)
    context = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    user_role_id = Column(Integer, ForeignKey("user_roles.id"))
    zaman = Column(DateTime)
    nesne = Column(String(50))
    nesne_id = Column(Integer)
    nesne_ids = Column(JSONEncodedList)
    nesne_sayi = Column(Integer, default=1)
    aksiyon = Column(Enum(CrudLogAction))
