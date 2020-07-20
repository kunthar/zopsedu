from flask import Blueprint
from flask_menu.classy import register_flaskview


# pylint: disable=invalid-name
from zopsedu.bap.bap_yetkilisi_dashboard.views import BapYetkilisiDashboardView

bap_yetkilisi_dashboard_blueprint = Blueprint(
    'bap_yetkilisi_dashboard',
    __name__,
    template_folder='templates',
    static_folder='static',
)
# pylint: enable=invalid-name

BapYetkilisiDashboardView.register(bap_yetkilisi_dashboard_blueprint,
                                   route_base='/')
register_flaskview(bap_yetkilisi_dashboard_blueprint, BapYetkilisiDashboardView)

