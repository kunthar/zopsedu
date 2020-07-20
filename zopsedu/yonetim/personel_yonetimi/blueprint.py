"""

Personel Yonetimi Blueprint

"""
from flask import Blueprint
from flask_menu.classy import register_flaskview

from zopsedu.yonetim.personel_yonetimi.views.akademik_personel import AkademikPersonelView
from zopsedu.yonetim.personel_yonetimi.views.idari_personel import IdariPersonelView

personel_yonetimi_bp = Blueprint(
    "personel_yonetimi",
    __name__,
    template_folder='templates/'
)


AkademikPersonelView.register(personel_yonetimi_bp, route_base="/yonetim/personel-yonetimi/akademik")
register_flaskview(personel_yonetimi_bp, AkademikPersonelView)

IdariPersonelView.register(personel_yonetimi_bp, route_base="/yonetim/personel-yonetimi/idari")
register_flaskview(personel_yonetimi_bp, IdariPersonelView)

