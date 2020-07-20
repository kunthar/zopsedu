"""BAP Eski Proje Modulu"""

from babel.numbers import format_currency
from flask import render_template, request, url_for, redirect, jsonify
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required
from flask_allows import And, Or

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.data_table_server import DataTableServer
from zopsedu.lib.db import DB
from zopsedu.models import EskiProje


class EskiProjeler(FlaskView):
    """
    Universitelerin eksi sistemlerinden kalma projelerle ilgili islemlerin yapildigi view
    """

    @staticmethod
    @login_required
    @auth.requires(And(Permission(*permission_dict["bap"]["proje"]["proje_arama"]["eski_projeleri_arama"]),
                       Or(Role("BAP Admin"),
                          Role("BAP Yetkilisi"))),
                   menu_registry={"path": ".bap.proje.eski_projeler",
                                  "title": _("Eski Projeler")})
    @route('listele', methods=['GET'])
    def eski_projeler_listele():
        """Eski projelerin listelendigi view"""
        # todo: pagination ozelligi eklenmesi gerekiyor.
        return render_template("proje_arama/eski_projeler_listele.html")

    @staticmethod
    @login_required
    @auth.requires(And(Permission(*permission_dict["bap"]["proje"]["proje_arama"]["eski_projeleri_goruntuleme"]),
                       Or(Role("BAP Admin"),
                          Role("BAP Yetkilisi"))))
    @route('listele/data', methods=['POST'])
    def eski_projeler_datatable():
        """Eski projeleri Datatable'a gonderir"""
        eski_projeler = DB.session.query(EskiProje)

        dts = DataTableServer(columns={
            0: EskiProje.id,
            1: EskiProje.no,
            2: EskiProje.tipi,
            3: EskiProje.baslik,
            4: EskiProje.yurutucu_adi,
            5: EskiProje.fakulte_ismi,
            6: EskiProje.sure,
            7: EskiProje.butce,
            8: EskiProje.baslama_tarihi
        }, qry=eski_projeler)

        eski_projeler = dts.query(request)
        data = [[
            eski_proje.id,
            eski_proje.no,
            eski_proje.tipi,
            eski_proje.baslik,
            eski_proje.yurutucu_adi,
            eski_proje.fakulte_ismi,
            "{sure} {sure_birimi}".format(sure=eski_proje.sure,
                                          sure_birimi=eski_proje.sure_birimi.value),
            float(eski_proje.butce),
            eski_proje.baslama_tarihi.strftime("%d.%m.%Y")
        ] for eski_proje in eski_projeler.items]

        return jsonify({"data": data,
                        "recordsFiltered": eski_projeler.total,
                        "recordsTotal": eski_projeler.filtered_from})

