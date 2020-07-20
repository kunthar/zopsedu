from flask import render_template

from flask_classful import FlaskView, route
from flask_babel import gettext as _

from zopsedu.auth.lib import Permission, auth
from zopsedu.auth.permissions import permission_dict


class StratejiTeslimView(FlaskView):
    """Bap Strateji Teslim view classi"""

    # todo: implemente edilmedigi icin demodan dolayi yoruma alinmisti. permission hatasindan dolayi
    # todo: yorumdan kaldirilip menuden silindi.
    @staticmethod
    @route('/liste', methods=['GET'])
    # @auth.requires(Permission(*permission_dict["bap"]["butce"]["strateji_teslim_listesi_goruntuleme"]),
    #                menu_registry={"path": ".bap.butce.strateji_teslim_listesi", "title": _("Strateji Teslim Listesi")})
    @auth.requires(
        Permission(*permission_dict["bap"]["butce"]["strateji_teslim_listesi_goruntuleme"]))
    def strateji_teslimleri_listele():
        return render_template("strateji_teslimleri_listeleme.html")
