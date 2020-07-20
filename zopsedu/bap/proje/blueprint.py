"""PROJE MODULÜ"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.bap.proje.views.dashboard.proje_notlari import ProjeNotlariView
from zopsedu.bap.proje.views.dashboard.proje_hakemleri import ProjeHakemView
from zopsedu.bap.proje.views.dashboard.proje_satinalma_talepleri import ProjeSatinalmaTalepleriView
from zopsedu.bap.proje.views.hakem.hakem_oneri import HakemOneriView
from zopsedu.bap.proje.views.dashboard.dashboard import ProjeDashboardView
from zopsedu.bap.proje.views.dashboard.proje_personelleri import ProjePersonelView
from zopsedu.bap.proje.views.dashboard.sablon_ekdosyalar import ProjeSablonEkDosyaView
from zopsedu.bap.proje.views.dashboard.yurutucu_dashboard import ProjeYurutucuDashboard
from zopsedu.bap.proje.views.dashboard.degerlendirme import ProjeDegerlendirmeView
from zopsedu.bap.proje.views.basvuru.kaydet import ProjeBasvuruView
from zopsedu.bap.proje.views.basvuru.revizyon import ProjeRevizyon
from zopsedu.bap.proje.views.basvuru.personel import BasvuruPersonelView
from zopsedu.bap.proje.views.dashboard.islem_gecmisi import ProjeIslemGecmisiListesiView
from zopsedu.bap.proje.views.proje_arama.bap_projeleri_arama import BapProjeleriAramaView
from zopsedu.bap.proje.views.proje_arama.proje_arama import ProjeAramaView
from zopsedu.bap.proje.views.proje_arama.eski_projeler import EskiProjeler
from zopsedu.bap.proje.views.proje_arama.proje_yurutucusu_proje_arama import ProjeYurutucusuProjeAramaView
from zopsedu.bap.proje.views.dashboard.proje_raporlari import ProjeRaporView
from zopsedu.bap.proje.views.proje_turu.proje_turu import ProjeTuruView
from zopsedu.bap.proje.views.proje_turu.kaydet import ProjeTuruKaydetView
from zopsedu.bap.proje.views.proje_turu.guncelle import ProjeTuruGuncelleView
from zopsedu.bap.proje.views.proje_turu.taslak import ProjeTuruTaslakView
from zopsedu.bap.proje.views.dashboard.proje_mesajlari import ProjeMesajView
from zopsedu.bap.proje.views.dashboard.proje_kararlari import ProjeKararlariView

# pylint: disable=invalid-name

proje_bp = Blueprint(
    "proje",
    __name__,
    template_folder='templates/'
)

ProjeYurutucuDashboard.register(proje_bp, route_base="/proje/yurutucu/")
ProjeYurutucusuProjeAramaView.register(proje_bp, route_base="/proje/yurucutu/projelerim")

ProjeDashboardView.register(proje_bp, route_base="/proje")
ProjeDegerlendirmeView.register(proje_bp, route_base="/proje")
ProjePersonelView.register(proje_bp, route_base="/proje")
ProjeMesajView.register(proje_bp, route_base="/proje")
ProjeSablonEkDosyaView.register(proje_bp, route_base="/proje")
ProjeRaporView.register(proje_bp, route_base="/proje")
ProjeKararlariView.register(proje_bp, route_base="/proje")
ProjeIslemGecmisiListesiView.register(proje_bp, route_base="/proje")
ProjeNotlariView.register(proje_bp, route_base="/proje")
ProjeHakemView.register(proje_bp, route_base="/proje")

ProjeRevizyon.register(proje_bp, route_base="/proje")
ProjeBasvuruView.register(proje_bp, route_base="/proje")
ProjeAramaView.register(proje_bp, route_base="/proje/proje_arama")
EskiProjeler.register(proje_bp, route_base="/proje/eski-projeler")
ProjeTuruView.register(proje_bp, route_base="/proje/proje_turu")
ProjeTuruKaydetView.register(proje_bp, route_base="/proje/proje_turu")
ProjeTuruGuncelleView.register(proje_bp, route_base="/proje/proje_turu")
ProjeTuruTaslakView.register(proje_bp, route_base="/proje/proje_turu")
BasvuruPersonelView.register(proje_bp, route_base="/proje")
HakemOneriView.register(proje_bp, route_base="/proje")

BapProjeleriAramaView.register(proje_bp, route_base="/bap-projeleri")


ProjeSatinalmaTalepleriView.register(proje_bp, route_base="/proje")

register_flaskview(proje_bp, BapProjeleriAramaView)
register_flaskview(proje_bp, ProjeYurutucuDashboard)
register_flaskview(proje_bp, ProjeDashboardView)
register_flaskview(proje_bp, ProjeAramaView)
register_flaskview(proje_bp, EskiProjeler)
register_flaskview(proje_bp, ProjeYurutucusuProjeAramaView)
register_flaskview(proje_bp, ProjeRaporView)
register_flaskview(proje_bp, ProjeTuruView)
register_flaskview(proje_bp, ProjeTuruKaydetView)
register_flaskview(proje_bp, ProjeTuruGuncelleView)
register_flaskview(proje_bp, ProjeTuruTaslakView)
register_flaskview(proje_bp, ProjeMesajView)
register_flaskview(proje_bp, ProjeBasvuruView)
register_flaskview(proje_bp, ProjeRevizyon)
register_flaskview(proje_bp, ProjeKararlariView)
register_flaskview(proje_bp, ProjeIslemGecmisiListesiView)
register_flaskview(proje_bp, ProjeHakemView)
register_flaskview(proje_bp, BasvuruPersonelView)
register_flaskview(proje_bp, ProjeNotlariView)
register_flaskview(proje_bp, ProjeSatinalmaTalepleriView)


# pylint: enable=invalid-name



