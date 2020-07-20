"""BAP Proje Rapor View Modulu"""
from flask import render_template, request, url_for, redirect, jsonify, flash
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_allows import And, Or
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_rapor import ProjeRaporDurumu, ProjeRaporTipi
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import ProjeRapor, File
from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.bap.proje.forms.proje_raporlari.proje_raporlari import RaporForm
from zopsedu.bap.lib.auth import ProjeYurutucusu, AtanmisHakem
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, \
    get_next_states_info, get_actions_info
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeRaporView(FlaskView):
    """Proje ara ve sonuc raporlarini goruntuleme, filtreleme ve indirme viewi"""

    excluded_methods = [
        "qry",
        "proje_rapor_filtreleme_form",
    ]

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_goruntuleme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"), AtanmisHakem())))
    @route('<int:proje_id>/dashboard/rapor', methods=["GET"], endpoint='proje_rapor_index_get')
    def proje_rapor_get(self, proje_id):
        """Proje raporlarini goruntulemek icin kullanilir"""

        proje_yurutucusu_mu = ProjeYurutucusu().fulfill(user=current_user)
        atanmis_hakem = AtanmisHakem()
        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_proje_turu).load_only(
                "ara_rapor_sablon_id",
                "sonuc_raporu_sablon_id"),
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            joinedload(Proje.proje_raporlari),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(Proje.id == proje_id, or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                                           Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()
        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)
        ara_rapor_degerlendirme_sablon_id = proje.proje_proje_turu.ara_rapor_sablon_id
        sonuc_raporu_degerlendirme_sablon_id = proje.proje_proje_turu.sonuc_raporu_sablon_id

        return render_template(
            'dashboard/proje_raporlari.html',
            ara_rapor_degerlendirme_sablon_id=ara_rapor_degerlendirme_sablon_id,
            sonuc_raporu_degerlendirme_sablon_id=sonuc_raporu_degerlendirme_sablon_id,
            proje_raporlari=proje.proje_raporlari,
            proje_id=proje_id,
            proje=proje,
            proje_yurutucusu_mu=proje_yurutucusu_mu,
            next_states_info=next_states_info,
            actions_info=actions_info,
            rapor_duzenle_formu=RaporForm(),
            atanmis_hakem=atanmis_hakem
        )

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_goruntuleme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route('<int:proje_id>/rapor/<int:rapor_id>/information', methods=["GET"])
    def get_rapor_information(self, proje_id, rapor_id):
        """Proje raporunun bilgilerini getirir"""
        rapor_bilgileri = DB.session.query(ProjeRapor).filter(ProjeRapor.id == rapor_id,
                                                              ProjeRapor.proje_id == proje_id).scalar()
        if not rapor_bilgileri:
            return jsonify(status="error"), 404

        rapor_data = {
            "rapor_metni": rapor_bilgileri.rapor_icerigi,
            "tamamlandi_mi": True if rapor_bilgileri.durumu == ProjeRaporDurumu.tamamlandi else False,
            "file_id": rapor_bilgileri.file_id
        }
        return jsonify(status="success", rapor_data=rapor_data)

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_duzenleme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route("<int:proje_id>/rapor/<int:rapor_id>/", methods=["POST"],
           endpoint='proje_rapor_guncelle')
    def rapor_guncelle(self, proje_id, rapor_id):  # pylint: disable=R0201
        """
            Proje raporunu duzenlemek icin kullanilir
        """
        rapor_formu = RaporForm(request.form)

        proje_raporu = DB.session.query(ProjeRapor).filter(ProjeRapor.proje_id == proje_id,
                                                           ProjeRapor.id == rapor_id).one()
        if proje_raporu.duzenlenebilir_mi:
            proje_raporu.rapor_icerigi = rapor_formu.rapor_metni.data
            proje_raporu.file_id = rapor_formu.rapor_dosya.data
            if rapor_formu.tamamlandi_mi.data:
                proje_raporu.duzenlenebilir_mi = False
                proje_raporu.durumu = ProjeRaporDurumu.tamamlandi
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "proje_raporu_guncellendi").type_index,
                "nesne": 'Proje Rapor',
                "nesne_id": proje_raporu.id,
                "etkilenen_nesne": "Proje",
                "etkilenen_nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} id'li proje raporunu güncelledi.".format(
                    current_user.username,
                    proje_raporu.id)
            }
            signal_sender(**signal_payload)

            flash(_("Rapor başarıyla güncellendi."))
            DB.session.commit()
        else:
            flash(_("Rapor kaydedilemedi. Raporu güncelleyebilmeniz için düzenlenebilir olması gerekir"))

        return redirect(url_for('proje.proje_rapor_index_get', proje_id=proje_id))

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_silme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route("<int:proje_id>/rapor/<int:rapor_id>/sil", methods=["GET"],
           endpoint="proje_rapor_dosyasi_sil")
    def rapor_dosyasi_sil(self, proje_id, rapor_id):  # pylint: disable=R0201
        """
            Proje raporunu silmek icin kullanilir
        """
        rapor = DB.session.query(ProjeRapor).filter(ProjeRapor.proje_id == proje_id,
                                                    ProjeRapor.id == rapor_id).one()

        rapor.file_id = None
        DB.session.commit()

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "proje_rapor_dosyasi_sil").type_index,
            "nesne": 'Proje Rapor',
            "nesne_id": rapor.id,
            "etkilenen_nesne": "Proje",
            "etkilenen_nesne_id": proje_id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} id'li proje raporunun dosyasini kaldırdı.".format(
                current_user.username,
                rapor_id)
        }
        signal_sender(**signal_payload)
        flash(_("Rapor dosyası başarıyla kaldırıldı."))
        return redirect(url_for('proje.proje_rapor_index_get', proje_id=proje_id))

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_duzenleme"]),
            Or(Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route("<int:proje_id>/rapor/<int:rapor_id>/duzenlenebilir_mi", methods=["GET"],
           endpoint="proje_rapor_duzenlenebilir_mi")
    def duzenlenebilir_mi(self, proje_id, rapor_id):  # pylint: disable=R0201
        """
            Proje raporunun duzenlenebilirligini degistirmek icin kullanilir
        """
        rapor = DB.session.query(ProjeRapor).filter(ProjeRapor.proje_id == proje_id,
                                                    ProjeRapor.id == rapor_id).one()
        rapor.duzenlenebilir_mi = not rapor.duzenlenebilir_mi
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "proje_raporu_duzenlenebilir").type_index,
            "nesne": 'Proje Rapor',
            "nesne_id": rapor.id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} id'li proje raporunu düzenlenebilir "
                            "yaptı.".format(current_user.username,
                                            rapor.id)
        }
        signal_sender(**signal_payload)
        if rapor.duzenlenebilir_mi:
            flash(_("Seçtiğiniz rapor artık düzenlenebilir."))
        else:
            flash(_("Seçtiğiniz raporun düzenlenebilirliğini kaldırdınız."))
        return redirect(url_for('proje.proje_rapor_index_get', proje_id=proje_id))

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_duzenleme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route("<int:proje_id>/rapor-olustur/", methods=["POST"],
           endpoint='yeni_rapor_ekle')
    def yeni_rapor_ekle(self, proje_id):  # pylint: disable=R0201
        """
            Projeye yeni rapor eklemek icin kullanilir
        """
        ara_rapor_mu = request.args.get("ara_rapor_mu")
        rapor_form = RaporForm(request.form)

        # todo: monkey patch
        rapor_tipi = ProjeRaporTipi.ara_rapor if ara_rapor_mu == 'true' else ProjeRaporTipi.sonuc_raporu
        rapor_durumu = ProjeRaporDurumu.tamamlandi if rapor_form.tamamlandi_mi.data else ProjeRaporDurumu.tamamlanmadi
        duzenlenebilir_mi = False if rapor_durumu == ProjeRaporDurumu.tamamlandi else True

        yeni_rapor = ProjeRapor(rapor_tipi=rapor_tipi,
                                proje_id=proje_id,
                                file_id=rapor_form.rapor_dosya.data,
                                rapor_icerigi=rapor_form.rapor_metni.data,
                                durumu=rapor_durumu,
                                duzenlenebilir_mi=duzenlenebilir_mi)
        DB.session.add(yeni_rapor)
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "proje_raporu_eklendi").type_index,
            "nesne": 'Proje Rapor',
            "nesne_id": yeni_rapor.id,
            "etkilenen_nesne": "Proje",
            "etkilenen_nesne_id": proje_id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} id'li proje raporu {} id'li projeye "
                            "ekledi.".format(current_user.username,
                                             yeni_rapor.id,
                                             proje_id)
        }
        signal_sender(**signal_payload)

        flash(_("Rapor başarıyla projeye eklendi."))

        return redirect(url_for('proje.proje_rapor_index_get', proje_id=proje_id))

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["dashboard"]["proje_raporlari_goruntuleme"]),
            Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role("BAP Admin"), AtanmisHakem())))
    @route('<int:proje_id>/rapor/<int:rapor_id>', methods=["GET"])
    def get_single_proje_rapor(self, proje_id, rapor_id):
        """Projenin belirli bir raporunu almak icin kullanilir"""

        proje_rapor = DB.session.query(ProjeRapor).filter(
            ProjeRapor.proje_id == proje_id, ProjeRapor.id == rapor_id).one()

        return jsonify(status="success", rapor={
            "rapor_metni": proje_rapor.rapor_icerigi
        })
