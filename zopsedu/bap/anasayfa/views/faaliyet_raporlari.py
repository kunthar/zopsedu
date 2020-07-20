"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from zopsedu.auth.lib import auth
from zopsedu.bap.anasayfa.views.common import get_anasayfa_formlar, get_satinalma_duyurular, get_bap_duyurular
from zopsedu.bap.models.belge import BAPBelge
from zopsedu.bap.models.helpers import BAPBelgeTipi
from zopsedu.lib.db import DB


class BapFaaliyetRaporlariView(FlaskView):
    """Bap anasyafa faaliyet raporlari view classi"""


    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.bap_rapor",
                                  "title": _("BAP Raporları"), "order": 8})
    @route('/faaliyet_raporlari', methods=['GET'])
    def bap_rapor():
        dosyalar = DB.session.query(BAPBelge).filter(BAPBelge.tur == BAPBelgeTipi.faaliyet_raporlari).all()
        return render_template("faaliyet_raporlari.html",
                               dosyalar=dosyalar)
