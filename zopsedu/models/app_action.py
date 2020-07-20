from sqlalchemy import Column, Integer, String, Enum

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.helpers import ActionTypes


class AppAction(BASE_MODEL, ZopseduBase):
    """App Action uygulama içerisinde projeye için yapılan işlemlerin tanımlarının yapıldığı modeldir."""

    __tablename__ = "app_action"
    id = Column(Integer, primary_key=True)
    universite_id = Column(Integer, default=0)
    action_type = Column(Enum(ActionTypes))
    action_code = Column(String(16))
    module_name = Column(String(16))
    sub_module_name = Column(String(16))
    description = Column(String(120))
