"""App State Modeli"""
from sqlalchemy import Column, String, Enum, Integer
from sqlalchemy.orm import relationship

from zopsedu.models.custom_types import JSONEncodedList
from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from .helpers import AppStates, StateTypes


class AppState(BASE_MODEL, ZopseduBase):
    """App state uygulama içerinde iş akışının tutulduğu modeldir."""

    __tablename__ = "app_state"
    id = Column(Integer, primary_key=True)
    universite_id = Column(Integer, default=0)
    state_type = Column(Enum(StateTypes))
    state_code = Column(String(16))
    module_name = Column(String(16))
    sub_module_name = Column(String(16))
    description = Column(String(120))
    current_app_state = Column(Enum(AppStates))
    possible_states = Column(JSONEncodedList)
    possible_actions = Column(JSONEncodedList)
    possible_template_types = Column(JSONEncodedList)

    app_state_stracker = relationship("AppStateTracker")
