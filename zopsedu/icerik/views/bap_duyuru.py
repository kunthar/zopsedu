"""Bap duyuru modulu"""

from flask_babel import lazy_gettext as _
from flask import render_template, jsonify, request, flash
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import desc

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.auth.lib import auth, Permission
from zopsedu.models import Icerik, User, Person
from zopsedu.icerik.model import IcerikBirimTipi, IcerikTipi
from zopsedu.icerik.form import BapDuyuruForm
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class BapDuyuruView(FlaskView):
    """Bap duyuru view classi"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["icerik"]["bap_duyuru"]["bap_duyuru_listeleme"]),
                   menu_registry={'path': '.yonetim.bap.bap_duyuru',
                                  'title': _("BAP Duyuru")})
    @route('/listele', methods=['GET'])
    def bap_duyuru_listele():
        """Bap duyurularini listeleyen method."""
        # tipi duyuru ve birim tipi bap olan butun icerikleri getirir
        duyurular = DB.session.query(Icerik).join(
            User, User.id == Icerik.ekleyen_id).join(
            Person, Person.user_id == User.id).add_columns(Icerik.id,
                                                           Icerik.icerik,
                                                           Icerik.baslik,
                                                           Icerik.baslangic_tarihi,
                                                           Icerik.bitis_tarihi,
                                                           Icerik.on_sayfa_gorunurlugu,
                                                           Icerik.aktif_mi,
                                                           Person.ad.label("ekleyen_ad"),
                                                           Person.soyad.label("ekleyen_soyad")
                                                           ).filter(
            Icerik.tipi == IcerikTipi.duyuru, Icerik.birim_tipi == IcerikBirimTipi.bap).order_by(desc(Icerik.created_at)).all()

        bap_duyuru_formu = BapDuyuruForm()

        return render_template("bap_duyuru_listele.html",
                               duyurular=duyurular,
                               bap_duyuru_formu=bap_duyuru_formu)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["icerik"]["bap_duyuru"]["bap_duyuru_listeleme"]))
    @route('/<int:duyuru_id>/duyuru', methods=['GET'], endpoint="get_bap_duyuru")
    def get_bap_duyuru(duyuru_id):
        """Belirli bir bap duyurusunu getirir"""
        # tipi duyuru, birim tipi bap olan duyuruyu getirir
        duyuru = DB.session.query(Icerik).join(
            User, User.id == Icerik.ekleyen_id).join(
            Person, Person.user_id == User.id).add_columns(Icerik.icerik,
                                                           Icerik.baslik,
                                                           Icerik.baslangic_tarihi,
                                                           Icerik.bitis_tarihi,
                                                           Icerik.on_sayfa_gorunurlugu,
                                                           Icerik.aktif_mi,
                                                           Person.ad.label("ekleyen_ad"),
                                                           Person.soyad.label("ekleyen_soyad")
                                                           ).filter(
            Icerik.tipi == IcerikTipi.duyuru, Icerik.birim_tipi == IcerikBirimTipi.bap).filter(Icerik.id == duyuru_id).one()
        duyuru_data = {
            "icerik": duyuru.icerik,
            "baslik": duyuru.baslik,
            "baslama_tarihi": duyuru.baslangic_tarihi.strftime("%d.%m.%Y %H:%M") if duyuru.baslangic_tarihi else "",
            "bitis_tarihi": duyuru.bitis_tarihi.strftime("%d.%m.%Y %H:%M") if duyuru.bitis_tarihi else "",
            "aktif_mi": duyuru.aktif_mi,
            "gorunur_mu": duyuru.on_sayfa_gorunurlugu,
        }

        return jsonify(status="success", duyuru_data=duyuru_data)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["icerik"]["bap_duyuru"]["bap_duyuru_listeleme"]))
    @route('/<int:duyuru_id>/guncelle', methods=['POST'], endpoint="bap_duyuru_guncelle")
    def bap_duyuru_guncelle(duyuru_id):
        """Belirli bir bap duyurusunu getirir"""
        bap_duyuru = request.get_json()
        duyuru_formu = BapDuyuruForm(**bap_duyuru)

        # tipi duyuru, birim tipi bap olan duyuruyu getirir
        guncellenecek_duyuru = DB.session.query(Icerik).filter(
            Icerik.tipi == IcerikTipi.duyuru,
            Icerik.birim_tipi == IcerikBirimTipi.bap,
            Icerik.id == duyuru_id).one()

        guncellenecek_duyuru.update_obj_data(duyuru_formu.data)

        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("icerik").get("bap_duyuru_guncelle").type_index,
            "nesne": 'Icerik',
            "nesne_id": guncellenecek_duyuru.id,
            "ekstra_mesaj": "{} adli user, {} id'li icerik(bap duyuru) guncelledi.".format(
                current_user.username,
                guncellenecek_duyuru.id)
        }
        signal_sender(**signal_payload)

        return jsonify(status="success")

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["icerik"]["bap_duyuru"]["bap_duyuru_listeleme"]))
    @route('/<int:duyuru_id>/sil', methods=['DELETE'], endpoint="bap_duyuru_sil")
    def bap_duyuru_sil(duyuru_id):
        """Belirli bir bap duyurusunu getirir"""
        # tipi duyuru, birim tipi bap, id si 'duyuru_id' olan icerigi getirir
        silinecek_duyuru = DB.session.query(Icerik).filter(
            Icerik.tipi == IcerikTipi.duyuru,
            Icerik.birim_tipi == IcerikBirimTipi.bap,
            Icerik.id == duyuru_id).one()
        DB.session.delete(silinecek_duyuru)

        DB.session.commit()

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("icerik").get("bap_duyuru_sil").type_index,
            "nesne": 'Icerik',
            "nesne_id": duyuru_id,
            "ekstra_mesaj": "{} adli user, {} id'li icerik(bap duyuru) sildi.".format(
                current_user.username,
                duyuru_id)
        }
        signal_sender(**signal_payload)

        return jsonify(status="success")

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["icerik"]["bap_duyuru"]["bap_duyuru_olusturma"]))
    @route('/olustur', methods=['POST', 'GET'], endpoint="bap_duyuru_olustur")
    def bap_duyuru_olustur():
        """Bap duyuru olusturur"""
        bap_duyuru_formu = BapDuyuruForm(request.form)
        if request.method == 'GET' or not bap_duyuru_formu.validate():
            return render_template("bap_duyuru_olustur.html", duyuru_formu=bap_duyuru_formu)

        duyuru_data = bap_duyuru_formu.data
        if duyuru_data["baslangic_tarihi"] >= duyuru_data["bitis_tarihi"]:
            flash(_("{}, {} sonraki bir tarih olamaz").format(
                bap_duyuru_formu.baslangic_tarihi.label.text,
                bap_duyuru_formu.bitis_tarihi.label.text))
            return render_template("bap_duyuru_olustur.html", duyuru_formu=bap_duyuru_formu)

        # formda olup modelde kullanilmayan alanlari cikartir
        duyuru_data.pop("icerik_id")
        duyuru_data.pop("ekleyen_ad_soyad")
        duyuru_data.pop("csrf_token")
        bap_duyuru = Icerik(ekleyen_id=current_user.id,
                            tipi=IcerikTipi.duyuru,
                            birim_tipi=IcerikBirimTipi.bap,
                            **duyuru_data)

        DB.session.add(bap_duyuru)
        DB.session.commit()
        flash(_("BAP Duyuru Başarı ile Oluşturuldu."))

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("icerik").get("bap_duyuru_olustur").type_index,
            "nesne": 'Icerik',
            "nesne_id": bap_duyuru.id,
            "ekstra_mesaj": "{} adli user, {} id'li icerik(bap duyuru) olusturdu.".format(
                current_user.username,
                bap_duyuru.id)
        }
        signal_sender(**signal_payload)

        return render_template("bap_duyuru_olustur.html", duyuru_formu=bap_duyuru_formu)
