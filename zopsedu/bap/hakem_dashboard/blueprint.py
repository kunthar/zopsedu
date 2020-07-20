"""Hakem  proje degerlendirme blueprint modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview
from zopsedu.bap.hakem_dashboard.views import HakemDashboard

# pylint: disable=invalid-name
hakem_dashboard_blueprint = Blueprint(
    'hakem_dashboard',
    __name__,
    template_folder='templates',
    static_folder='static',
)
# pylint: enable=invalid-name

HakemDashboard.register(hakem_dashboard_blueprint, route_base='/hakem')
register_flaskview(hakem_dashboard_blueprint, HakemDashboard)
