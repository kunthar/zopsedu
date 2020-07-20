"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from zopsedu.auth.lib import auth
from zopsedu.bap.anasayfa.views.common import get_anasayfa_formlar, get_satinalma_duyurular, get_bap_duyurular
from zopsedu.bap.models.belge import BAPBelge
from zopsedu.bap.models.helpers import BAPBelgeTipi
from zopsedu.lib.db import DB


class BapMevzuatView(FlaskView):
    """Bap anasyafa mevzuat view classi"""

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.mevuzat",
                                  "title": _("Mevzuat"), "order": 12})
    @route('/mevzuat', methods=['GET'])
    def bap_mevzuat():
        dosyalar = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.mevzuat).all()
        return render_template("mevzuat.html",
                               dosyalar=dosyalar)
