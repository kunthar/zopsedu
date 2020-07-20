"""BAP Proje Arama View Modulu"""

from flask import render_template, request, jsonify
from sqlalchemy.sql import desc
from flask_classful import FlaskView, route
from flask_babel import gettext as _

from zopsedu.auth.lib import auth
from zopsedu.bap.models.proje_turu import ProjeTuru
from zopsedu.bap.proje.forms.proje_arama.proje_arama import BAPProjeSearchForm
from zopsedu.lib.db import DB
from zopsedu.models import Proje, AppState


class BapProjeleriAramaView(FlaskView):
    """Proje Arama"""

    excluded_methods = [
        "qry"
    ]

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.proje_turu_ad,
            r.proje_no if r.proje_no else '-',
            r.proje_basligi] for index, r in enumerate(result)]

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
        ).join(ProjeTuru, ProjeTuru.id == Proje.proje_turu).join(AppState, Proje.proje_durumu_id == AppState.id).\
            filter(AppState.state_code == 'P22').\
            add_columns(
                Proje.id,
                Proje.bitis_tarihi,
                Proje.proje_basligi,
                Proje.proje_turu_numarasi,
                Proje.proje_no,
                ProjeTuru.ad.label("proje_turu_ad")
        )

    @route('/', methods=["GET"])
    @auth.requires(menu_registry={'path': '.bap_proje_arama', 'title': _("BAP Projeleri"), 'order': 5})
    def bap_projeleri_listele(self):
        """
        Projeler arama index sayfasi
        Returns:
            http response

        """
        search_form = BAPProjeSearchForm()

        return render_template('/proje_arama/bap_projeleri.html', form=search_form)

    @route('/data', methods=["POST"], endpoint="bap_projeler_search")
    def projeler_arama(self):  # pylint: disable=too-many-branches
        """
        Bap projelerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = BAPProjeSearchForm(**form_data)

        if not search_form.validate():
            result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        proje_basligi = search_form.proje_ad.data.strip()
        proje_turu_adi = search_form.proje_turu_adi.data
        bitis_tarihi = search_form.date.bitis_tarihi.data
        bitis_tarihi_option = search_form.date.bitis_tarihi_option.data

        if proje_basligi:
            qry = qry.filter(Proje.proje_basligi.ilike('%' + proje_basligi + '%'))

        if proje_turu_adi:
            qry = qry.filter(ProjeTuru.ad.ilike('%' + proje_turu_adi + '%'))

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
