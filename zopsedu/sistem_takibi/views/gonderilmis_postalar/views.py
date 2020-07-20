""" Gonderilmiş E-postalar Modülü"""
import json

from flask import render_template, current_app
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_mesajlari import ProjeMesaj
from zopsedu.common.mesaj.models import Mesaj
from zopsedu.lib.db import DB
from zopsedu.lib.sessions import SessionHandler

from zopsedu.models import Person
from zopsedu.auth.lib import auth, Permission


class GonderilmisEpostalarView(FlaskView):
    """Gonderilmis epostalar Viewi"""

    excluded_methods = [
        "qry",
        "user_id"
    ]

    @property
    def qry(self):
        """ProjeMesaj BaseQuery"""

        system_user = SessionHandler.system_user()
        sp_id = system_user['person_id']

        return DB.session.query(ProjeMesaj).join(
            Proje, ProjeMesaj.proje_id == Proje.id).join(
            Mesaj, Mesaj.id == ProjeMesaj.mesaj_id).join(
            Person, Mesaj.gonderen == Person.id).add_columns(Proje.proje_basligi,
                                                             Proje.id.label("proje_id"),
                                                             Proje.proje_no,
                                                             Mesaj.okundu,
                                                             Mesaj.gonderim_zamani,
                                                             Mesaj.baslik,
                                                             Person.ad.label("gonderen_ad"),
                                                             Person.soyad.label("gonderen_soyad")).filter(
            Mesaj.gonderen == sp_id
        )

    @login_required
    @auth.requires(Permission(*permission_dict['sistem_takibi']['gonderilmis_epostalar']['gonderilmis_epostalar_goruntuleme']),
                   menu_registry={'path': '.sistem_takibi.gonderilmis_epostalar',
                                  'title': _("Gönderilmiş Epostalar")})
    @route("/liste")
    def liste(self):
        eposta_listesi = self.qry.all()

        return render_template("gonderilmis_epostalar/liste.html",
                               eposta_listesi=eposta_listesi)
