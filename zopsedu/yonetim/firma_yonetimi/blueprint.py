"""Bap Firma Yönetimi modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

# pylint: disable=invalid-name
from zopsedu.yonetim.firma_yonetimi.views import BapFirmaView

firma_yonetimi_blueprint = Blueprint(
    'firma_yonetimi',
    __name__,
    template_folder='templates/',
)

BapFirmaView.register(firma_yonetimi_blueprint, route_base="/")
register_flaskview(firma_yonetimi_blueprint, BapFirmaView)
# pylint: enable=invalid-name
