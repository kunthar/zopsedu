"""Proje hakkinda verilen kararların  listelenmesi"""

from flask import render_template, abort, current_app
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_allows import Or, And
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import BapGundem
from zopsedu.bap.lib.auth import ProjeYurutucusu
from zopsedu.bap.models.helpers import KararDurumu, ProjeBasvuruDurumu
from zopsedu.auth.lib import auth, Role, Permission
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, \
    get_next_states_info, \
    get_actions_info
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeKararlariView(FlaskView):
    """Proje kararları listeleme"""

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(
            *permission_dict["bap"]["proje"]["dashboard"]["proje_kararlari_goruntuleme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route('<int:proje_id>/dashboard/karar', methods=["GET"], endpoint='proje_kararlari_listele')
    def proje_kararlari(proje_id):
        """Yönetim Kurulu Kararları Listesi Ekrani"""
        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)

        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(Proje.id == proje_id,
                 or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                     Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)
        try:
            karar_listesi = DB.session.query(
                BapGundem
            ).filter(
                BapGundem.proje_id == proje_id,
                BapGundem.karar_durum != KararDurumu.degerlendirilmedi
            )
        except SQLAlchemyError as exc:
            CustomErrorHandler.error_handler(
                hata="Proje kararları sorgusunda hata oluştu  "
                     "Hata: {}, User id: {}, Proje id: {}".format(exc, current_user.id, proje_id))

            return abort(500)

        return render_template("dashboard/proje_kararlari.html",
                               karar_listesi=karar_listesi,
                               proje_id=proje_id,
                               proje=proje,
                               next_states_info=next_states_info,
                               actions_info=actions_info,
                               proje_yurutucusu_mu=proje_yurutucusu_mu)
