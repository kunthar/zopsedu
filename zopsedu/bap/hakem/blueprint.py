"""HAKEM KAYIT VE ARAMA MODULÜ"""
from flask import Blueprint
from flask_menu.classy import register_flaskview
from zopsedu.bap.hakem.views import HakemView

# pylint: disable=invalid-name
hakem_bp = Blueprint(
    "hakem",
    __name__,
    template_folder='templates/'
)

HakemView.register(hakem_bp, route_base="/hakem")
register_flaskview(hakem_bp, HakemView)

# pylint: enable=invalid-name
