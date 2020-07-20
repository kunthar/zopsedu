"""Yoksis blueprint"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.akademik_performans.views import YoksisView

# pylint: disable=invalid-name
akademik_performans_bp = Blueprint(
    "akademik_performans",
    __name__,
    template_folder='templates/'
)

YoksisView.register(akademik_performans_bp, route_base="/")
register_flaskview(akademik_performans_bp, YoksisView)


# pylint: enable=invalid-name
