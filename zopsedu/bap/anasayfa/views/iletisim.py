"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from zopsedu.auth.lib import auth
from zopsedu.bap.anasayfa.views.common import get_anasayfa_formlar, get_satinalma_duyurular, get_bap_duyurular


class BapIletisimView(FlaskView):
    """Bap anasyafa iletisim view classi"""

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.bap_iletisim",
                                  "title": _("İletişim"), "order": 9})
    @route('/iletisim', methods=['GET'])
    def bap_iletisim():
        return render_template("iletisim.html")
