from datetime import timedelta, datetime, date

from flask import render_template, jsonify, url_for, request, current_app
from flask_allows import Or

from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required
from sqlalchemy import desc

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif, FirmaTeklifKalemi
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.satinalma.forms.teslimi_beklenen_firmalar_listesi import TeslimiBeklenenFirmalarSearchForm
from zopsedu.lib.db import DB
from zopsedu.models import Person
from zopsedu.models.helpers import SiparisDurumu
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class TeslimBeklenenFirmalarView(FlaskView):
    """Bap Satinalma Teslim Beklenen Firmalar view class"""

    excluded_methods = [
        "qry"
    ]

    def kalan_gun_sayisi(self, teslim_edilmesi_beklenen_tarih):
        kalan_gun = (datetime(teslim_edilmesi_beklenen_tarih.year, teslim_edilmesi_beklenen_tarih.month,
                              teslim_edilmesi_beklenen_tarih.day) - datetime.now()).days
        if kalan_gun < 0:
            return ("{} Gün geçti".format(abs(kalan_gun)), kalan_gun)

        return ("{} Gün kaldı".format(kalan_gun), kalan_gun)

    @property
    def qry(self):
        """
                Proje ve ilgili alanlari icin query nesnesi olustur.
                Returns:
                """
        return DB.session.query(BapFirma). \
            join(FirmaSatinalmaTeklif, FirmaSatinalmaTeklif.firma_id == BapFirma.id). \
            join(FirmaTeklifKalemi, FirmaTeklifKalemi.teklif_id == FirmaSatinalmaTeklif.id). \
            join(ProjeSatinAlmaTalebi, ProjeSatinAlmaTalebi.id == FirmaSatinalmaTeklif.satinalma_id). \
            join(TalepKalemleri, TalepKalemleri.satinalma_id == ProjeSatinAlmaTalebi.id). \
            join(SiparisTakip, SiparisTakip.satinalma_talep_kalemleri_id == TalepKalemleri.id). \
            join(Proje, Proje.id == ProjeSatinAlmaTalebi.proje_id). \
            join(OgretimElemani, Proje.yurutucu == OgretimElemani.id). \
            join(Personel, OgretimElemani.personel_id == Personel.id). \
            join(Person, Person.id == Personel.person_id). \
            join(HitapUnvan, Personel.unvan == HitapUnvan.id). \
            add_columns(
            BapFirma.adi.label("firma_adi"),
            Proje.proje_no.label("proje_no"),
            SiparisTakip.siparis_numarasi.label("siparis_no"),
            SiparisTakip.siparis_tarihi.label("siparis_tarihi"),
            SiparisTakip.teslim_edilmesi_beklenen_tarih.label("teslim_edilmesi_beklenen_tarih"),
            Person.ad.label("ad"),
            Person.ad.label("soyad"),
            HitapUnvan.ad.label("unvan"),
            ProjeSatinAlmaTalebi.id.label("satinalma_id"),
            FirmaTeklifKalemi.teslimat_suresi.label("teslimat_suresi")
        ). \
            filter(SiparisTakip.siparis_durumu == SiparisDurumu.firma_bekleniyor)

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.firma_adi,
            r.proje_no if r.proje_no else '-',
            r.siparis_no,
            "{} {} {}".format(r.unvan, r.ad, r.soyad),
            '{}'.format(r.siparis_tarihi.strftime(current_app.config['DATE_FORMAT'])),
            '{}'.format(r.teslim_edilmesi_beklenen_tarih.strftime(current_app.config['DATE_FORMAT'])),
            "{}".format(self.kalan_gun_sayisi(r.teslim_edilmesi_beklenen_tarih)[0]),
            """
            <a class="detail_arrow" href="{}"><span class="fa fa-arrow-circle-right fa-2x "></span>
                </a>
                """.format(url_for('satinalma.satinalma_dashboard', satinalma_id=r.satinalma_id))] for index, r in
            enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record})

    @staticmethod
    @login_required
    @route('/', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["teslimi_beklenen_firmalar_listesi_görüntüleme"]),
                   menu_registry={"path": ".bap.satinalma.teslim_beklenen_firmalar",
                                  "title": _("Ürün Teslim Takibi")})
    def teslimi_beklenen_firmalar_listele():
        search_form = TeslimiBeklenenFirmalarSearchForm()
        return render_template("teslimi_beklenen_firmalar.html", form=search_form)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["satinalma"]["teslimi_beklenen_firmalar_listesi_görüntüleme"]),
                      Or(Role("BAP Admin"), Role("BAP Yetkilisi"))))
    @route('/data', methods=["POST"], endpoint="teslim_beklenen_firmalar_search")
    def teslimi_beklenen_firmalar_ara(self):  # pylint: disable=too-many-branches
        """
        Bap projelerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.
        Returns:
            http response
        """

        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = TeslimiBeklenenFirmalarSearchForm(**form_data)

        if search_form.gun_gecikmesi.data == '1':
            qry = qry.filter(SiparisTakip.teslim_edilmesi_beklenen_tarih > date.today())

        elif search_form.gun_gecikmesi.data == '2':
            qry = qry.filter(SiparisTakip.teslim_edilmesi_beklenen_tarih < date.today())

        elif search_form.gun_gecikmesi.data == '3':
            qry = qry.filter(SiparisTakip.teslim_edilmesi_beklenen_tarih == date.today())

        if not search_form.validate():
            result = qry.order_by(desc(SiparisTakip.siparis_tarihi)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        firma_adi = search_form.firma_adi.data
        proje_no = search_form.proje_no.data
        yurutucu = search_form.yurutucu.data
        siparis_no = search_form.siparis_no.data
        siparis_tarihi = search_form.date.siparis_tarihi.data
        siparis_tarihi_option = search_form.date.siparis_tarihi_option.data
        teslim_edilmesi_beklenen_tarih = search_form.date.teslim_edilmesi_beklenen_tarih.data
        teslim_edilmesi_beklenen_tarih_option = search_form.date.teslim_edilmesi_beklenen_tarih_option.data

        if proje_no:
            qry = qry.filter(Proje.proje_no.ilike('%' + proje_no + '%'))

        if yurutucu:
            qry = qry.filter(Person.ad.ilike('%' + yurutucu + '%'))

        if firma_adi:
            qry = qry.filter(BapFirma.adi.ilike('%' + firma_adi + '%'))

        if siparis_no:
            qry = qry.filter(SiparisTakip.siparis_numarasi.ilike('%' + siparis_no + '%'))

        if siparis_tarihi:
            if siparis_tarihi_option == '0':
                qry = qry.filter(SiparisTakip.siparis_tarihi <= siparis_tarihi)
            if siparis_tarihi_option == '1':
                qry = qry.filter(SiparisTakip.siparis_tarihi == siparis_tarihi)
            if siparis_tarihi_option == '2':
                qry = qry.filter(SiparisTakip.siparis_tarihi >= siparis_tarihi)

        if teslim_edilmesi_beklenen_tarih:
            if teslim_edilmesi_beklenen_tarih_option == '0':
                qry = qry.filter(SiparisTakip.teslim_edilmesi_beklenen_tarih <= teslim_edilmesi_beklenen_tarih)
            if teslim_edilmesi_beklenen_tarih_option == '1':
                qry = qry.filter(SiparisTakip.teslim_edilmesi_beklenen_tarih == teslim_edilmesi_beklenen_tarih)
            if teslim_edilmesi_beklenen_tarih_option == '2':
                qry = qry.filter(SiparisTakip.teslim_edilmesi_beklenen_tarih >= teslim_edilmesi_beklenen_tarih)

        result = qry.order_by(desc(SiparisTakip.siparis_tarihi)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
