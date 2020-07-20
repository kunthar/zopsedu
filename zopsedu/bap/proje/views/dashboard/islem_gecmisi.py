"""BAP Proje yapilan İşlem Geçmişi Modulu"""
from flask import render_template, abort
from flask_allows import And, Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import Permission, auth, Role as RoleReq
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import ProjeYurutucusu
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import AppStateTracker, Person, AppState
from zopsedu.models.helpers import JobTypes
from zopsedu.bap.proje.views.dashboard.common import get_next_states_info, get_actions_info
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeIslemGecmisiListesiView(FlaskView):
    """
        Proje islem gecmisini listeleyen view
    """

    @login_required
    @auth.requires(
        Or(And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["islem_gecmisi_goruntuleme"]),
               ProjeYurutucusu()), RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:proje_id>/dashboard/islem-gecmisi', methods=['GET'],
           endpoint='proje_islem_gecmisi_listele')
    def islem_gecmisi(self, proje_id):
        """
        Projenin islem gecmisine ulasmak icin kullanilir
        :param proje_id: proje_id(int)
        :return: http response
        """
        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        params = {"proje_id": proje_id}
        try:
            proje = DB.session.query(Proje).options(
                joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                    OgretimElemani.personel).load_only("id").joinedload(
                    Personel.person).load_only("ad", "soyad"),
                lazyload(Proje.proje_detayi),
                lazyload(Proje.kabul_edilen_proje_hakemleri),
                lazyload(Proje.proje_hakem_onerileri),
                lazyload(Proje.proje_destekleyen_kurulus),
                lazyload(Proje.proje_kalemleri),
            ).filter(Proje.id == proje_id, or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                                               Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

            next_states_info = get_next_states_info(proje_id=proje_id)
            actions_info = get_actions_info(proje_id=proje_id)

            islem_listesi = DB.session.query(AppStateTracker). \
                filter(AppStateTracker.params.contains(params),
                       or_(AppStateTracker.job_type == JobTypes.project_state_change,
                            AppStateTracker.job_type == JobTypes.project_action)). \
                       join(Person, Person.user_id == AppStateTracker.triggered_by). \
                       join(AppState, AppStateTracker.state_id == AppState.id). \
                       add_columns(
                           AppState.state_code,
                           Person.ad,
                           Person.soyad,
                       ).all()

        except Exception as exc:
            CustomErrorHandler.error_handler(
                                             hata="Proje işlem geçmişi görüntülenirken hata oluştu."
                                                  "Hata: {}, Proje id: {}".format(proje_id, exc)
                                             )
            return abort(500)

        return render_template("dashboard/proje_islem_gecmisi.html",
                               islem_listesi=islem_listesi,
                               proje_id=proje_id,
                               proje=proje,
                               next_states_info=next_states_info,
                               actions_info=actions_info,
                               proje_yurutucusu_mu=proje_yurutucusu_mu)
