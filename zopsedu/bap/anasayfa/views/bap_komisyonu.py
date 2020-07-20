"""Bap anasayfa modulu"""
from flask_babel import lazy_gettext as _
from flask import render_template
from flask_classful import FlaskView, route

from zopsedu.auth.lib import auth

from zopsedu.lib.db import DB
from zopsedu.models import Person, Birim
from zopsedu.personel.models.idari_personel import BapIdariPersonel
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class BapKomisyonuView(FlaskView):
    """Bap anasyafa bap komisyonu view classi"""

    @staticmethod
    @auth.requires(menu_registry={"path": ".anasayfa.bap_komisyonu",
                                  "title": _("BAP Komisyonu"), "order": 6})
    @route('/komisyon', methods=['GET'])
    def bap_komisyonu():
        bap_komisyonu = DB.session.query(
            BapIdariPersonel,
            Person.ad.label("personel_ad"),
            Person.soyad.label("personel_soyad"),
            BapIdariPersonel.gorevi.label("personel_gorevi"),
            HitapUnvan.ad.label("personel_hitap_unvan_ad"),
        ).join(
            Personel, BapIdariPersonel.personel_id == Personel.id
        ).join(
            Person, Personel.person_id == Person.id
        ).join(
            HitapUnvan, HitapUnvan.id == Personel.unvan).filter(
            BapIdariPersonel.gorevde_mi == True).all()

        return render_template("bap_komisyonu.html", bap_komisyonu=bap_komisyonu)
