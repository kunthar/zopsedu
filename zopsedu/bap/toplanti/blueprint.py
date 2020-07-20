"""Bap Toplanti modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview



# pylint: disable=invalid-name
from zopsedu.bap.toplanti.views.gundem import GundemView
from zopsedu.bap.toplanti.views.karar import ToplantiKararlariView
from zopsedu.bap.toplanti.views.toplanti import ToplantiOlusturView, ToplantiView

toplanti_blueprint = Blueprint(
    'toplanti',
    __name__,
    template_folder='templates',
    static_folder='static',
)


GundemView.register(toplanti_blueprint, route_base="/gundem")
register_flaskview(toplanti_blueprint, GundemView)
# pylint: enable=invalid-name

ToplantiOlusturView.register(toplanti_blueprint, route_base="/toplanti")
register_flaskview(toplanti_blueprint, ToplantiOlusturView)

ToplantiView.register(toplanti_blueprint, route_base='/toplanti')
register_flaskview(toplanti_blueprint, ToplantiView)

ToplantiKararlariView.register(toplanti_blueprint, route_base='/toplanti')
register_flaskview(toplanti_blueprint, ToplantiKararlariView)
