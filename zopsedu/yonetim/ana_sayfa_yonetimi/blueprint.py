"""BAP YÖNETİMİ MODULÜ"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

# pylint: disable=invalid-name
from zopsedu.yonetim.ana_sayfa_yonetimi.views.bap_hakkinda_ayarlari import BapHakkindaAyarlarView
from zopsedu.yonetim.ana_sayfa_yonetimi.views.faaliyet_raporlari import BapFaaliyetRaporlariAyarlarView
from zopsedu.yonetim.ana_sayfa_yonetimi.views.formlar_ve_belgeler import FormlarVeBelgelerAyarlarView
from zopsedu.yonetim.ana_sayfa_yonetimi.views.mevzuat import MevzuatAyarlarView

ana_sayfa_yonetimi_bp = Blueprint(
    "ana_sayfa_yonetimi",
    __name__,
    template_folder='templates/'
)

BapFaaliyetRaporlariAyarlarView.register(ana_sayfa_yonetimi_bp, route_base="/ana-sayfa-yonetimi")
register_flaskview(ana_sayfa_yonetimi_bp, BapFaaliyetRaporlariAyarlarView)

MevzuatAyarlarView.register(ana_sayfa_yonetimi_bp, route_base="/ana-sayfa-yonetimi")
register_flaskview(ana_sayfa_yonetimi_bp, MevzuatAyarlarView)

FormlarVeBelgelerAyarlarView.register(ana_sayfa_yonetimi_bp, route_base="/ana-sayfa-yonetimi")
register_flaskview(ana_sayfa_yonetimi_bp, FormlarVeBelgelerAyarlarView)

BapHakkindaAyarlarView.register(ana_sayfa_yonetimi_bp, route_base="/ana-sayfa-yonetimi")
register_flaskview(ana_sayfa_yonetimi_bp, BapHakkindaAyarlarView)


