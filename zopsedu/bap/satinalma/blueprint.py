""" Satınalma Modülü """

from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.bap.satinalma.views.avans_malzemeler import AvansMalzemelerView
from zopsedu.bap.satinalma.views.avans_talepleri import AvansTalepleriView
from zopsedu.bap.satinalma.views.muayene_teslim import MuayeneTeslimListesiView
from zopsedu.bap.satinalma.views.satinalinan_malzemeler_arama import SatinAlinanMalzemelerView
from zopsedu.bap.satinalma.views.satinalma_dashboard.satinalma_belgeler import SatinalmaBelgelerView
from zopsedu.bap.satinalma.views.satinalma_dashboard.satinalma_dashboard import SatinalmaDashboardView
from zopsedu.bap.satinalma.views.satinalma_dashboard.satinalma_urunler import SatinalmaUrunlerListesiView
from zopsedu.bap.satinalma.views.satinalma_dashboard.satinalma_yapilan_islemler import SatinalmaIslemGecmisiListesiView
from zopsedu.bap.satinalma.views.satinalma_dashboard.satinalma_firmalar import SatinalmaFirmalar
from zopsedu.bap.satinalma.views.satinalma_dashboard.muhasebe_fisi import SatinalmaMuhasebeFisleri
from zopsedu.bap.satinalma.views.satinalma_talepleri_arama import SatinAlmaTalepleriView
from zopsedu.bap.satinalma.views.teslimi_beklenen_firmalar import TeslimBeklenenFirmalarView

satinalma_blueprint = Blueprint(
    "satinalma",
    __name__,
    template_folder='templates/'
)

AvansMalzemelerView.register(satinalma_blueprint, route_base="/satinalma/avans-ile-alinan-malzemeler")
register_flaskview(satinalma_blueprint, AvansMalzemelerView)

AvansTalepleriView.register(satinalma_blueprint, route_base="/satinalma/avans-talepleri")
register_flaskview(satinalma_blueprint, AvansTalepleriView)

MuayeneTeslimListesiView.register(satinalma_blueprint, route_base="/satinalma/muayene-teslim-listesi")
register_flaskview(satinalma_blueprint, MuayeneTeslimListesiView)

SatinAlinanMalzemelerView.register(satinalma_blueprint, route_base="/satinalma/satinalinan-malzemeler")
register_flaskview(satinalma_blueprint, SatinAlinanMalzemelerView)

SatinAlmaTalepleriView.register(satinalma_blueprint, route_base="/satinalma/satinalma-talepleri")
register_flaskview(satinalma_blueprint, SatinAlmaTalepleriView)

TeslimBeklenenFirmalarView.register(satinalma_blueprint, route_base="/satinalma/teslim-beklenen-firmalar")
register_flaskview(satinalma_blueprint, TeslimBeklenenFirmalarView)

SatinalmaDashboardView.register(satinalma_blueprint, route_base="/satinalma/")
register_flaskview(satinalma_blueprint, SatinalmaDashboardView)

SatinalmaIslemGecmisiListesiView.register(satinalma_blueprint, route_base="/satinalma/")
register_flaskview(satinalma_blueprint, SatinalmaIslemGecmisiListesiView)

SatinalmaUrunlerListesiView.register(satinalma_blueprint, route_base="/satinalma/")
register_flaskview(satinalma_blueprint, SatinalmaUrunlerListesiView)

SatinalmaFirmalar.register(satinalma_blueprint, route_base="/satinalma/")
register_flaskview(satinalma_blueprint, SatinalmaFirmalar)

SatinalmaBelgelerView.register(satinalma_blueprint, route_base="/satinalma/")
register_flaskview(satinalma_blueprint, SatinalmaBelgelerView)

SatinalmaMuhasebeFisleri.register(satinalma_blueprint, route_base="/satinalma/")
register_flaskview(satinalma_blueprint, SatinalmaMuhasebeFisleri)
