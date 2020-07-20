from flask import render_template, url_for, jsonify, request
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required
from sqlalchemy import desc, or_

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi
from zopsedu.bap.models.proje_turu import ProjeTuru
from zopsedu.bap.satinalma.forms.satinalma_talepleri_arama import SatinalmaTalepSearchForm
from zopsedu.lib.db import DB
from zopsedu.models import Person, AppState
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class SatinAlmaTalepleriView(FlaskView):
    """Bap Satinalma Talepleri view class"""

    excluded_methods = [
        "qry"
    ]

    @property
    def qry(self):
        """
                Proje ve ilgili alanlari icin query nesnesi olustur.
                Returns:
                """
        return DB.session.query(
            ProjeSatinAlmaTalebi
        ).join(
            Proje, Proje.id == ProjeSatinAlmaTalebi.proje_id
        ).join(
            OgretimElemani, Proje.yurutucu == OgretimElemani.id
        ).join(
            Personel, OgretimElemani.personel_id == Personel.id
        ).join(
            Person, Person.id == Personel.person_id
        ).join(ProjeTuru, ProjeTuru.id == Proje.proje_turu
               ).join(AppState, ProjeSatinAlmaTalebi.durum_id == AppState.id
                      ).add_columns(
            ProjeSatinAlmaTalebi.id,
            ProjeSatinAlmaTalebi.created_at.label("talep_tarihi"),
            Proje.proje_no.label("proje_no"),
            Person.ad,
            Person.soyad,
            AppState.state_code.label("satinalma_durumu"),
            ProjeTuru.ad.label("proje_turu_ad")
        )

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.proje_no if r.proje_no else '-',
            r.satinalma_durumu,
            "{} {}".format(r.ad, r.soyad),
            '{:%d.%m.%Y}'.format(r.talep_tarihi),
            """
            <a class="detail_arrow" href="{}"><span class="fa fa-arrow-circle-right fa-2x "></span>
                </a>
                """.format(url_for('satinalma.satinalma_dashboard', satinalma_id=r.id))] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": len(result),
                        "recordsTotal": total_record})

    @login_required
    @route('/liste', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["satınalma_talepleri_listesi_goruntuleme"]),
                   menu_registry={"path": ".bap.satinalma.satinalma_talepleri",
                                  "title": _("Talepler")})
    def satinalma_talepleri_listele(self):
        search_form = SatinalmaTalepSearchForm()
        return render_template('satinalma_talepleri.html', form=search_form)


    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["satinalma"]["satınalma_talepleri_listesi_goruntuleme"]),
                      Or(Role("BAP Admin"), Role("BAP Yetkilisi"))))
    @route('/data', methods=["POST"], endpoint="satinalma_search")
    def satilama_talebi_ara(self):  # pylint: disable=too-many-branches
        """
        Bap projelerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.
        Returns:
            http response
        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = SatinalmaTalepSearchForm(**form_data)

        talep_durumu = search_form.talep_durumu.data



        satinalma_sureci = search_form.satinalma_sureci.data

        if satinalma_sureci == "-1":
            qry = qry.filter(or_((AppState.current_app_state == 'basvuru_kabul'),
                                 (AppState.current_app_state == 'devam'),
                                 (AppState.current_app_state == 'son')))
        if satinalma_sureci == 'AppStates.basvuru_kabul':
            qry = qry.filter(AppState.current_app_state == 'basvuru_kabul')
        if satinalma_sureci == 'AppStates.devam':
            qry = qry.filter(AppState.current_app_state == 'devam')
        if satinalma_sureci == 'AppStates.son':
            qry = qry.filter(AppState.current_app_state == 'son')



        if talep_durumu != '0' and talep_durumu != 'None':
            qry = qry.filter(AppState.id == int(talep_durumu))

        if not search_form.validate():
            result = qry.order_by(desc(ProjeSatinAlmaTalebi.id)).offset(form_data['start']).limit(
                form_data['length']).all()
            return self.process_data(result, form_data, total_record)

        proje_no = search_form.proje_no.data
        talep_tarihi = search_form.date.talep_tarihi.data
        talep_tarihi_option = search_form.date.talep_tarihi_option.data
        yurutucu = search_form.yurutucu.data
        proje_turu_adi = search_form.proje_turu_adi.data

        if proje_no:
            qry = qry.filter(Proje.proje_no.ilike('%' + proje_no + '%'))

        if yurutucu:
            qry = qry.filter(Person.ad.ilike('%' + yurutucu + '%'))

        if proje_turu_adi:
            qry = qry.filter(ProjeTuru.ad.ilike('%' + yurutucu + '%'))

        if talep_tarihi:
            if talep_tarihi_option == '0':
                qry = qry.filter(ProjeSatinAlmaTalebi.created_at >= talep_tarihi)
            if talep_tarihi_option == '1':
                qry = qry.filter(ProjeSatinAlmaTalebi.created_at == talep_tarihi)
            if talep_tarihi_option == '2':
                qry = qry.filter(ProjeSatinAlmaTalebi.created_at <= Proje.kabul_edilen_baslama_tarihi)

        result = qry.order_by(desc(ProjeSatinAlmaTalebi.id)).offset(form_data['start']).limit(form_data['length']).all()

        return self.process_data(result, form_data, total_record)
