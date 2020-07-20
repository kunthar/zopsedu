"""Ozgecmis modeli"""
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class Ozgecmis(BASE_MODEL, ZopseduBase):
    """Ozgecmis Modeli
    """
    __tablename__ = "ozgecmis"

    id = Column(Integer, primary_key=True)
    tecrube = Column(Text)
    file_id = Column(Integer, ForeignKey("file.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", uselist=False)
    file = relationship("File")
