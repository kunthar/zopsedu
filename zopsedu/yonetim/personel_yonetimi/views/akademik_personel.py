"""BAP GundemSablonlari View Modulu"""
from flask import render_template, jsonify, abort, current_app, request, url_for, redirect, flash, \
    render_template_string
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from zopsedu.auth.lib import Permission, auth
from zopsedu.auth.models.auth import User
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import Personel, Person
from zopsedu.models.helpers import PersonelTuru
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.unvan import HitapUnvan
from zopsedu.yonetim.personel_yonetimi.forms.personel import PersonelDurumForm, AkademikPersonelSearchForm


class AkademikPersonelView(FlaskView):
    """Akademik Personel ile ilgili islemler Viewi"""

    excluded_methods = [
        "qry",
        "user_id"
    ]

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            "{}".format(r.unvan_ad),
            "{} {}".format(r.ad, r.soyad),
            # "{}".format(r.fakulte_id),
            # "{}".format(r.bolum.id),
            "{}".format("Aktif" if r.durumu else "Pasif"),
            render_template_string("""
             <a href="#preview-personel_durum"
                class="btn btn-success m-t-10"
                data-toggle="modal"
                data-target="#preview-personel_durum"
                onclick="personel_bilgisi({{ id }});">
                {{ _("Durumunu Belirle") }}
              </a>
            """, id=r.user_id)

        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @property
    def qry(self):
        """AkademikPersonel BaseQuery"""
        return DB.session.query(OgretimElemani). \
            join(Personel, Personel.id == OgretimElemani.personel_id). \
            join(Person, Person.id == Personel.person_id). \
            join(User, User.id == Person.user_id). \
            join(HitapUnvan, HitapUnvan.id == Personel.unvan). \
            filter(Personel.personel_turu == PersonelTuru.akademik). \
            add_columns(
            User.id.label("user_id"),
            User.durumu.label("durumu"),
            Person.ad.label("ad"),
            Person.soyad.label("soyad"),
            HitapUnvan.ad.label("unvan_ad")
        )

    @login_required
    @auth.requires(Permission(
        *permission_dict["yonetim"]["personel_yonetimi"]["akademik_personel_listesi_goruntuleme"]),
        menu_registry={'path': '.yonetim.personel_yonetimi.akademik_personel_listesi',
                       'title': _("Akademik Personel")})
    @route("/", methods=["GET"])
    def liste(self):
        """AkademikPersonel Listesi Ekrani"""
        personel_durum_form = PersonelDurumForm()
        search_form = AkademikPersonelSearchForm()
        return render_template("akademik_liste.html",
                               search_form=search_form,
                               personel_durum_form=personel_durum_form)

    # todo: Silme islemleri daha sonra dusunulecek
    @staticmethod
    @login_required
    @auth.requires(
        Permission(*permission_dict["yonetim"]["personel_yonetimi"]["akademik_personel_silme"]))
    @route("/sil/<int:personel_id>/", methods=["DELETE"], endpoint='sil')
    def sil(personel_id):
        """AkademikPersonel Silme"""

        personel = DB.session.query(
            Personel
        ).filter(
            Personel.id == personel_id
        ).one_or_none()

        if personel:
            DB.session.delete(personel)
            DB.session.commit()
            signal_payload = {
                "nesne": 'Personel',
                "nesne_id": personel.id,
                "ekstra_mesaj": "{} adlı kullanıcı {} id'li personeli sildi.".format(
                    current_user.username,
                    personel.id
                )
            }
            signal_sender(**signal_payload)
            return jsonify(status='success')

        return abort(400)

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_arama"]["projeleri_arama"]))
    @route('/data', methods=["POST"], endpoint="akademik_search")
    def personel_arama(self):  # pylint: disable=too-many-branches
        """
        Bap personel için POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """

        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = AkademikPersonelSearchForm(**form_data)

        ad = search_form.ad.data.strip()
        soyad = search_form.soyad.data.strip()
        unvan_id = search_form.unvan_id.data
        # fakulte_id = search_form.fakulte_id.data
        # bolum_id = search_form.bolum_id.data
        durumu = search_form.durumu.data

        if durumu != '-1':
            if durumu == '1':
                qry = qry.filter(User.durumu.is_(True))
            else:
                qry = qry.filter(User.durumu.is_(False))

        if not search_form.validate():
            result = qry.offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        if unvan_id:
            qry = qry.filter(HitapUnvan.id == unvan_id)

        if ad:
            qry = qry.filter(Person.ad.ilike('%' + ad + '%'))

        if soyad:
            qry = qry.filter(Person.soyad.ilike('%' + soyad + '%'))

        result = qry.offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)

    @staticmethod
    @login_required
    @auth.requires(Permission(
        *permission_dict["yonetim"]["personel_yonetimi"]["personel_durum_atama"]))
    @route("/durum-ata/<int:personel_id>/", methods=["POST"], endpoint='durum_ata')
    def durum_ata(personel_id):
        """AkademikPersonel Aktif veya Pasif durumu atama"""

        personel = DB.session.query(
            Personel
        ).filter(
            Personel.id == personel_id
        ).one_or_none()
        personel_durum_form = PersonelDurumForm(request.form)
        try:
            durum = bool(int(personel_durum_form.durum_listesi.data))
            personel.user.durumu = durum
            DB.session.add(personel)
            DB.session.commit()
            if durum:
                flash(
                    f"{personel.person.ad} {personel.person.soyad} adlı personelin durumu aktif olarak değiştirildi.")
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                        "personel_durumu_belirle").type_index,
                    "nesne": 'Personel',
                    "nesne_id": personel.id,
                    "ekstra_mesaj": """
                                          {} adlı kullanıcı
                                          {} {} adlı ve {} idsine sahip personelin durumunu Aktif olarak değiştirdi.""".format(
                        current_user.username,
                        personel.person.ad,
                        personel.person.soyad,
                        personel.id,
                    )
                }
            else:
                # Useri logout etmek icin cacheten session keyini siliyoruz.
                usid = personel.user.session_id
                cache = current_app.extensions['redis']
                key = "{prefix}:{usid}".format(
                    prefix=current_app.config.get('SESSION_CACHE_KEY_PREFIX'), usid=usid)
                cache.delete(key)
                flash(
                    f"{personel.person.ad} {personel.person.soyad} adlı personelin durumu pasif olarak değiştirildi.")
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                        "personel_durumu_belirle").type_index,
                    "nesne": 'Personel',
                    "nesne_id": personel.id,
                    "ekstra_mesaj": """
                              {} adlı kullanıcı
                              {} {} adlı ve {} idsine sahip personelin durumunu Pasif olarak değiştirdi.""".format(
                        current_user.username,
                        personel.person.ad,
                        personel.person.soyad,
                        personel.id,
                    )
                }
            signal_sender(**signal_payload)
            return redirect(url_for('personel_yonetimi.AkademikPersonelView:liste'))
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Akademik personel durumu değiştirilmeye çalışıldı. Hata: {}".format(exc))
            return redirect(url_for('personel_yonetimi.AkademikPersonelView:liste'))

    @staticmethod
    @login_required
    @auth.requires(Permission(
        *permission_dict["yonetim"]["personel_yonetimi"]["personel_durum_atama"]))
    @route("/personel-bilgisi/<int:personel_id>/", methods=["GET"])
    def personel_bilgisi(personel_id):
        try:
            personel = DB.session.query(Personel).filter(Personel.id == personel_id).options(
                joinedload(Personel.user)).first()
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="{} id li personel bilgisine oluşılırken bir hata oluştu. Hata:{}".format(
                    personel_id, exc))
            return jsonify(status="error"), 400

        personel_detay = {'personel_id': personel_id,
                          'personel_turu': personel.hitap_unvan.ad,
                          'personel_adı': personel.person.ad,
                          'personel_soyadı': personel.person.soyad,
                          'personel_aktifliği': personel.user.durumu

                          }

        return jsonify(status="success", personel=personel_detay)
