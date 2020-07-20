"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from zopsedu.auth.lib import auth
from zopsedu.bap.models.belge import BAPBelge
from zopsedu.bap.models.helpers import BAPBelgeTipi
from zopsedu.lib.db import DB


class BapFormBelgelerView(FlaskView):
    """Bap anasyafa formlar ve belgeler view classi"""

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.formlar_belgeler",
                                  "title": _("Formlar ve Belgeler"), "order": 6})
    @route('/formlar-belgeler', methods=['GET'])
    def bap_belgeler():
        dosyalar = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.formlar_ve_belgeler).all()
        return render_template("formlar_ve_belgeler.html",
                               dosyalar=dosyalar,
                               )
