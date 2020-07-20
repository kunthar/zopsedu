"""Bap Icerik modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview
from zopsedu.icerik.views.bap_duyuru import BapDuyuruView


# pylint: disable=invalid-name
icerik_blueprint = Blueprint(
    'icerik',
    __name__,
    template_folder='templates/',
)


BapDuyuruView.register(icerik_blueprint, route_base="/bap-duyuru")
register_flaskview(icerik_blueprint, BapDuyuruView)
# pylint: enable=invalid-name
