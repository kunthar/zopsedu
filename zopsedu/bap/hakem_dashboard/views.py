"""Hakem Proje Degerlendirme Views"""
# todo: izinler degisecek !!!
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, lazyload

from flask import render_template, request, redirect, url_for, jsonify, abort
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_babel import gettext as _

from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import AtanmisHakem
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_detay import ProjeDegerlendirmeleri, ProjeHakemDavetDurumlari, \
    ProjeHakemleri
from zopsedu.bap.hakem_dashboard.forms import ProjeDegerlendirmeForm, RaporDegerlendirmeForm, \
    HakemProjeDegerlendirmeForm, ProjeDegerlendirmeFormu
from zopsedu.bap.models.proje_rapor import ProjeRapor, ProjeRaporTipi, ProjeRaporDurumu
from zopsedu.lib.db import DB
from zopsedu.auth.lib import auth, Permission
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.personel.models.hakem import Hakem
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class HakemDashboard(FlaskView):
    """Hakem Projeleri Degerlendirme"""

    @staticmethod
    @login_required
    @route('/degerlendirmeler/', methods=['GET'])
    # todo: permissin durumu kontrol edilecek
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]),
        menu_registry={'path': '.bap.proje_degerlendirmeleri',
                       'title': _("İstekler")})
    def hakem_proje_degerlendirme_istekleri():
        """ Hakem proje degerlendirme liste ekrani."""
        hakem = DB.session.query(Hakem.id.label("hakem_id")).options(lazyload('*')).filter(
            Hakem.person_id == current_user.person.id).one()
        hakem_id = hakem.hakem_id

        # query sonucu tuple list halde gelir.
        # proje basligi ve proje id label a sahip oldugu icin attr olarak donen degerden alinabilir
        # tuple in 0 indexli elemani ProjeHakemleri instance i icerir
        # todo: lib query birlesince oraya tasinacak
        hakem_projeleri = DB.session.query(
            ProjeHakemleri,
            Proje.proje_basligi.label("proje_basligi"),
            Proje.id.label("proje_id")
        ).options(lazyload("*")).filter(
            ProjeHakemleri.hakem_id == hakem_id
        ).join(Proje).all()

        tamamlanan_degerlendirmeler = []
        degerlendirilmemis_davetler = []

        for hakem_proje in hakem_projeleri:
            data = {
                "proje_basligi": hakem_proje.proje_basligi,
                "proje_id": hakem_proje.proje_id,
                "davet_durumu": hakem_proje[0].davet_durumu.value,
                "proje_hakem_id": hakem_proje[0].id,
                "projeyi_inceleyebilir_mi": True
            }
            if hakem_proje[0].davet_durumu == ProjeHakemDavetDurumlari.gonderildi:
                degerlendirilmemis_davetler.append(data)
            else:
                if hakem_proje[0].davet_durumu == ProjeHakemDavetDurumlari.reddedildi:
                    data["projeyi_inceleyebilir_mi"] = False
                tamamlanan_degerlendirmeler.append(data)

        return render_template("proje_degerlendirme_istekleri.html",
                               degerlendirilmemis_davetler=degerlendirilmemis_davetler,
                               tamamlanan_degerlendirmeler=tamamlanan_degerlendirmeler)

    @login_required
    @route('proje/<int:proje_id>/degerlendirmeler/<int:proje_hakem_id>', methods=['POST'],
           endpoint='post_hakem_proje_degerlendirme_istekleri')
    # todo: izin degisecek. yapilan islemi test edebilmek icin bu halde
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]))
    def post_hakem_proje_degerlendirme_istekleri(self, proje_hakem_id,
                                                 proje_id):  # pylint: disable=R0201
        """
                Hakem degerlendirmesi kabul veya reddi icin kullanilir.

        """
        proje_hakemi = DB.session.query(ProjeHakemleri).options(
            joinedload(ProjeHakemleri.proje).load_only(Proje.proje_no)
        ).filter(
            ProjeHakemleri.id == proje_hakem_id,
            ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.gonderildi
        ).one()
        hakem = DB.session.query(Hakem.id.label("hakem_id")).options(lazyload('*')).filter(
            Hakem.person_id == current_user.person.id).one()
        if proje_hakemi:
            if proje_hakemi.hakem_id != hakem.hakem_id:
                return jsonify(status="error"), 500
            davet_durumu = request.get_json().get('davet_durumu')
            proje_hakemi.davet_durumu = davet_durumu
            DB.session.commit()
            if proje_hakemi.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi:
                message = "hakemlik davetini kabul etti"
            else:
                message = "hakemlik davetini reddetti"
            extra_message = """{} adlı kullanıcı({} id'li hakem),{} numaralı projenin {}""".format(
                current_user.username,
                hakem.hakem_id,
                proje_hakemi.proje.proje_no,
                message
            )
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "degerlendirme_teklifi_cevaplandi").type_index,
                "nesne": 'Proje Hakemleri',
                "nesne_id": proje_hakemi.id,
                "ekstra_mesaj": extra_message
            }
            signal_sender(**signal_payload)

            for bap_admin in bap_yetkili_and_admin_ids():
                payload = {
                    "notification_receiver": bap_admin.person_id,
                    "notification_title": proje_hakemi.davet_durumu.value,
                    "notification_message": "{} adlı kullanıcı {} numaralı projenin {}".format(
                        current_user.username, proje_hakemi.proje.proje_no,
                        message),
                }

                signal_sender(log=False, notification=True, **payload)
            return jsonify(status="success")

        return abort(400)

    @staticmethod
    @login_required
    # todo: izin kontrolu yap
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]),
        menu_registry={'path': '.bap.atanmis_projeler',
                       'title': _("Atanmış Projeler")})
    @route('/atanmis-projeler', methods=["GET"])
    def proje_listesi():
        """Hakem Proje Listesi"""
        hakem_id = DB.session.query(Hakem).filter(
            Hakem.person_id == current_user.person.id).one().id

        # kabul edilen proje hakemliklerinin id listesini doner
        hakem_proje = DB.session.query(ProjeHakemleri.id).filter(
            ProjeHakemleri.hakem_id == hakem_id,
            ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi
        ).all()

        degerlendirme_bilgileri = DB.session.query(ProjeDegerlendirmeleri).options(
            joinedload(ProjeDegerlendirmeleri.rapor).joinedload(ProjeRapor.proje)).filter(
            ProjeDegerlendirmeleri.proje_hakem_id.in_(hakem_proje)).all()

        degerlendirilecek_projeler = []
        ara_rapor_deg_projeler = []
        sonuc_rapor_deg_projeler = []

        for degerlendirme in degerlendirme_bilgileri:
            if degerlendirme.rapor.durumu == ProjeRaporDurumu.tamamlandi:
                if degerlendirme.rapor.rapor_tipi == ProjeRaporTipi.ara_rapor:
                    ara_rapor_deg_projeler.append(degerlendirme)
                elif degerlendirme.rapor.rapor_tipi == ProjeRaporTipi.proje_basvuru:
                    degerlendirilecek_projeler.append(degerlendirme)
                elif degerlendirme.rapor.rapor_tipi == ProjeRaporTipi.sonuc_raporu:
                    sonuc_rapor_deg_projeler.append(degerlendirme)

        # todo bilim kurulu ve komisyon üyesi olduğu projeler eklenecek
        return render_template('proje_listesi.html',
                               degerlendirilecek_projeler=degerlendirilecek_projeler,
                               ara_rapor_deg_projeler=ara_rapor_deg_projeler,
                               sonuc_rapor_deg_projeler=sonuc_rapor_deg_projeler,
                               hakem_proje_degerlendirme_formu=HakemProjeDegerlendirmeForm(),
                               degerlendirme_formu=ProjeDegerlendirmeFormu(),
                               hakem_id=hakem_id
                               )

    @staticmethod
    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]))
    @route('/degerlendirme/<int:degerlendirme_id>/kaydet', methods=["POST"],
           endpoint="degerlendirme_kaydet")
    def degerlendirme_kaydet(degerlendirme_id):
        degerlendirme_formu = ProjeDegerlendirmeFormu(request.form)
        degerlendirme = DB.session.query(ProjeDegerlendirmeleri).options(
            joinedload(ProjeDegerlendirmeleri.rapor).joinedload(ProjeRapor.proje).load_only(
                "proje_no")
        ).filter(
            ProjeDegerlendirmeleri.id == degerlendirme_id).one()

        degerlendirme.degerlendirme = degerlendirme_formu.degerlendirme_metni.data
        degerlendirme.degerlendirme_sonuclandi_mi = degerlendirme_formu.degerlendirme_tamamlandi_mi.data
        degerlendirme.degerlendirme_gonderim_tarihi = datetime.now()
        degerlendirme.sonuc = degerlendirme_formu.degerlendirme_sonucu.data
        DB.session.commit()
        if degerlendirme.degerlendirme_sonuclandi_mi:
            for bap_admin in bap_yetkili_and_admin_ids():
                payload = {
                    "notification_receiver": bap_admin.person_id,
                    "notification_title": "{} Değerlendirmesi Tamamlandı".format(
                        degerlendirme.rapor.rapor_tipi.value),
                    "notification_message": "{} adlı kullanıcı {} numaralı projenin {} değerlendirmesini tamamladı. Değerlendirme sonucu {}".format(
                        current_user.username,
                        degerlendirme.rapor.proje.proje_no,
                        degerlendirme.rapor.rapor_tipi.value,
                        degerlendirme.sonuc.value),
                }

                signal_sender(log=False, notification=True, **payload)
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "proje_degerlendirdi").type_index,
                "nesne": 'ProjeDegerlendirmeleri',
                "nesne_id": degerlendirme.id,
                "ekstra_mesaj": "{} adlı kullanıcı {} numaralı projenin {} değerlendirmesini tamamladı. Değerlendirme sonucu {}".format(
                    current_user.username,
                    degerlendirme.rapor.proje.proje_no,
                    degerlendirme.rapor.rapor_tipi.value,
                    degerlendirme.sonuc.value)
            }
            signal_sender(**signal_payload)
        return redirect(url_for('hakem_dashboard.HakemDashboard:proje_listesi'))

    @staticmethod
    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]))
    @route('/degerlendirme/<int:degerlendirme_id>/text', methods=["GET"],
           endpoint="get_degerlendirme_text")
    def get_degerlendirme_text(degerlendirme_id):
        degerlendirme = DB.session.query(ProjeDegerlendirmeleri).filter(
            ProjeDegerlendirmeleri.id == degerlendirme_id).scalar()
        return jsonify(status="success", degerlendirme_metni=degerlendirme.degerlendirme)

    @staticmethod
    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]),
        AtanmisHakem())
    @route('/<int:proje_id>', methods=["GET"], endpoint='proje_degerlendirme')
    def proje_degerlendirme(proje_id):
        """Hakem Proje Degerlendirme"""
        hakem_id = DB.session.query(Hakem).filter(
            Hakem.person_id == current_user.person.id).first().id
        proje_degerlendirme = DB.session.query(ProjeDegerlendirmeleri).filter(
            ProjeDegerlendirmeleri.proje_id == proje_id,
            ProjeDegerlendirmeleri.hakem_id == hakem_id,
            ProjeDegerlendirmeleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi).first()
        if proje_degerlendirme.davet_durumu in [ProjeHakemDavetDurumlari.suruyor,
                                                ProjeHakemDavetDurumlari.tamamlandi]:
            form = ProjeDegerlendirmeForm(**proje_degerlendirme.degerlendirme_detaylari)
        else:
            form = ProjeDegerlendirmeForm()
        return render_template('proje_degerlendirme.html', form=form, proje_id=proje_id)

    @staticmethod
    @login_required
    @auth.requires(
        Permission(*permission_dict["bap"]["hakem_dashboard"]["hakem_proje_degerlendirme"]),
        AtanmisHakem())
    @route('/<int:proje_id>', methods=["POST"])
    def post_proje_degerlendirme(proje_id):
        """Hakem Proje Degerlendirme"""
        form = ProjeDegerlendirmeForm(request.form)
        sess = DB.session

        hakem_id = DB.session.query(Hakem).filter(
            Hakem.person_id == current_user.person.id).one().id

        try:
            proje_degerlendirmesi = sess.query(ProjeDegerlendirmeleri).filter(
                ProjeDegerlendirmeleri.hakem_id == hakem_id).filter(
                ProjeDegerlendirmeleri.proje_id == proje_id).one()

            proje_degerlendirmesi.degerlendirme_detaylari = form.data
            proje_degerlendirmesi.sonuc = form.degerlendirme_sonucu.data
            proje_degerlendirmesi.degerlendirme_tarihi = datetime.now()
            if form.degerlendirme_tamamlandi.data:
                proje_degerlendirmesi.davet_durumu = ProjeHakemDavetDurumlari.tamamlandi
            else:
                proje_degerlendirmesi.davet_durumu = ProjeHakemDavetDurumlari.suruyor

            sess.commit()
            extra_mesaj = """{} adlı kullanıcı({} id'li hakem), proje değerlendirme bilgilerini
            {} olarak düzenledi.""".format(
                current_user.username,
                hakem_id,
                proje_degerlendirmesi.davet_durumu
            )
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "proje_degerlendirdi").type_index,
                "nesne": 'Proje Degerlendirme',
                "nesne_id": proje_degerlendirmesi.id,
                "ekstra_mesaj": extra_mesaj
            }
            signal_sender(**signal_payload)
        except SQLAlchemyError as exc:
            sess.rollback()
            print(str(exc))

        return redirect(
            url_for(".HakemDashboard:proje_listesi",
                    proje_id=proje_id)
        )
