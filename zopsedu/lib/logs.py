"""Custom LogHandler Sinifi"""
import json
import logging

from zopsedu.lib.db import DB
from zopsedu.models import AppLog


class LogHandler(logging.StreamHandler):
    """Custom LogHandler Sinifi"""

    def emit(self, record):
        """Olusan log mesajini DBye kaydeder."""

        if isinstance(record.msg, dict):
            msg = str(record.msg)
        elif isinstance(record.msg, ValueError):
            msg = str(record.msg)
        else:
            msg = record.msg

        details = {
            'file_name': record.filename,
            'line_no': record.lineno,
            'path_name': record.pathname,
        }
        if isinstance(record.args, tuple):
            record.args = {}

        log = AppLog(
            logger=record.name,
            level=record.levelname,
            msg=msg,
            details=json.dumps(details),
            created_at=record.created,
            **record.args
        )

        self.flush()
        DB.session.add(log)
        DB.session.commit()
