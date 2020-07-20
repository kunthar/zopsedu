"""FARABİ MODULÜ"""

from flask import Blueprint

# pylint: disable=invalid-name

farabi_form_blueprint = Blueprint(
    'farabi_form',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# pylint: enable=invalid-name