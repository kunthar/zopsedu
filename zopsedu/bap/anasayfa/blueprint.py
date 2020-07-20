"""Bap Anasayfa modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview
from zopsedu.bap.anasayfa.views.anasayfa import BapAnasayfaView

# pylint: disable=invalid-name
from zopsedu.bap.anasayfa.views.bap_hakkinda import BapHakkindaView
from zopsedu.bap.anasayfa.views.bap_komisyonu import BapKomisyonuView
from zopsedu.bap.anasayfa.views.faaliyet_raporlari import BapFaaliyetRaporlariView
from zopsedu.bap.anasayfa.views.form_belgeler import BapFormBelgelerView
from zopsedu.bap.anasayfa.views.iletisim import BapIletisimView
from zopsedu.bap.anasayfa.views.mevzuat import BapMevzuatView
from zopsedu.bap.anasayfa.views.yardim import BapYardimView

anasayfa_blueprint = Blueprint(
    'anasayfa',
    __name__,
    template_folder='templates/',
)
BapAnasayfaView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapAnasayfaView)

BapYardimView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapYardimView)

BapMevzuatView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapMevzuatView)

BapFormBelgelerView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapFormBelgelerView)

BapIletisimView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapIletisimView)

BapHakkindaView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapHakkindaView)

BapKomisyonuView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapKomisyonuView)


BapFaaliyetRaporlariView.register(anasayfa_blueprint, route_base="/")
register_flaskview(anasayfa_blueprint, BapFaaliyetRaporlariView)