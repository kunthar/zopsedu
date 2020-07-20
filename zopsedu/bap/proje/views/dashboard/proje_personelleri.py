"""Proje Personel view classları"""
from flask import render_template

from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import ProjeYurutucusu
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, get_next_states_info, \
    get_actions_info
from zopsedu.lib.db import DB
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjePersonelView(FlaskView):
    """
    Proje Dashboard
    """

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_personelleri_goruntuleme"]),
                   Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/personel", methods=["GET"], endpoint="proje_personelleri")
    def proje_personelleri(proje_id):
        """
        projenin personel bilgilerine ulaşmak için kullanılır
        Args:
            proje_id(int): projenin id si

        Returns:

        """

        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            joinedload(Proje.proje_calisanlari),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(
            Proje.id == proje_id,
            or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)
        ).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)
        if not proje:
            pass
            # todo: proje bulunamadı hatası dön
        return render_template("dashboard/proje_personelleri.html",
                               proje=proje,
                               next_states_info=next_states_info,
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               actions_info=actions_info,
                               proje_id=proje.id)
