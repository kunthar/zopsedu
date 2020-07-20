from flask import render_template, jsonify, request, current_app, url_for
from flask_allows import Or
from flask_classful import FlaskView, route
from babel.numbers import format_currency
from flask_babel import gettext as _
from flask_login import login_required
from sqlalchemy import desc

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaTeklifKalemi, FirmaSatinalmaTeklif
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.models.siparis_takip import SiparisTakip

from zopsedu.bap.satinalma.forms.satinalinan_malzemeler_arama import SatinalinanMalzemelerSearchForm
from zopsedu.lib.db import DB
from zopsedu.models import Person
from zopsedu.models.helpers import SiparisDurumu
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class SatinAlinanMalzemelerView(FlaskView):
    """Bap Satinalma Satınalınan Malzemeler view class"""

    excluded_methods = [
        "qry"
    ]

    @property
    def qry(self):
        """
        ilgili alanlari icin query nesnesi olustur.
        Returns:
        """
        return DB.session.query(SiparisTakip). \
            join(TalepKalemleri, TalepKalemleri.id == SiparisTakip.satinalma_talep_kalemleri_id). \
            join(FirmaTeklifKalemi, FirmaTeklifKalemi.id == SiparisTakip.kazanan_firma_teklif_id). \
            join(FirmaSatinalmaTeklif, FirmaSatinalmaTeklif.id == FirmaTeklifKalemi.teklif_id). \
            join(BapFirma, BapFirma.id == FirmaSatinalmaTeklif.firma_id). \
            join(ProjeKalemi, ProjeKalemi.id == TalepKalemleri.proje_kalemi_id). \
            join(ProjeSatinAlmaTalebi, TalepKalemleri.satinalma_id == ProjeSatinAlmaTalebi.id). \
            join(Proje, Proje.id == ProjeSatinAlmaTalebi.proje_id). \
            join(OgretimElemani, Proje.yurutucu == OgretimElemani.id). \
            join(Personel, OgretimElemani.personel_id == Personel.id). \
            join(Person, Person.id == Personel.person_id). \
            join(HitapUnvan, Personel.unvan == HitapUnvan.id). \
            add_columns(
            ProjeKalemi.ad.label("malzeme_adi"),
            SiparisTakip.siparis_numarasi.label("siparis_numarasi"),
            Proje.proje_no.label("proje_no"),
            Person.ad.label("yurutucu_ad"),
            Person.ad.label("yurutucu_soyad"),
            HitapUnvan.ad.label("yurutucu_unvan"),
            SiparisTakip.kabul_tarihi.label("siparis_kabul_tarihi"),
            TalepKalemleri.talep_miktari.label("talep_miktari"),
            FirmaTeklifKalemi.teklif.label("toplam_fiyati"),
            ProjeKalemi.birim.label("birim"),
            TalepKalemleri.satinalma_id.label("satinalma_id"),
            BapFirma.adi.label("firma_adi")). \
            filter(SiparisTakip.siparis_durumu == SiparisDurumu.siparis_tamamlandi)

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.malzeme_adi,
            r.siparis_numarasi,
            r.firma_adi,
            r.proje_no,
            "{} {} {}".format(r.yurutucu_unvan, r.yurutucu_ad, r.yurutucu_soyad),
            "{}".format(r.siparis_kabul_tarihi.strftime(current_app.config['DATE_FORMAT'])),
            "{} {}".format(r.talep_miktari, r.birim),
            format_currency(r.toplam_fiyati, 'TL', '#,##0.00 ¤¤¤', locale='tr_TR') if r.toplam_fiyati else "-",
            """
            <a class="detail_arrow" href="{}"><span class="fa fa-arrow-circle-right fa-2x "></span>
                </a>
                """.format(url_for('satinalma.satinalma_dashboard', satinalma_id=r.satinalma_id))

        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record})

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["satınalinan_malzemeler_listesi_goruntuleme"]),
                   menu_registry={"path": ".bap.satinalma.satin_alinan_malzemeler",
                                  "title": _("Malzeme Arama")})
    @route('/liste', methods=['GET'])
    def satinalinan_malzemeler_listele(self):
        search_form = SatinalinanMalzemelerSearchForm()
        return render_template("satinalinan_malzemeler.html", form=search_form)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["satinalma"]["satınalinan_malzemeler_listesi_goruntuleme"])),
                   Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route('/data', methods=["POST"], endpoint="satinalinan_malzeme_search")
    def satinalinan_malzeme_ara(self):  # pylint: disable=too-many-branches
        """
         POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.
        Returns:
            http response
        """

        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = SatinalinanMalzemelerSearchForm(**form_data)

        if not search_form.validate():
            result = qry.order_by(desc(SiparisTakip.kabul_tarihi)).offset(form_data['start']).limit(
                form_data['length']).all()
            return self.process_data(result, form_data, total_record)

        malzeme_adi = search_form.malzeme_adi.data
        siparis_no = search_form.siparis_no.data
        proje_no = search_form.proje_no.data
        yurutucu = search_form.yurutucu.data
        siparis_kabul_tarihi = search_form.date.siparis_kabul_tarihi.data
        siparis_kabul_tarihi_option = search_form.date.siparis_kabul_tarihi_option.data
        talep_miktari = search_form.talep_miktari.data
        toplam_fiyati = search_form.toplam_fiyati.data
        toplam_fiyati_option = search_form.toplam_fiyati_option.data
        firma_adi = search_form.firma_adi.data

        if malzeme_adi:
            qry = qry.filter(ProjeKalemi.ad.ilike('%' + malzeme_adi + '%'))
        if siparis_no:
            qry = qry.filter(SiparisTakip.siparis_numarasi.ilike('%' + siparis_no + '%'))
        if proje_no:
            qry = qry.filter(Proje.proje_no.ilike('%' + proje_no + '%'))
        if yurutucu:
            qry = qry.filter(Person.ad.ilike('%' + yurutucu + '%'))
        if firma_adi:
            qry = qry.filter(BapFirma.adi.ilike('%' + firma_adi + '%'))

        if siparis_kabul_tarihi:
            if siparis_kabul_tarihi_option == '0':
                qry = qry.filter(SiparisTakip.kabul_tarihi >= siparis_kabul_tarihi)
            if siparis_kabul_tarihi_option == '1':
                qry = qry.filter(SiparisTakip.kabul_tarihi == siparis_kabul_tarihi)
            if siparis_kabul_tarihi_option == '2':
                qry = qry.filter(SiparisTakip.kabul_tarihi <= siparis_kabul_tarihi)

        if talep_miktari:
            if toplam_fiyati_option == '0':
                qry = qry.filter(TalepKalemleri.talep_miktari <= talep_miktari)
            if toplam_fiyati_option == '1':
                qry = qry.filter(TalepKalemleri.talep_miktari == talep_miktari)
            if toplam_fiyati_option == '2':
                qry = qry.filter(TalepKalemleri.talep_miktari >= talep_miktari)

            qry = qry.filter(TalepKalemleri.talep_miktari == talep_miktari)

        if toplam_fiyati:
            if toplam_fiyati_option == '0':
                qry = qry.filter(FirmaTeklifKalemi.teklif <= toplam_fiyati)
            if toplam_fiyati_option == '1':
                qry = qry.filter(FirmaTeklifKalemi.teklif == toplam_fiyati)
            if toplam_fiyati_option == '2':
                qry = qry.filter(FirmaTeklifKalemi.teklif >= toplam_fiyati)

        result = qry.order_by(desc(ProjeSatinAlmaTalebi.id)).offset(form_data['start']).limit(form_data['length']).all()

        return self.process_data(result, form_data, total_record)


