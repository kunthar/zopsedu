"""BAP Toplanti View Modulu"""

from flask import render_template, request, url_for, redirect, flash, jsonify, render_template_string
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.helpers import GundemTipi
from zopsedu.auth.lib import Permission, auth
from zopsedu.lib.db import DB
from zopsedu.models import BapToplanti, BapGundem, Person
from zopsedu.bap.toplanti.forms import ToplantiKararFiltreleForm
from zopsedu.bap.models.proje import Proje
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class ToplantiKararlariView(FlaskView):
    """Toplanti kararlarini listeleyen metot"""
    excluded_methods = ['form', 'qry', 'gundem_tipi_choices']

    @property
    def qry(self):
        """
        + toplanti tarihi
        + gundem sıra no
        + proje no
        + karar durumu
        + gündem tipi
        + yürütücü
        + karar metni
        """

        return DB.session.query(
            BapGundem.gundem_sira_no.label("gundem_sira_no"),
            BapGundem.proje_id.label("proje_id"),
            Proje.proje_no.label("proje_no"),
            BapGundem.karar_durum.label("karar_durumu"),
            BapGundem.tipi.label("gundem_tipi"),
            HitapUnvan.ad.label("yurutucu_hitap_unvan_ad"),
            Person.ad.label("yurutucu_ad"),
            Person.soyad.label("yurutucu_soyad"),
            BapGundem.karar.label("karar_metni"),
            BapToplanti.toplanti_tarihi.label("toplanti_tarihi"),
        ).outerjoin(
            BapToplanti,
            BapGundem.toplanti_id == BapToplanti.id
        ).outerjoin(
            Proje,
            Proje.id == BapGundem.proje_id
        ).outerjoin(
            OgretimElemani,
            OgretimElemani.id == Proje.yurutucu
        ).outerjoin(
            Personel,
            Personel.id == OgretimElemani.personel_id
        ).outerjoin(
            Person,
            Person.id == Personel.person_id
        ).outerjoin(
            HitapUnvan,
            Personel.unvan == HitapUnvan.id
        ).filter(BapGundem.karar is not None)

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            render_template_string("""
            {{ date_to_string(toplanti_tarihi) if toplanti_tarihi else "-" }}
            """, toplanti_tarihi=r.toplanti_tarihi),
            r.gundem_sira_no if r.gundem_sira_no else "-",
            r.proje_no,
            r.karar_durumu.value,
            "{unvan} {ad} {soyad}".format(unvan=r.yurutucu_hitap_unvan_ad, ad=r.yurutucu_ad, soyad=r.yurutucu_soyad),
            r.gundem_tipi.value,
            render_template_string("""
            {{karar_metni | safe}}
            """, karar_metni=r.karar_metni)
        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record})


    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_kararlari_listesi_goruntuleme"]),
                   menu_registry={'path': '.bap.yk_toplanti.toplanti_kararlari',
                                  'title': _("Kararlar")})
    @route('/kararlar/', methods=['GET'])
    def kararlari_listele(self):
        """Toplanti kararlarının listelendigi view"""

        form = ToplantiKararFiltreleForm()
        return render_template('kararlari_listele.html', form=form)

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_kararlari_listesi_goruntuleme"]))
    @route('/kararlar/', methods=['POST'], endpoint="karar_search")
    def kararlari_filtrele(self):
        """
        Bap hakemlerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = ToplantiKararFiltreleForm(**form_data)

        ara_text = search_form.ara_text.data
        gundem_tipi = search_form.gundem_tipi.data
        toplanti_tarihi = search_form.tarih_arama.toplanti_tarihi.data
        toplanti_tarihi_tarihi_option = search_form.tarih_arama.toplanti_tarihi_option.data

        if gundem_tipi != '-1':
            qry = qry.filter(BapGundem.tipi == gundem_tipi)

        if not search_form.validate():
            result = qry.offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        if ara_text:
            qry = qry.filter(BapGundem.karar.ilike('%' + search_form.ara_text.data.strip() + '%'))

        if toplanti_tarihi:
            if toplanti_tarihi_tarihi_option == '0':
                qry = qry.filter(BapToplanti.toplanti_tarihi >= toplanti_tarihi)
            if toplanti_tarihi_tarihi_option == '1':
                qry = qry.filter(BapToplanti.toplanti_tarihi == toplanti_tarihi)
            if toplanti_tarihi_tarihi_option == '2':
                qry = qry.filter(BapToplanti.toplanti_tarihi <= toplanti_tarihi)

        result = qry.offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
