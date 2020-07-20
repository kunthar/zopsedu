"""Proje Türü View Metotları"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-nested-blocks
import simplejson
from flask import render_template, request, redirect, flash, session, url_for
from flask_classful import FlaskView, route
from flask_login import login_required, current_user

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import Taslak
from zopsedu.models.taslak import TaslakTipleri
from zopsedu.bap.proje.forms.proje_turu.proje_turu import ProjeTuruFormu
from zopsedu.auth.lib import auth, Permission
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class ProjeTuruTaslakView(FlaskView):
    """Proje Türü Taslak View"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/taslak/kaydet', methods=["POST"], endpoint='proje_turu_taslak_kaydet')
    def taslak_olarak_kaydet():
        """Taslak olarak kaydet."""
        user_id = session.get("user_id")
        proje_turu_formu = ProjeTuruFormu(request.form)
        basvuru_baslama_tarihi = proje_turu_formu.basvuru_baslama_tarihi.data
        basvuru_bitis_tarihi = proje_turu_formu.basvuru_bitis_tarihi.data

        if basvuru_baslama_tarihi:
            proje_turu_formu.basvuru_baslama_tarihi.data = str(basvuru_baslama_tarihi)
        if basvuru_bitis_tarihi:
            proje_turu_formu.basvuru_bitis_tarihi.data = str(basvuru_bitis_tarihi)

        yeni_taslak = Taslak(versiyon=0,
                             user_id=user_id,
                             taslak=proje_turu_formu.data,
                             taslak_tipi=TaslakTipleri.bap_proje_turu)

        DB.session.add(yeni_taslak)
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("proje_turu_taslak_kaydet").type_index,
            "nesne": 'Taslak',
            "nesne_id": yeni_taslak.id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} tipinde yeni bir taslak kaydetti.".format(
                yeni_taslak.user.username,
                yeni_taslak.taslak_tipi),
        }
        signal_sender(**signal_payload)
        return redirect(url_for('.proje_turu_get_taslak_with_id', taslak_id=yeni_taslak.id))

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/taslak/<int:taslak_id>', methods=["GET"], endpoint='proje_turu_get_taslak_with_id')
    def get_taslak(self, taslak_id):
        """Taslak olarak kaydedilmiş proje türünü id si ile al."""
        taslak = DB.session.query(Taslak).filter_by(id=taslak_id).one()
        if TaslakTipleri.bap_proje_turu != taslak.taslak_tipi:
            flash("Proje Türüne Ait Böyle Bir Taslak Bulunamadı.", "genel_ayarlar")
            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=ProjeTuruFormu())
        proje_turu_taslagi = getattr(taslak, "taslak", None)
        basvuru_baslama_tarihi = proje_turu_taslagi.get("basvuru_baslama_tarihi", None)
        basvuru_bitis_tarihi = proje_turu_taslagi.get("basvuru_bitis_tarihi", None)
        if basvuru_baslama_tarihi:
            proje_turu_taslagi["basvuru_baslama_tarihi"] = str(basvuru_baslama_tarihi)
        if basvuru_bitis_tarihi:
            proje_turu_taslagi["basvuru_bitis_tarihi"] = str(basvuru_bitis_tarihi)

        proje_turu_formu = ProjeTuruFormu(**proje_turu_taslagi)
        return render_template("proje_turu/proje_turu.html",
                               proje_turu_formu=proje_turu_formu, taslak_id=taslak.id)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/taslak/<int:taslak_id>/guncelle', methods=["POST"],
           endpoint='proje_turu_taslak_guncelle_with_id')
    def taslak_guncelle(taslak_id):
        """Taslak güncellemek için kullanılır"""
        taslak = DB.session.query(Taslak).filter_by(id=taslak_id).one()
        if TaslakTipleri.bap_proje_turu != taslak.taslak_tipi:
            # todo: return metod not allowed
            flash("Proje Türüne Ait Böyle Bir Taslak Bulunamadı.", "genel_ayarlar")
            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=ProjeTuruFormu())
        user_id = current_user.id
        proje_turu_formu = ProjeTuruFormu(request.form)
        basvuru_baslama_tarihi = proje_turu_formu.basvuru_baslama_tarihi.data
        basvuru_bitis_tarihi = proje_turu_formu.basvuru_bitis_tarihi.data
        if basvuru_baslama_tarihi:
            proje_turu_formu.basvuru_baslama_tarihi.data = str(basvuru_baslama_tarihi)
        if basvuru_bitis_tarihi:
            proje_turu_formu.basvuru_bitis_tarihi.data = str(basvuru_bitis_tarihi)

        taslak.user_id = user_id
        taslak.taslak = proje_turu_formu.data
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("proje_turu_taslak_guncelle").type_index,
            "nesne": 'Taslak',
            "nesne_id": taslak.id,
            "ekstra_mesaj": "{} adlı kullanıcı, proje türü taslagini guncelledi.".format(
                current_user.username)
        }
        signal_sender(**signal_payload)

        return redirect(url_for('.proje_turu_get_taslak_with_id', taslak_id=taslak.id))
