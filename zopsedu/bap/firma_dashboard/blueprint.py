"""Bap Firma modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

# pylint: disable=invalid-name
from zopsedu.bap.firma_dashboard.views.firma_islemleri import BapFirmaIslemleriView

firma_blueprint = Blueprint(
    'firma',
    __name__,
    template_folder='templates/',
)

BapFirmaIslemleriView.register(firma_blueprint, route_base="/firma")
register_flaskview(firma_blueprint, BapFirmaIslemleriView)
# pylint: enable=invalid-name
