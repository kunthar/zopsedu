from flask import render_template
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required
from flask_babel import gettext as _

from zopsedu.auth.lib import Permission, auth,Role
from zopsedu.auth.permissions import permission_dict


class DemirbasView(FlaskView):
    """Toplanti Gundem Viewi"""

    @staticmethod
    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_listeleme"]),
                      Role("BAP Yetkilisi"),
                      Role("BAP Admin")),
                   menu_registry={'path': '.bap.demirbas.demirbas_arama',
                                  'title': _("Demirbaş")})
    @route("/demirbas", methods=['GET'])
    def demirbas():
        return render_template("demirbas.html")

