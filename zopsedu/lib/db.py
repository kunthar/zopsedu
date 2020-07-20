"""DB related objects, Base Sqlalchemy Model"""
from datetime import datetime
from enum import Enum
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Date, DateTime, Column
from sqlalchemy import Enum as SqlEnum

BASE_MODEL = declarative_base()


class ZopseduBase(object):
    """Base Zopsedu Data Model"""

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    crud_log = True

    def __repr__(self):
        return 'Zopsedu Base Model'

    def to_dict(self, json_serializable=False):
        """
        Serialize model instance as dict

        Args:
            json_serializable (bool): if method return json serializable str or not

        Returns:
            (dict): serizalized model instance

        """
        obj = {}
        for k, col in self.__table__.columns.items():
            val = getattr(self, k, None)

            if json_serializable and val:
                if isinstance(col.type, (DateTime, Date)):
                    val = datetime.strftime(val, "%Y-%m-%d %H:%M:%S")

                if isinstance(col.type, Enum):
                    val = val.value

            obj[k] = val
        return obj

    def to_json(self):
        """
        Serialize model instance to `json`

        Returns:
            (str): json string

        """
        return json.dumps(self.to_dict(json_serializable=True))

    def update_obj_data(self, data):
        """

        Args:
            data (dict): dict contains data

        Returns:
            (self): model instance

        """
        for key, _ in self.__table__.columns.items():
            if key in data:
                val = data.get(key)
                attr = getattr(self, key)
                if isinstance(attr, Enum):
                    val = attr.__class__(val).name
                setattr(self, key, val)

    @classmethod
    def data_to_dict(cls, data):
        """
        Reduce the data dict based on models' columns.

        Args:
            data (dict): containing model data

        Returns:
            (dict): reduced dict

        """
        obj = {}
        for column_name, col in cls.__table__.columns.items():
            if column_name in data:
                val = data.get(column_name)
                if isinstance(col.type, SqlEnum):
                    val = col.type.enum_class(val).name
                obj[column_name] = val
        return obj


DB = SQLAlchemy(model_class=BASE_MODEL)
