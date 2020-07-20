from flask import render_template

from flask_classful import FlaskView, route
from flask_babel import gettext as _

from zopsedu.auth.lib import Permission, auth
from zopsedu.auth.permissions import permission_dict


class AvansVerilenProjelerView(FlaskView):
    """Bap Bütçe Avans verilen Projeler view classi"""

    # todo: implemente edilmedigi icin demodan dolayi yoruma alinmisti. permission hatasindan dolayi
    # todo: yorumdan kaldirilip menuden silindi.
    @staticmethod
    @route('/liste', methods=['GET'])
    # @auth.requires(Permission(*permission_dict["bap"]["butce"]["avans_verilen_projeler_goruntuleme"]),
    #                menu_registry={"path": ".bap.butce.avans_verilen_projeler", "title": _("Avans Verilen Projeler")})
    @auth.requires(
        Permission(*permission_dict["bap"]["butce"]["avans_verilen_projeler_goruntuleme"]))
    def avans_verilen_projeler_listele():
        return render_template("avans_verilen_projeler_listeleme.html")
