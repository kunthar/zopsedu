"""FARABİ MODULÜ"""

from flask import Blueprint

# pylint: disable=invalid-name

erasmus_forms_blueprint = Blueprint(
    'erasmus_form',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# pylint: enable=invalid-name