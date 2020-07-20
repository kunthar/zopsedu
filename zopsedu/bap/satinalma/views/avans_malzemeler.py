from flask import render_template

from flask_classful import FlaskView, route
from flask_babel import gettext as _

from zopsedu.auth.lib import Permission, auth
from zopsedu.auth.permissions import permission_dict


class AvansMalzemelerView(FlaskView):
    """Bap Satinalma Avans ile alınan malzemeler view class"""

    # todo: implemente edilmedigi icin demodan dolayi yoruma alinmisti. permission hatasindan dolayi
    # todo: yorumdan kaldirilip menuden silindi.
    @staticmethod
    @route('/liste', methods=['GET'])
    # @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["avans_ile_alinan_malzemeler_listesi_goruntuleme"]),
    #                menu_registry={"path": ".bap.satinalma.avans_ile_alinan_malzemeler", "title": _("Avans ile Alınan Malzemeler")})
    @auth.requires(Permission(
        *permission_dict["bap"]["satinalma"]["avans_ile_alinan_malzemeler_listesi_goruntuleme"]))
    def avans_ile_alinan_malzemeler_listele():
        return render_template("avans_malzemeler.html")
