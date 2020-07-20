import random
import string

from flask import render_template, request, jsonify, url_for, render_template_string
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy import desc
from sqlalchemy.orm import lazyload
from werkzeug.datastructures import ImmutableMultiDict

from zopsedu.auth.models.auth import User
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_detay import ProjeHakemleri
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import Hakem, Person
from zopsedu.auth.lib import auth, Permission
from zopsedu.personel.models.personel import Personel

from .forms import HakemSearchForm, KurumIciHakemKayitForm, KurumDisiHakemKayitForm


def random_pw():
    chars = string.ascii_letters + string.digits
    return "".join([random.choice(chars) for i in range(8)])


class HakemView(FlaskView):
    excluded_methods = [
        "qry"
    ]

    @property
    def qry(self):
        """
        Proje ve ilgili alanlari icin query nesnesi olustur.
        Returns:
        """

        return DB.session.query(Hakem). \
            join(Person, Person.id == Hakem.person_id). \
            add_columns(
            Person.ad.label('ad'),
            Person.soyad.label('soyad'),
        )

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.ad + ' ' + r.soyad,
            r.Hakem.universite.ad if r.Hakem.universite else r.Hakem.kurum if r.Hakem.kurum else '-',
            r.Hakem.fakulte.ad if r.Hakem.fakulte else r.Hakem.daire if r.Hakem.daire else '-',
            r.Hakem.bolum.ad if r.Hakem.bolum else r.Hakem.birim if r.Hakem.birim else '-',
            r.Hakem.hitap_unvan.ad,
            r.Hakem.hakem_turu.value,
            """<a href="{}">
            <span class="float-left  fa ft-search fa-2x"></span>
            </a>""".format(url_for('hakem.hakem_detay', hakem_id=r.Hakem.id)),
            render_template_string(
                """
                {% if kurum_ici_mi %}
                {{ _('Düzenlenemez') }}
                {% else %}
                    <a href="{{url}}">
                    <span class="float-left fa fa-edit fa-2x"></span>
                    </a>
                 {% endif %}   
                    """, url=url_for('hakem.hakem_duzenle', hakem_id=r.Hakem.id),
                kurum_ici_mi=r.Hakem.kurum_ici)
        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record})

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_listemele"]),
                   menu_registry={"path": ".bap.proje.hakem", "title": _("Hakem Arama"),
                                  "order": 4})
    @route('/hakem-arama', methods=["GET"])
    def hakem_listele(self):
        """Hakem Arama Ekrani"""

        hakem_arama_form = HakemSearchForm()

        return render_template('arama.html', form=hakem_arama_form)

    @login_required
    @route('/hakem-kayit', methods=['GET'], endpoint='hakem_kayit')
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_kayit_ekleme"]))
    def hakem_kayit(self):
        """Hakem Kayit ekrani"""

        kurum_ici_hakem_form = KurumIciHakemKayitForm()
        kurum_disi_hakem_form = KurumDisiHakemKayitForm()

        return render_template('kayit.html', kurum_ici_hakem_form=kurum_ici_hakem_form,
                               kurum_disi_hakem_form=kurum_disi_hakem_form)

    @login_required
    @route('/hakem-kayit-kurum-ici', methods=['POST'], endpoint='hakem_kayit_kurum_ici')
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_kayit_ekleme"]))
    def hakem_kayit_kurum_ici(self):
        """Kurum içi hakem kayıt için post methodunu karşılayan view"""

        form = request.get_json()['kurum_ici']
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        kurum_ici_form = KurumIciHakemKayitForm(imd)

        if kurum_ici_form.validate():
            personel_id = kurum_ici_form.personel_sec.data

            hakem_kayitli_mi = DB.session.query(Hakem).filter_by(personel_id=personel_id).first()

            if not hakem_kayitli_mi:

                hakem = Hakem()
                personel = DB.session.query(Personel).filter_by(id=personel_id).first()
                hakem.unvan = personel.unvan
                hakem.universite_id = personel.birim
                hakem.fakulte_id = personel.birim
                hakem.personel_id = personel_id
                hakem.person_id = personel.person_id
                hakem.bolum_id = personel.birim
                hakem.hakem_turu = kurum_ici_form.kurum_ici_hakem_turu.data
                hakem.kurum_ici = True
                try:
                    DB.session.add(hakem)
                    DB.session.commit()
                except Exception as exc:
                    DB.session.rollback()
                    CustomErrorHandler.error_handler(hata="Kurum içi hakem eklenirken bir hata "
                                                          "oluştu." "Hata: {}".format(exc))

                    return jsonify(status="error"), 500

                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "personel_hakem_yap").type_index,
                    "nesne": 'Hakem',
                    "nesne_id": hakem.id,
                    "etkilenen_nesne": "Personel",
                    "etkilenen_nesne_id": personel.id,
                    "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı personeli hakem olarak ekledi ".format(
                        current_user.username,
                        personel.person.ad,
                        personel.person.soyad)
                }
                signal_sender(**signal_payload)

                return jsonify(status="success")

            return jsonify(status="error", error_message="Personel hakem olarak kayıtlı.!"), 500

        return jsonify(status="error", error_message="Lütfen formu eksiksiz doldurunuz.!"), 400

    @login_required
    @route('/hakem-kayit-kurum-disi', methods=['POST'], endpoint='hakem_kayit_kurum_disi')
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_kayit_ekleme"]))
    def hakem_kayit_kurum_disi(self):
        """Kurum dışı hakem kayıt için post methodunu karşılayan view"""

        form = request.get_json()['kurum_disi']
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        kurum_disi_form = KurumDisiHakemKayitForm(imd)

        if kurum_disi_form.validate():
            try:
                harici_hakem_ekli_mi = DB.session.query(Person).filter(
                    Person.birincil_eposta == kurum_disi_form.email.data).first()

                if harici_hakem_ekli_mi:
                    return jsonify(status="error",
                                   error_message="İlgili eposta adresi başka bir kişi tarafından "
                                                 "kullanılmaktadır. Lütfen başka bir eposta "
                                                 "adresiyle tekrar deneyiniz!"), 500

                user = User()
                user.username = kurum_disi_form.email.data
                user.password = random_pw()
                user.email = kurum_disi_form.email.data
                DB.session.add(user)
                DB.session.flush()

                person = Person()
                person.ad = kurum_disi_form.ad.data
                person.soyad = kurum_disi_form.soyad.data
                person.birincil_eposta = kurum_disi_form.email.data
                person.user_id = user.id
                DB.session.add(person)
                DB.session.flush()

                hakem = Hakem()
                hakem.unvan = kurum_disi_form.unvan.data
                if kurum_disi_form.universitede_gorev_almayan.data:
                    hakem.kurum = kurum_disi_form.kurum.data
                    hakem.daire = kurum_disi_form.daire.data
                    hakem.birim = kurum_disi_form.birim.data
                else:
                    hakem.universite_id = kurum_disi_form.universite.data
                    hakem.fakulte_id = kurum_disi_form.fakulte.data
                    hakem.bolum_id = kurum_disi_form.bolum.data

                hakem.hakem_turu = kurum_disi_form.hakem_turu.data
                hakem.person_id = person.id
                hakem.kurum_ici = False

                DB.session.add(hakem)
                DB.session.commit()
            except Exception as exc:
                DB.session.rollback()
                CustomErrorHandler.error_handler(hata="Kurum dışı hakem eklenirken bir hata oluştu."
                                                      "Hata: {}".format(exc))
                return jsonify(status="error"), 500

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "person_hakem_yap").type_index,
                "nesne": 'Hakem',
                "nesne_id": hakem.id,
                "etkilenen_nesne": "Person",
                "etkilenen_nesne_id": person.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı kurum dışı hakem olarak ekledi ".format(
                    current_user.username,
                    person.ad,
                    person.soyad)
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")

        return jsonify(status="error", error_message="Lütfen formu eksiksiz doldurunuz!"), 400

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_kayit_duzenleme"]))
    @route('/duzenle/<int:hakem_id>', methods=['GET'], endpoint='hakem_duzenle')
    def hakem_edit(self, hakem_id):
        """Hakem duzenleme"""
        hakem = DB.session.query(Hakem).filter(Hakem.id == hakem_id).one()
        if hakem.kurum_ici:
            form_data = {
                'personel_sec': hakem.person_id,
                'kurum_ici_hakem_turu': hakem.hakem_turu.name,
            }
            kurum_ici_hakem_form = KurumIciHakemKayitForm(**form_data)
            return render_template("edit.html", kurum_ici_hakem_form=kurum_ici_hakem_form,
                                   hakem=hakem_id)
        else:
            universitede_gorev_almayan = False
            if hakem.kurum or hakem.daire or hakem.birim:
                universitede_gorev_almayan = True
            form_data = {
                'fakulte': hakem.fakulte_id,
                'unvan': hakem.hitap_unvan.id,
                'hakem_turu': hakem.hakem_turu,
                'ad': hakem.person.ad,
                'soyad': hakem.person.soyad,
                'universite': hakem.universite_id,
                'bolum': hakem.bolum_id,
                'email': hakem.person.birincil_eposta,
                'kurum': hakem.kurum,
                'daire': hakem.daire,
                'birim': hakem.birim,
                'universitede_gorev_almayan': universitede_gorev_almayan
            }
            kurum_disi_hakem_form = KurumDisiHakemKayitForm(**form_data)
            return render_template('edit.html', kurum_disi_hakem_form=kurum_disi_hakem_form,
                                   hakem=hakem_id)

    @login_required
    @route('/duzenle/<int:hakem_id>', methods=['POST'], endpoint='hakem_duzenle_post')
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_kayit_duzenleme"]))
    def hakem_edit_post(self, hakem_id):
        """Hakem duzenleme"""
        hakem = DB.session.query(Hakem).filter(Hakem.id == hakem_id).one()

        if hakem.kurum_ici:

            form = request.get_json()['kurum_ici']
            imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
            kurum_ici_form = KurumIciHakemKayitForm(imd)

            if kurum_ici_form.validate():
                personel_id = kurum_ici_form.personel_sec.data
                hakem_ekli_mi = DB.session.query(Hakem).filter_by(personel_id=personel_id).first()
                if hakem_ekli_mi:
                    return jsonify(status="error",
                                   error_message="Seçilen personel kurumiçi hakem olarak kayıtlı.!"), 500

                personel = DB.session.query(Personel).filter_by(id=personel_id).first()
                hakem.unvan = personel.unvan
                hakem.universite_id = personel.birim
                hakem.fakulte_id = personel.birim
                hakem.personel_id = personel_id
                hakem.person_id = personel.person_id
                hakem.bolum_id = personel.birim
                hakem.hakem_turu = kurum_ici_form.kurum_ici_hakem_turu.data
                hakem.person_id = personel.person_id
                try:
                    DB.session.commit()
                except Exception as exc:
                    DB.session.rollback()
                    CustomErrorHandler.error_handler(hata="Kurum içi hakem eklenirken bir hata "
                                                          "oluştu.Hata: {}".format(exc))

                    return jsonify(status="error"), 500

                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "personel_hakem_yap").type_index,
                    "nesne": 'Hakem',
                    "nesne_id": hakem.id,
                    "etkilenen_nesne": "Personel",
                    "etkilenen_nesne_id": personel.id,
                    "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı personeli {} idli hakem yerine hakem olarak ekledi ".format(
                        current_user.username,
                        personel.person.ad,
                        personel.person.soyad,
                        hakem.id)
                }
                signal_sender(**signal_payload)

                return jsonify(status="success")

            return jsonify(status="error", error_message="Lütfen formu eksiksiz doldurunuz.!"), 400

        else:
            form = request.get_json()['kurum_disi']
            imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
            kurum_disi_form = KurumDisiHakemKayitForm(imd)

            if kurum_disi_form.validate():
                try:
                    hakem = DB.session.query(Hakem).filter(Hakem.id == hakem_id).one()
                    person = DB.session.query(Person).filter(Person.id == hakem.person_id).one()

                    person.ad = kurum_disi_form.ad.data
                    person.soyad = kurum_disi_form.soyad.data
                    person.birincil_eposta = kurum_disi_form.email.data
                    hakem.unvan = kurum_disi_form.unvan.data
                    hakem.hakem_turu = kurum_disi_form.hakem_turu.data
                    if kurum_disi_form.universitede_gorev_almayan.data:
                        hakem.kurum = kurum_disi_form.kurum.data
                        hakem.daire = kurum_disi_form.daire.data
                        hakem.birim = kurum_disi_form.birim.data
                        hakem.universite_id = None
                        hakem.fakulte_id = None
                        hakem.bolum_id = None
                    else:
                        hakem.kurum = None
                        hakem.daire = None
                        hakem.birim = None
                        hakem.universite_id = kurum_disi_form.universite.data
                        hakem.fakulte_id = kurum_disi_form.fakulte.data
                        hakem.bolum_id = kurum_disi_form.bolum.data
                    DB.session.commit()
                except Exception as exc:
                    DB.session.rollback()
                    CustomErrorHandler.error_handler(
                        hata="Kurum dışı hakem eklenirken bir hata oluştu."
                             "Hata: {}".format(exc))
                    return jsonify(status="error"), 500

                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "person_hakem_yap").type_index,
                    "nesne": 'Hakem',
                    "nesne_id": hakem.id,
                    "etkilenen_nesne": "Person",
                    "etkilenen_nesne_id": person.id,
                    "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı kurum dışı hakem bilgilerini güncelledi.".format(
                        current_user.username,
                        person.ad,
                        person.soyad)
                }
                signal_sender(**signal_payload)

                return jsonify(status="success")

            return jsonify(status="error", error_message="Lütfen formu eksiksiz doldurunuz!"), 400

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_detay_goruntuleme"]))
    @route('/detay/<int:hakem_id>', methods=['GET'], endpoint='hakem_detay')
    def hakem_detay(self, hakem_id):
        """Hakem detay ekrani"""
        hakem = DB.session.query(Hakem).filter(Hakem.id == hakem_id).one()

        hakem_projeleri = DB.session.query(
            ProjeHakemleri,
            Proje.proje_basligi.label("proje_basligi"),
            Proje.proje_no.label("proje_no"),
            Proje.proje_basligi.label("proje_basligi"),
            Proje.id.label("proje_id")).options(lazyload("*")).filter(
            ProjeHakemleri.hakem_id == hakem_id).join(Proje).all()

        return render_template('detay.html',
                               hakem=hakem,
                               hakem_projeleri=hakem_projeleri)

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["hakem"]["hakem_listemele"]))
    @route('/data', methods=["POST"], endpoint="hakem_search")
    def hakem_arama(self):  # pylint: disable=too-many-branches
        """
        Bap hakemlerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = HakemSearchForm(**form_data)

        kurum_ici_option = search_form.kurum_ici_option.data
        hakem_turu_option = search_form.hakem_turu_option.data

        if kurum_ici_option != '0':
            if kurum_ici_option == '1':
                qry = qry.filter(Hakem.kurum_ici == True)
            else:
                qry = qry.filter(Hakem.kurum_ici == False)
        if hakem_turu_option != '0':
            qry = qry.filter(Hakem.hakem_turu == hakem_turu_option)

        if not search_form.validate():
            result = qry.order_by(desc(Hakem.id)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        ad = search_form.ad.data
        soyad = search_form.soyad.data

        if ad:
            qry = qry.filter(Person.ad.ilike('%' + ad + '%'))
        if soyad:
            qry = qry.filter(Person.soyad.ilike('%' + soyad + '%'))

        result = qry.order_by(desc(Hakem.id)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
