"""BAP Satinalma Yapilan işlemler modülü View Modulu"""

from flask import render_template, abort
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required
from sqlalchemy import or_

from zopsedu.auth.lib import Permission, auth, Role as RoleReq
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.satinalma.views.commons import get_satinalma_with_related_fields, \
    get_satinalma_next_states_info, \
    get_satinalma_actions_info
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import AppStateTracker, Person, AppState
from zopsedu.models.helpers import JobTypes


class SatinalmaIslemGecmisiListesiView(FlaskView):
    """
        Satinalma islem gecmisini listeleyen view
    """

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_islem_gecmisi_goruntuleme"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/islem-gecmisi', methods=['GET'],
           endpoint='satinalma_islem_gecmisi_listele')
    def satinalma_islem_gecmisi(self, satinalma_id):
        """
        Satinalma islem gecmisine ulasmak icin kullanilir
        :param satinalma_id: satinalma_id(int)
        :return: http response
        """
        params = {"satinalma_id": satinalma_id}

        try:
            satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
            states_info = get_satinalma_next_states_info(satinalma_id=satinalma_id)
            actions_info = get_satinalma_actions_info(satinalma_id=satinalma_id)
            proje = DB.session.query(Proje).filter(Proje.id == satinalma.proje_id).first()

            islem_listesi = DB.session.query(AppStateTracker). \
                filter(AppStateTracker.params.contains(params),
                       or_(AppStateTracker.job_type == JobTypes.satinalma_state_change,
                            AppStateTracker.job_type == JobTypes.satinalma_action)). \
                       join(Person, Person.user_id == AppStateTracker.triggered_by). \
                       join(AppState, AppStateTracker.state_id == AppState.id). \
                       add_columns(
                           AppState.state_code.label("state_code"),
                           Person.ad.label("person_ad"),
                           Person.soyad.label("person_soyad"),
                       ).all()

        except Exception as exc:
            CustomErrorHandler.error_handler(
                                             hata="Satinalma işlem geçmişi görüntülenirken hata oluştu."
                                                  "Hata: {}, Satinalma id: {}".format(satinalma_id,
                                                                                      exc)
                                             )
            return abort(500)

        return render_template("satinalma_dashboard/satinalma_yapilan_islemler.html",
                               islem_listesi=islem_listesi,
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               proje=proje,
                               actions_info=actions_info,
                               states_info=states_info)
