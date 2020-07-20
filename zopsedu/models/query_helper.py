"""QueryHelper Model"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from zopsedu.models.custom_types import JSONEncodedList
from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class QueryHelper(BASE_MODEL, ZopseduBase):
    """Simple query helper modeli"""
    __tablename__ = 'query_helper'
    id = Column(Integer, primary_key=True)
    module_name = Column(String(30))
    sub_module_name = Column(String(30))
    class_name = Column(String(50))
    import_path = Column(String(180))
    function_name = Column(String(60))
    function_arg_list = Column(JSONEncodedList)

    sablons = relationship("Sablon")
