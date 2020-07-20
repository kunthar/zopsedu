"""Proje view classları"""
from flask import render_template, current_app, abort
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_allows import And

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import Proje, ProjeCalisanlari
from zopsedu.auth.lib import auth, Permission
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.proje.views.basvuru.common import proje_turu_to_dict, \
    get_proje_turu_with_related_field, basvuru_formu_restriction, get_proje_data
from zopsedu.bap.lib.auth import TamamlanmamisProjeBasvurusu, ProjeYurutucusu


class ProjeRevizyon(FlaskView):
    """Proje revizyon view classı"""

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            And(TamamlanmamisProjeBasvurusu(), ProjeYurutucusu())))
    @route('/revizyon/<int:proje_id>', methods=['GET'])
    def proje_revizyon_get(proje_id):
        """
        Proje yetkilisi tarafindan gerekli gorulup yurutucuden proje revizyonu yapmasi istenirse
        bu view methodu kullanilir.
        Projenin ilgili state durumunda olup olmadigi(P9 - Başvurunun onaylanması için yürütücü
        revizyonu bekleniyor (ilgili state id = 9))  kontrolu yapilir.
        :param proje_id: revizyon beklenen projenin id si
        :return:
        """
        user_id = current_user.id
        revizyon_proje = DB.session.query(Proje).filter(
            Proje.id == Proje.id,
            Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor).first()
        if not revizyon_proje:
            CustomErrorHandler.error_handler(
                hata="Revizyon istenmeyen bir proje revize edilmeye "
                     "calisildi".format(user_id, proje_id))
            return abort(404)

        proje_turu = get_proje_turu_with_related_field(revizyon_proje.proje_turu, False)
        proje_turu_dict = proje_turu_to_dict(proje_turu)
        yurutucu_calisan_id = None

        yurutucu_calisan = DB.session.query(ProjeCalisanlari).filter_by(
            proje_id=proje_id,
            personel_id=revizyon_proje.yurutucu).first()
        if yurutucu_calisan:
            yurutucu_calisan_id = yurutucu_calisan.id

        form_data = get_proje_data(proje_turu_dict, revizyon_proje)

        proje_formu = basvuru_formu_restriction(proje_turu_dict=proje_turu_dict, **form_data)
        return render_template(
            'arastirma_projesi_basvuru/arastirma_proje_basvurusu.html',
            yeni_basvuru_formu=proje_formu,
            proje_tur_dict=proje_turu.to_dict(),
            proje_id=proje_id,
            proje_hakem_onerileri=revizyon_proje.proje_hakem_onerileri,
            proje_calisanlari=[calisan for calisan in revizyon_proje.proje_calisanlari if
                               not (
                                           revizyon_proje.yurutucu and revizyon_proje.yurutucu == calisan.personel_id)],
            yurutucu_calisan_id=yurutucu_calisan_id,
            taslak_mi=False,
            revizyon_bekleniyor_mu=True,
            uyari_mesajlari=proje_turu_dict.get("genel_uyari_mesajlari", None)
        )
