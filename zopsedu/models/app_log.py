"""App Loggin Model"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.lib.decorators import no_crud_log


@no_crud_log
class AppLog(BASE_MODEL, ZopseduBase):
    """AppLog Modeli"""
    __tablename__ = 'app_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    url = Column(String)
    method = Column(String(20))
    request_details = Column(Text)
    remote_addr = Column(String)

    logger = Column(String)
    level = Column(String)
    msg = Column(String)
    details = Column(String)
    created_at = Column(Float)
