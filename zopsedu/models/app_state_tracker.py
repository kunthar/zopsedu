"""App State Modeli"""
from sqlalchemy import Column, String, Enum, Integer, DateTime, ForeignKey, Unicode
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from .helpers import JobTypes


class AppStateTracker(BASE_MODEL, ZopseduBase):
    """App state uygulama içerinde iş akışının takip edildiği modeldir."""

    __tablename__ = "app_state_tracker"
    id = Column(Integer, primary_key=True)
    apscheduler_job_id = Column(Unicode(191, _warn_on_bytestring=False), ForeignKey("apscheduler_jobs.id", ondelete="SET NULL"), nullable=True)
    state_id = Column(Integer, ForeignKey("app_state.id"))
    params = Column(JSONB)
    date = Column(DateTime)
    description = Column(String(500))
    job_type = Column(Enum(JobTypes))
    triggered_by = Column(Integer)

    app_state = relationship("AppState")


