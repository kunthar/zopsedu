"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route
from zopsedu.auth.lib import auth
from zopsedu.bap.anasayfa.views.common import get_anasayfa_formlar, get_satinalma_duyurular, get_bap_duyurular


class BapYardimView(FlaskView):
    """Bap anasyafa yardım view classi"""

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.yardim",
                                  "title": _("Yardım"), "order": 11})
    @route('/yardim', methods=['GET'])
    def bap_yardim():
        anasayfa_formlar = get_anasayfa_formlar()
        satinalma_duyurular = get_satinalma_duyurular()
        bap_duyurular = get_bap_duyurular()
        return render_template("anasayfa_yapim_asamasinda.html",
                               anasayfa_formlar=anasayfa_formlar,
                               satinalma_duyurular=satinalma_duyurular,
                               bap_duyurular=bap_duyurular)



