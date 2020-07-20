"""Proje Dashboard view classları"""
from flask import render_template
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required

from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.satinalma.views.commons import get_satinalma_with_related_fields, get_satinalma_next_states_info, \
    get_satinalma_actions_info, get_templates_info
from zopsedu.lib.db import DB


class SatinalmaBelgelerView(FlaskView):
    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["satinalma_belgeleri_goruntuleme"]),
               Or(Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:satinalma_id>/belgeler", methods=["GET", "POST"], endpoint="satinalma_belgeler")
    def satinalma_ozet(satinalma_id):

        satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
        states_info = get_satinalma_next_states_info(satinalma_id=satinalma_id)
        actions_info = get_satinalma_actions_info(satinalma_id=satinalma_id)
        proje = DB.session.query(Proje).filter(Proje.id == satinalma.proje_id).first()
        templates = get_templates_info(satinalma_id=satinalma_id)

        return render_template("satinalma_dashboard/satinalma_belgeler.html",
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               proje=proje,
                               actions_info=actions_info,
                               states_info=states_info,
                               templates=templates
                               )
