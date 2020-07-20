"""Bap Toplanti modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.bap.demirbas.views import DemirbasView

demirbas_blueprint = Blueprint(
    'demirbas',
    __name__,
    template_folder='templates',
    static_folder='static',
)

DemirbasView.register(demirbas_blueprint, route_base="/")
register_flaskview(demirbas_blueprint, DemirbasView)
# pylint: enable=invalid-name