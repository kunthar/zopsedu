"""YONETİM MODULÜ"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.sistem_takibi.views.gonderilmis_postalar.views import GonderilmisEpostalarView
from zopsedu.sistem_takibi.views.hata_loglari.views import HataLoglariView
from zopsedu.sistem_takibi.views.is_takibi.views import IsTakipView
from zopsedu.sistem_takibi.views.kayit_gecmisi.views import KayitGecmisiView

sistem_takibi_bp = Blueprint(
    "sistem_takibi",
    __name__,
    template_folder='templates/'
)



GonderilmisEpostalarView.register(sistem_takibi_bp, route_base="/sistem-takibi/gonderilmis-epostalar")
register_flaskview(sistem_takibi_bp, GonderilmisEpostalarView)

HataLoglariView.register(sistem_takibi_bp, route_base="/sistem-takibi/hata-loglari")
register_flaskview(sistem_takibi_bp, HataLoglariView)


IsTakipView.register(sistem_takibi_bp, route_base="/sistem-takibi/is-takibi")
register_flaskview(sistem_takibi_bp,IsTakipView)

KayitGecmisiView.register(sistem_takibi_bp, route_base="/sistem-takibi/kayit-gecmisi")
register_flaskview(sistem_takibi_bp,KayitGecmisiView)


# pylint: enable=invalid-name