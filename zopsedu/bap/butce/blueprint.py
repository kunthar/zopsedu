""" Bütçe Modülü """

from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.bap.butce.views.avans_verilen_projeler import AvansVerilenProjelerView
from zopsedu.bap.butce.views.butce_kodlari import ButceKodlariView
from zopsedu.bap.butce.views.genel_butce_ozeti import GenelButceOzetiView
from zopsedu.bap.butce.views.muhasebe_fisleri import MuhasebeFisleriView
from zopsedu.bap.butce.views.strateji_teslim import StratejiTeslimView

butce_blueprint = Blueprint(
    "butce",
    __name__,
    template_folder='templates/'
)

GenelButceOzetiView.register(butce_blueprint, route_base="/butce/genel-butce-ozeti")
register_flaskview(butce_blueprint, GenelButceOzetiView)

AvansVerilenProjelerView.register(butce_blueprint, route_base="/butce/avans-verilen-projeler")
register_flaskview(butce_blueprint, AvansVerilenProjelerView)

StratejiTeslimView.register(butce_blueprint, route_base="/butce/strateji-teslim")
register_flaskview(butce_blueprint, StratejiTeslimView)

ButceKodlariView.register(butce_blueprint, route_base="/butce/butce-kodlari")
register_flaskview(butce_blueprint, ButceKodlariView)

MuhasebeFisleriView.register(butce_blueprint, route_base="/butce/muhasebe-fisleri")
register_flaskview(butce_blueprint, MuhasebeFisleriView)
