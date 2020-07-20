from flask import render_template, jsonify, request, url_for, redirect, flash, render_template_string, current_app
from flask_babel import gettext as _

from zopsedu.auth.lib import Permission, auth
from flask_classful import FlaskView, route
from flask_login import login_required, current_user

from zopsedu.auth.models.auth import User
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import Person
from zopsedu.personel.models.idari_personel import BapIdariPersonel
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan
from zopsedu.yonetim.personel_yonetimi.forms.personel import IdariPersonelSearchForm, PersonelDurumForm, \
    IdariPersonelEkle


class IdariPersonelView(FlaskView):
    excluded_methods = [
        "qry",
        "user_id"
    ]

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            "{}".format(r.unvan_ad),
            "{} {}".format(r.ad, r.soyad),
            "{}".format(r.gorevi.value),
            "{}".format(r.gorev_aciklamasi),
            "{}".format("Aktif" if r.durumu else "Pasif"),
            render_template_string("""
             <a href="#preview-personel_durum"
                class="btn btn-success m-t-10"
                data-toggle="modal"
                data-target="#preview-personel_durum"
                onclick="personel_bilgisi({{ id }});">
                {{ _("Durumunu Belirle") }}
              </a>
            """, id=r.user_id),
            render_template_string("""
                <button class="btn  btn-icon btn-danger" type='button' 
                    onclick="idari_personel_sil('{{id}}', '{{unvan}}', '{{ad}}', '{{soyad}}' );">
                    <span class="float-left detail_edit fa-in-button fa ft-trash fa-1x m-l-10"></span>
                </button>
            """, id=r.idari_personel_id, unvan=r.unvan_ad, ad=r.ad, soyad=r.soyad, )

        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @property
    def qry(self):
        """AkademikPersonel BaseQuery"""
        return DB.session.query(BapIdariPersonel). \
            join(Personel, Personel.id == BapIdariPersonel.personel_id). \
            join(Person, Person.id == Personel.person_id). \
            join(User, User.id == Person.user_id). \
            join(HitapUnvan, HitapUnvan.id == Personel.unvan).\
            add_columns(
            User.id.label("user_id"),
            User.durumu.label("durumu"),
            Person.ad.label("ad"),
            Person.soyad.label("soyad"),
            HitapUnvan.ad.label("unvan_ad"),
            BapIdariPersonel.gorevi.label("gorevi"),
            BapIdariPersonel.id.label("idari_personel_id"),
            BapIdariPersonel.gorev_aciklamasi.label("gorev_aciklamasi")
        ).filter(BapIdariPersonel.gorevde_mi == True)

    @login_required
    @auth.requires(Permission(
        *permission_dict["yonetim"]["personel_yonetimi"]["idari_personel_listesi_goruntuleme"]),
        menu_registry={'path': '.yonetim.personel_yonetimi.idari_personel_listesi',
                       'title': _("İdari Personel")})
    @route("/", methods=["GET"])
    def liste(self):

        personel_durum_form = PersonelDurumForm()
        search_form = IdariPersonelSearchForm()
        idari_personel_ekle_form = IdariPersonelEkle()
        return render_template("idari_liste.html",
                               search_form=search_form,
                               personel_durum_form=personel_durum_form,
                               idari_personel_ekle_form=idari_personel_ekle_form)

    @login_required
    @auth.requires(Permission(
        *permission_dict["yonetim"]["personel_yonetimi"]["idari_personel_listesi_goruntuleme"]))
    @route("/idari-personel-kaydet", methods=["POST"], endpoint="idari_personel_kaydet")
    def idari_personel_kaydet(self):
        form_data = request.form.to_dict()
        idari_personel_ekle_form = IdariPersonelEkle(**form_data)

        if not idari_personel_ekle_form.validate():
            flash("İdari personel eklenirken bir hata ile karşılaşıldı. Lütfen girdiğiniz bilgileri kontrol ediniz")
            return redirect(url_for('personel_yonetimi.IdariPersonelView:liste'))

        idari_personel = BapIdariPersonel(
            personel_id=idari_personel_ekle_form.personel_id.data,
            gorevi=idari_personel_ekle_form.gorevi.data,
            gorev_aciklamasi=idari_personel_ekle_form.gorev_aciklamasi.data
        )
        try:
            DB.session.add(idari_personel)
            DB.session.commit()
            flash("İşleminiz başarıyla gerçekleştirildi")
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                    "idari_personel_ekle").type_index,
                "nesne": 'Personel',
                "nesne_id": idari_personel.personel_id,
                "ekstra_mesaj": " {} personel idsine sahip personel idari personel olarak eklendi".format(
                    idari_personel.personel_id)
            }
            signal_sender(**signal_payload)
            return redirect(url_for('personel_yonetimi.IdariPersonelView:liste'))
        except Exception as exc:
            DB.session.rollback()
            flash("İdari personel eklenirken bir hata ile karşılaşıldı")
            CustomErrorHandler.error_handler(
                hata="İdari personel eklenmeye çalışıldı. Hata: {}".format(exc))
            return redirect(url_for('personel_yonetimi.IdariPersonelView:liste'))

    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["personel_yonetimi"]["idari_personel_silme"]))
    @route("/idari-personel-sil", methods=["POST"], endpoint="idari_personel_sil")
    def idari_personel_sil(self):
        idari_personel_id = request.get_json()['idari_personel_id']

        idari_personel = DB.session.query(BapIdariPersonel).filter(BapIdariPersonel.id == idari_personel_id).first()
        idari_personel.gorevde_mi = False
        try:
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("yonetim").get(
                    "idari_personel_sil").type_index,
                "nesne": 'Personel',
                "nesne_id": idari_personel.personel_id,
                "ekstra_mesaj": " {} idari personel idsine sahip personel idari personel görevi pasifleştirildi ".format(
                    idari_personel.personel_id)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success")

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="İdari personel silinmeye çalışıldı. Hata: {}".format(exc))
            return jsonify(status="error"), 400


    @staticmethod
    @login_required
    @auth.requires(Permission(
        *permission_dict["yonetim"]["personel_yonetimi"]["personel_durum_atama"]))
    @route("/durum-ata/<int:personel_id>/", methods=["POST"], endpoint='idari_personel_durum_ata')
    def durum_ata(personel_id):
        """İdari Personel Aktif veya Pasif durumu atama"""

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
            return redirect(url_for('personel_yonetimi.IdariPersonelView:liste'))
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="İdari personel durumu değiştirilmeye çalışıldı. Hata: {}".format(exc))
            return redirect(url_for('personel_yonetimi.IdariPersonelView:liste'))



    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["personel_yonetimi"]["idari_personel_listesi_goruntuleme"]))
    @route('/data', methods=["POST"], endpoint="idari_search")
    def personel_arama(self):  # pylint: disable=too-many-branches
        """
        Bap personel için POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """

        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = IdariPersonelSearchForm(**form_data)

        ad = search_form.ad.data.strip()
        soyad = search_form.soyad.data.strip()
        unvan_id = search_form.unvan_id.data
        durumu = search_form.durumu.data
        gorevi = search_form.gorevi.data

        if durumu != '-1':
            if durumu == '1':
                qry = qry.filter(User.durumu.is_(True))
            else:
                qry = qry.filter(User.durumu.is_(False))

        if gorevi != '0':
            qry = qry.filter(BapIdariPersonel.gorevi == gorevi)

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
