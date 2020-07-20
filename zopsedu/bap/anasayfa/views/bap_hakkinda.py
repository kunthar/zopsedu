"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from zopsedu.auth.lib import auth
from zopsedu.bap.anasayfa.views.common import get_anasayfa_formlar, get_satinalma_duyurular, get_bap_duyurular


class BapHakkindaView(FlaskView):
    """Bap anasyafa hakkinda view classi"""


    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.bak_hakkinda",
                                  "title": _("BAP Hakkında"), "order": 7})
    @route('/hakkinda', methods=['GET'])
    def bap_hakkinda():
        return render_template("bap_hakkinda.html")
