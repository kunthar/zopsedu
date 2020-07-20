"""Mesaj blueprint modulu"""

from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.common.mesaj.views import MesajView

mesaj_blueprint = Blueprint(  # pylint: disable=invalid-name

    'mesaj',
    __name__,
    template_folder='templates',
    static_folder='static',
)

MesajView.register(mesaj_blueprint, route_base='/')
register_flaskview(mesaj_blueprint, MesajView)
