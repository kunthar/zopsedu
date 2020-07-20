"""MEVLANA MODÜLÜ"""

from flask import Blueprint


# pylint: disable=invalid-name
mevlana_blueprint = Blueprint(
    'mevlana',
    __name__,
    template_folder='templates',
    static_folder='static',
)
# pylint: enable=invalid-name
