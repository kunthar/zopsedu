"""Proje Personel view classları"""
from flask import render_template, request, jsonify

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
from zopsedu.bap.models.proje_not import ProjeNot
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, get_next_states_info, \
    get_actions_info
from zopsedu.lib.db import DB
from zopsedu.models import Person
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeNotlariView(FlaskView):
    """
    Proje Notlari
    """

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_notlari_goruntuleme"]),
                   Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/notlar", methods=["GET"], endpoint="proje_notlari")
    def proje_notlari(proje_id):
        """
        projeye eklenen özel notları görüntüler
        Args:
            proje_id(int): projenin id si

        Returns:

        """
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

        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        proje_notlari = DB.session.query(ProjeNot, Person.ad.label("ad"), Person.soyad.label("soyad")).filter(
            ProjeNot.proje_id == proje_id).join(Person, Person.user_id == ProjeNot.notu_ekleyen_yetkili).all()

        if not proje:
            pass
            # todo: proje bulunamadı hatası dön

        return render_template("dashboard/proje_notlari.html",
                               proje=proje,
                               next_states_info=next_states_info,
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               actions_info=actions_info,
                               proje_notlari=proje_notlari,
                               proje_id=proje.id)


