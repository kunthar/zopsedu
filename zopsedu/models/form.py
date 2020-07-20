"""Form Model"""
from sqlalchemy import Column, Boolean, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class Form(BASE_MODEL, ZopseduBase):
    """Simple form data model"""
    __tablename__ = 'forms'
    form_name = Column(String(80), primary_key=True)
    form_type = Column(String(80))
    form_import_path = Column(String(180))
    form_class_name = Column(String(60))
    will_explored = Column(Boolean(), nullable=False)
    will_listed = Column(Boolean(), nullable=False)

    def __repr__(self):
        return "Form:{}".format(self.form_name)
