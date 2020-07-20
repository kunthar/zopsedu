""" Yetki Yönetimi """
from flask import Blueprint
from flask_menu.classy import register_flaskview

# pylint: disable=invalid-name
from zopsedu.yonetim.yetki_yonetimi.views.rol_atama import RolAtamaView
from zopsedu.yonetim.yetki_yonetimi.views.rol_yonetimi import RolView

yetki_yonetimi_bp = Blueprint(
    "yetki_yonetimi",
    __name__,
    template_folder='templates/'
)

RolView.register(yetki_yonetimi_bp, route_base="/yonetim/rol-yonetimi")
register_flaskview(yetki_yonetimi_bp, RolView)

RolAtamaView.register(yetki_yonetimi_bp, route_base="/yonetim/rol-atama")
register_flaskview(yetki_yonetimi_bp, RolAtamaView)