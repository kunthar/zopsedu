from sqlalchemy import Column, Integer, String

from zopsedu.lib.db import BASE_MODEL, ZopseduBase


class AppDemand(BASE_MODEL, ZopseduBase):
    """App demand uygulama içerisinde projeye yapılan taleplerin  tutulduğu modeldir."""

    __tablename__ = "app_demand"
    id = Column(Integer, primary_key=True)
    universite_id = Column(Integer, default=0)
    action_code = Column(String(16))
    module_name = Column(String(16))
    sub_module_name = Column(String(16))
    description = Column(String(120))


