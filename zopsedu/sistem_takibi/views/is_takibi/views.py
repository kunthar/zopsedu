""" İş Takip Modülü """
import datetime

from flask import render_template, request, jsonify

from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required
from sqlalchemy import desc

from zopsedu.app import job_store
from zopsedu.lib.data_table_server import DataTableServer
from zopsedu.lib.db import DB
from zopsedu.auth.lib import auth, Role
from zopsedu.lib.job_handler import JobHandler
from zopsedu.models import AppStateTracker, AppState, Person


class IsTakipView(FlaskView):
    """Zamanlanmış işleri takip ekrani"""

    excluded_methods = [
        "qry"
    ]

    @property
    def qry(self):
        """AkademikPersonel BaseQuery"""

        return DB.session.query(AppStateTracker). \
            outerjoin(AppState, AppStateTracker.state_id == AppState.id). \
            outerjoin(job_store.jobs_t,
                      AppStateTracker.apscheduler_job_id == job_store.jobs_t.c.id). \
            join(Person, AppStateTracker.triggered_by == Person.user_id). \
            add_columns(
            AppStateTracker.id,
            AppStateTracker.apscheduler_job_id,
            AppState.state_code,
            AppStateTracker.description,
            AppStateTracker.params,
            AppStateTracker.date,
            AppStateTracker.job_type,
            Person.ad,
            Person.soyad,
            job_store.jobs_t.c.next_run_time
        ).order_by(desc(AppStateTracker.updated_at))

    @login_required
    @route('/data', methods=["POST"])
    @auth.requires(Role("BAP Admin"))
    def data_table(self):
        """
        Data table ajax sorgularini karsilayan method
        :return: json(Response)
        """

        dts = DataTableServer({
            0: AppState.state_code,
            1: AppStateTracker.description,
            2: AppStateTracker.params,
            3: AppStateTracker.date,
            4: Person.ad
        }, self.qry)
        result = dts.query(request)
        data = [[
            '{}'.format(r.state_code) if r.state_code else None,
            r.description,
            '{}'.format(r.params),
            '{:%d.%m.%Y}'.format(r.date),
            '{}'.format(datetime.datetime.fromtimestamp(int(r.next_run_time)).strftime(
                '%d.%m.%Y %H:%M:%S')) if r.next_run_time else None,
            '{} {}'.format(r.ad, r.soyad),
            '{}'.format(r.job_type.value),
            """                   <td class="sorting_1" tabindex="0">
                                            <span class="btn-group">
                                                  <a href="#"
                                                     class="btn btn-default">İşlemler</a>
                                                  <a href="#"
                                                     class="btn btn-default dropdown-toggle"
                                                     data-toggle="dropdown"></a>
                                                  <ul class="dropdown-menu pull-right">
                                                  <li>
                                                        <a onclick="is_baslat('{}');">
                                                            <button
                                                                    class="btn btn-link"
                                                                    style="white-space: normal;">Başlat
                                                            </button>
                                                        </a>
                                                      </li>
                                                      <li>
                                                        <a onclick="is_durdur('{}');">
                                                            <button
                                                                    class="btn btn-link"
                                                                    style="white-space: normal;">Durdur
                                                            </button>
                                                        </a>
                                                      </li>
                                                      <li>
                                                        <a onclick="is_sil('{}');">
                                                            <button
                                                                    class="btn btn-link"
                                                                    style="white-space: normal;">Sil
                                                            </button>
                                                        </a>
                                                      </li>
                                                  </ul>
                                            </span>
                                </td>
            
            """.format(r.apscheduler_job_id, r.apscheduler_job_id,
                       r.apscheduler_job_id) if r.apscheduler_job_id else None] for r in
            result.items]

        return jsonify(
            {"data": data, "recordsFiltered": result.total, "recordsTotal": result.filtered_from})

    @login_required
    @auth.requires(Role("BAP Admin"),
                   menu_registry={"path": ".sistem_takibi.is_takibi", "title": _("İş Takip")})
    @route("/is-listesi", methods=['GET'])
    def is_listele(self):
        """ Zamanlanmış işleri listeler"""

        qry = self.qry.limit(50)

        return render_template("is_takibi/is_listele.html", results=qry)

    @login_required
    @auth.requires(Role("BAP Admin"))
    @route("/is-bitir", methods=['POST'], endpoint='is_bitir')
    def is_bitir(self):
        """ Zamanlanmış işleri listeler"""
        job_id = request.get_json()['job_id']

        try:
            job_handler = JobHandler(remove_jobs=[job_id])
            job_handler.remove_job()
        except Exception as exc:
            return jsonify(status='error'), 500

        return jsonify(status='success')

    @login_required
    @auth.requires(Role("BAP Admin"))
    @route("/is-baslat", methods=['POST'], endpoint='is_baslat')
    def is_baslat(self):
        """ Zamanlanmış işleri listeler"""
        job_id = request.get_json()['job_id']

        try:
            job_handler = JobHandler(resume_jobs=[job_id])
            job_handler.resume_job()
        except Exception as exc:
            return jsonify(status='error'), 500

        return jsonify(status='success')

    @login_required
    @auth.requires(Role("BAP Admin"))
    @route("/is-durdur", methods=['POST'], endpoint='is_durdur')
    def is_durdur(self):
        """ Zamanlanmış işleri listeler"""
        job_id = request.get_json()['job_id']

        try:
            job_handler = JobHandler(pause_jobs=[job_id])
            job_handler.pause_job()
        except Exception as exc:
            return jsonify(status='error'), 500

        return jsonify(status='success')
