"""BAP YÖNETİMİ MODULÜ"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

# pylint: disable=invalid-name
from zopsedu.yonetim.bap_yonetimi.views.diger import DigerAyarlariView
from zopsedu.yonetim.bap_yonetimi.views.gundem_sablonlari import GundemSablonlariView
from zopsedu.yonetim.bap_yonetimi.views.hakem import HakemAyarlarView
from zopsedu.yonetim.bap_yonetimi.views.otomasyon_ayarlari import AyarlarView
from zopsedu.yonetim.bap_yonetimi.views.sablon import SablonlarView

bap_yonetimi_bp = Blueprint(
    "bap_yonetimi",
    __name__,
    template_folder='templates/'
)

AyarlarView.register(bap_yonetimi_bp, route_base="/bap-yonetimi")
register_flaskview(bap_yonetimi_bp, AyarlarView)

SablonlarView.register(bap_yonetimi_bp, route_base="/bap-yonetimi")
register_flaskview(bap_yonetimi_bp, SablonlarView)

HakemAyarlarView.register(bap_yonetimi_bp, route_base="/bap-yonetimi")
register_flaskview(bap_yonetimi_bp, HakemAyarlarView)

DigerAyarlariView.register(bap_yonetimi_bp, route_base="/bap-yonetimi")
register_flaskview(bap_yonetimi_bp, DigerAyarlariView)

GundemSablonlariView.register(bap_yonetimi_bp, route_base='/bap-yonetimi/gundem-sablonlari')
register_flaskview(bap_yonetimi_bp, GundemSablonlariView)

# pylint: enable=invalid-name
