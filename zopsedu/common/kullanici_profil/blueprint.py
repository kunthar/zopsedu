"""KULLANICI PROFIL MODULÜ"""
from flask import Blueprint
from zopsedu.common.kullanici_profil.views import KullaniciProfilView

# pylint: disable=invalid-name
kullanici_profil_bp = Blueprint(
    "kullanici_profil",
    __name__,
    template_folder='templates/'
)
KullaniciProfilView.register(kullanici_profil_bp, route_base="/profil")

# pylint: enable=invalid-name
