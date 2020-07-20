"""Dosya kayıtlarının tutulduğu model"""
from io import BytesIO

from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.lib.helpers import AllowedUploadedFile


class File(BASE_MODEL, ZopseduBase):
    """Dosyalın saklandığı model"""
    __tablename__ = 'file'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column('content',
                     UploadedFileField(upload_storage="local", upload_type=AllowedUploadedFile))
    uploaded_at = Column(DateTime)

    user = relationship("User")

    @property
    def file_object(self):
        """Kaydedilen contenti file like object olarak geri dondurur."""
        fobj = BytesIO()
        fobj.write(self.content.file.read())
        fobj.seek(0)
        return fobj
