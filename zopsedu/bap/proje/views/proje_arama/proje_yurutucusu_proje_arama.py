"""BAP Proje Arama View Modulu"""

from flask import render_template
from flask_allows import And
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import auth, Role, Permission
from zopsedu.auth.models.auth import User
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.lib.db import DB
from zopsedu.models import Proje, Personel, Person
from zopsedu.models.helpers import AppStates


class ProjeYurutucusuProjeAramaView(FlaskView):
    """Proje Arama"""

    excluded_methods = [
        "qry",
    ]

    @login_required
    @route('/', methods=["GET"])
    @auth.requires(Role("Öğretim Üyesi"),
                   menu_registry={'path': '.bap.projelerim',
                                  'title': _("Projelerim"), "order": 1})
    def proje_listesi(self):
        """
        Proje arama index sayfasi
        Returns:
            http response
        """

        ogretim_gorevlisi = DB.session.query(User). \
            join(Person, Person.user_id == User.id). \
            join(Personel, Person.id == Personel.person_id). \
            add_columns(Personel.id.label("ogretim_gorevlisi_id")). \
            filter(User.id == current_user.id).one()

        ogretim_gorevlisi_id = ogretim_gorevlisi.ogretim_gorevlisi_id

        tum_projeler = DB.session.query(Proje).filter(
            Proje.yurutucu == ogretim_gorevlisi_id,
            or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)
        ).options(joinedload(Proje.proje_durumu)).all()

        basvuru_kabul = list(
            filter(lambda x: x.proje_durumu.current_app_state == AppStates.basvuru_kabul,
                   tum_projeler))

        devam_eden = list(
            filter(lambda x: x.proje_durumu.current_app_state == AppStates.devam, tum_projeler))

        sonlandirilmis = list(
            filter(lambda x: x.proje_durumu.current_app_state == AppStates.son, tum_projeler))

        revizyon_beklenenler = []
        for proje in tum_projeler:
            if proje.proje_durumu.current_app_state == AppStates.basvuru_kabul and proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor:
                revizyon_beklenenler.append(proje)

        taslak_olan_projeler = DB.session.query(Proje).options(
            lazyload('*')
        ).filter(
            Proje.user_id == current_user.id,
            Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.taslak
        ).all()

        return render_template('proje_arama/proje_yurutucu_proje_arama.html',
                               tum_projelerim=tum_projeler,
                               basvuru_kabul=basvuru_kabul,
                               devam_eden=devam_eden,
                               sonlandirilmis=sonlandirilmis,
                               revizyon_beklenenler=revizyon_beklenenler,
                               taslak_olan_projeler=taslak_olan_projeler)
