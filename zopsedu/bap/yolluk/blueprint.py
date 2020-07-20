"""Bap Toplanti modulu"""
from flask import Blueprint
from flask_menu.classy import register_flaskview




from zopsedu.bap.yolluk.views import YollukView

yolluk_blueprint = Blueprint(
    'yolluk',
    __name__,
    template_folder='templates',
    static_folder='static',
)


YollukView.register(yolluk_blueprint, route_base="/")
register_flaskview(yolluk_blueprint, YollukView)
# pylint: enable=invalid-name

