"""  Hata loglari Modülü """
import time
import json

from sqlalchemy.orm.exc import NoResultFound
from flask import render_template, request, jsonify, abort, url_for
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required
from sqlalchemy import desc

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.data_table_server import DataTableServer
from zopsedu.models import  AppLog
from zopsedu.lib.db import DB
from zopsedu.auth.lib import auth, Permission


class HataLoglariView(FlaskView):
    """Hata loglarini listeleyip detay olarak goruntuledigimiz view"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict['sistem_takibi']['hata_loglari']['hata_loglari_goruntuleme']),
                   menu_registry={"path": ".sistem_takibi.hata_loglari",
                                  "title": _("Hata Logları")})
    @route('listele', methods=['GET'])
    def hata_loglari():
        """Hata loglarini listeler"""
        # todo: pagination ozelligi eklenmesi gerekiyor.
        loglar = DB.session.query(AppLog).filter(
            AppLog.level == "ERROR").order_by(desc(AppLog.created_at)).all()
        return render_template("hata_loglari/hata_loglari.html", hata_loglari=loglar)

    @staticmethod
    @login_required
    @auth.requires(Permission("Hata Logları Görüntüleme", "Sistem Takibi",31))
    @route('listele/data', methods=['POST'])
    def hata_loglari_datatable():
        """Hata loglarini Datatable'a gonderir"""
        loglar = DB.session.query(AppLog).filter(
            AppLog.level == "ERROR")
        dts = DataTableServer(columns={
            0: AppLog.id,
            1: AppLog.created_at,
            2: AppLog.user_id,
            3: AppLog.remote_addr,
            4: AppLog.url,
            5: AppLog.method
        }, qry=loglar)
        result = dts.query(request)
        data = [[
            r.id,
            time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(r.created_at)),
            r.user_id,
            r.remote_addr if r.remote_addr else "-",
            r.url,
            r.method,
            f"""
                <a class="detail_arrow"
                href="{ url_for('sistem_takibi.hata_log_detay', log_id=r.id) }"><span
                class="fa fa-arrow-circle-right fa-2x "></span></a>
            """] for r in result.items]

        return jsonify({"data": data,
                        "recordsFiltered": result.total, "recordsTotal": result.filtered_from})

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict['sistem_takibi']['hata_loglari']['hata_loglari_goruntuleme']))
    @route('<int:log_id>/detay', methods=['GET'], endpoint='hata_log_detay')
    def hata_log_detay(log_id):
        """Hata logunun detayini goruntuler"""
        try:
            log = DB.session.query(AppLog).filter(AppLog.id == log_id).one()
        except NoResultFound:
            return abort(404)
        request_details = json.loads(log.request_details)
        return render_template("hata_loglari/hata_log_detay.html",
                               traceback=log.msg,
                               request_details=request_details,
                               log=log)
