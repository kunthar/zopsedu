"""BAP Proje Arama View Modulu"""

from babel.numbers import format_currency
from flask import render_template, request, url_for, jsonify
from flask_allows import Or
from sqlalchemy import cast, String, or_
from sqlalchemy.sql import desc
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje_turu import ProjeTuru
from zopsedu.lib.db import DB
from zopsedu.models import Proje, OgretimElemani, Personel, Person, AppState
from zopsedu.bap.proje.forms.proje_arama.proje_arama import SearchForm


class ProjeAramaView(FlaskView):
    """Proje Arama"""

    excluded_methods = [
        "qry"
    ]
    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.proje_turu_ad,
            r.proje_no if r.proje_no else '-',
            r.state_code,
            r.proje_basligi,
            '{:%d.%m.%Y}'.format(r.kabul_edilen_baslama_tarihi) if r.kabul_edilen_baslama_tarihi else "-",
            "{} {}".format(r.ad, r.soyad),
            format_currency(r.kabul_edilen_butce, 'TL', '#,##0.00 ¤¤¤',
                            locale='tr_TR') if r.kabul_edilen_butce else "-",
            """
            <a class="detail_arrow" href="{}"><span class="fa fa-arrow-circle-right fa-2x "></span>
                </a>
                """.format(url_for('proje.proje_dashboard', proje_id=r.id))] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @property
    def qry(self):
        """
        Proje ve ilgili alanlari icin query nesnesi olustur.
        Returns:
        """
        return DB.session.query(
            Proje
        ).join(
            OgretimElemani, Proje.yurutucu == OgretimElemani.id
        ).join(
            Personel, OgretimElemani.personel_id == Personel.id
        ).join(
            Person, Person.id == Personel.person_id
        ).join(AppState, AppState.id == Proje.proje_durumu_id).join(ProjeTuru,
                                                                    ProjeTuru.id == Proje.proje_turu).add_columns(
            Proje.id,
            Proje.kabul_edilen_butce,
            Proje.kabul_edilen_baslama_tarihi,
            Proje.bitis_tarihi,
            Proje.proje_basligi,
            Proje.proje_turu_numarasi,
            Proje.proje_no,
            Person.ad,
            Person.soyad,
            AppState.state_code,
            ProjeTuru.ad.label("proje_turu_ad")
        )

    @login_required
    @route('/', methods=["GET"])
    @auth.requires(Or(Permission(*permission_dict["bap"]["proje"]["proje_arama"]["projeleri_arama"])),
                   Or(Role("BAP Admin"), Role("BAP Yetkilisi")),
                   menu_registry={'path': '.bap.proje.proje_arama',
                                  'title': _("Proje Arama"), 'order': 3})
    def proje_listele(self):
        """
        Proje arama index sayfasi
        Returns:
            http response

        """
        search_form = SearchForm()
        return render_template('/proje_arama/proje_arama.html', form=search_form)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["proje"]["proje_arama"]["projeleri_arama"])),
                   Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route('/data', methods=["POST"], endpoint="proje_search")
    def proje_arama(self):  # pylint: disable=too-many-branches
        """
        Bap projelerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = SearchForm(**form_data)

        proje_durumu = search_form.proje_durumu.data
        proje_sureci = search_form.proje_sureci.data

        if proje_sureci == "-1":
            qry = qry.filter(or_((AppState.current_app_state == 'basvuru_kabul'),
                                 (AppState.current_app_state == 'devam'),
                                 (AppState.current_app_state == 'son')))
        if proje_sureci == 'AppStates.basvuru_kabul':
            qry = qry.filter(AppState.current_app_state == 'basvuru_kabul')
        if proje_sureci == 'AppStates.devam':
            qry = qry.filter(AppState.current_app_state == 'devam')
        if proje_sureci == 'AppStates.son':
            qry = qry.filter(AppState.current_app_state == 'son')

        if proje_durumu != '0' and proje_durumu != 'None':
            qry = qry.filter(AppState.id == int(proje_durumu))

        if not search_form.validate():
            result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        proje_basligi = search_form.ad.data.strip()
        proje_turu_adi = search_form.proje_turu_adi.data
        proje_no = search_form.proje_no.data
        kabul_edilen_baslama_tarihi = search_form.date.baslama_tarihi.data
        bitis_tarihi = search_form.date.bitis_tarihi.data
        baslama_tarihi_option = search_form.date.baslama_tarihi_option.data
        bitis_tarihi_option = search_form.date.bitis_tarihi_option.data
        yurutucu = search_form.yurutucu.data.strip()
        kabul_edilen_butce = search_form.butce.data
        kabul_edilen_butce_option = search_form.butce_option.data

        if proje_basligi:
            qry = qry.filter(Proje.proje_basligi.ilike('%' + proje_basligi + '%'))

        if proje_turu_adi:
            qry = qry.filter(ProjeTuru.ad.ilike('%' + proje_turu_adi + '%'))

        if proje_no:
            qry = qry.filter(Proje.proje_no == proje_no)

        if yurutucu:
            qry = qry.filter(Person.ad.ilike('%' + yurutucu + '%'))

        if kabul_edilen_butce:
            if kabul_edilen_butce_option == '0':
                qry = qry.filter(Proje.kabul_edilen_butce < kabul_edilen_butce)
            elif kabul_edilen_butce_option == '1':
                qry = qry.filter(
                    cast(Proje.kabul_edilen_butce, String()) == str(kabul_edilen_butce))
            else:
                qry = qry.filter(Proje.kabul_edilen_butce > kabul_edilen_butce)

        if kabul_edilen_baslama_tarihi:
            if baslama_tarihi_option == '0':
                qry = qry.filter(Proje.kabul_edilen_baslama_tarihi <= kabul_edilen_baslama_tarihi)
            if baslama_tarihi_option == '1':
                qry = qry.filter(Proje.kabul_edilen_baslama_tarihi == kabul_edilen_baslama_tarihi)
            if baslama_tarihi_option == '2':
                qry = qry.filter(kabul_edilen_baslama_tarihi <= Proje.kabul_edilen_baslama_tarihi)

        if bitis_tarihi:
            if bitis_tarihi_option == '0':
                qry = qry.filter(Proje.bitis_tarihi <= bitis_tarihi)
            if bitis_tarihi_option == '1':
                qry = qry.filter(Proje.bitis_tarihi == bitis_tarihi)
            if bitis_tarihi_option == '2':
                qry = qry.filter(bitis_tarihi <= Proje.bitis_tarihi)

        result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
