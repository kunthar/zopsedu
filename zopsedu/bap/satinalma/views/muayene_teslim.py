from flask import render_template, request, current_app, url_for, jsonify
from flask_allows import Or

from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required
from sqlalchemy import desc, or_

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif, FirmaTeklifKalemi
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_satinalma_talepleri import TalepKalemleri, ProjeSatinAlmaTalebi
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.satinalma.forms.muayene_teslim_listesi import MuayeneTeslimListesiSearchForm
from zopsedu.lib.db import DB
from zopsedu.models import Person
from zopsedu.models.helpers import SiparisDurumu
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan


class MuayeneTeslimListesiView(FlaskView):
    """Bap Satinalma Muayene teslim listesi view class"""

    @property
    def qry(self):
        """
                Proje ve ilgili alanlari icin query nesnesi olustur.
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
            SiparisTakip.muayeneye_gonderilen_tarih.label("muayeneye_gonderilen_tarih"),
            SiparisTakip.siparis_durumu.label("siparis_durumu"),
            TalepKalemleri.talep_miktari.label("talep_miktari"),
            FirmaTeklifKalemi.teklif.label("toplam_fiyati"),
            ProjeKalemi.birim.label("birim"),
            TalepKalemleri.satinalma_id.label("satinalma_id"),
            BapFirma.adi.label("firma_adi"),
            TalepKalemleri.talep_miktari.label("talpe_miktari"),
            ProjeKalemi.birim.label("birim"))

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.malzeme_adi,
            "{} {}".format(r.talep_miktari, r.birim),
            r.siparis_numarasi,
            r.firma_adi,
            r.proje_no,
            "{} {} {}".format(r.yurutucu_unvan, r.yurutucu_ad, r.yurutucu_soyad),
            "{}".format(r.muayeneye_gonderilen_tarih.strftime(current_app.config['DATE_FORMAT'])),
            "{}".format(r.siparis_durumu.value),
            """
            <a class="detail_arrow" href="{}"><span class="fa fa-arrow-circle-right fa-2x "></span>
                </a>
                """.format(url_for('satinalma.satinalma_dashboard', satinalma_id=r.satinalma_id))

        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record})

    @staticmethod
    @login_required
    @route('/liste', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["muayene_teslim_listesi_goruntuleme"]),
                   menu_registry={"path": ".bap.satinalma.muayene_teslim_listesi",
                                  "title": _("Muayene Takibi")})
    def muayene_teslim_listele():
        search_form = MuayeneTeslimListesiSearchForm()
        return render_template("muayene_teslim_listesi.html", form=search_form)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["satinalma"]["muayene_teslim_listesi_goruntuleme"]),
                      Or(Role("BAP Admin"), Role("BAP Yetkilisi"))))
    @route('/data', methods=["POST"], endpoint="muayene_teslim_listesi_search")
    def muayene_teslim_listesi_ara(self):  # pylint: disable=too-many-branches
        """
        Bap projelerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.
        Returns:
            http response
        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = MuayeneTeslimListesiSearchForm(**form_data)
        muayene_durumu = search_form.muayene_durumu.data

        if muayene_durumu == "-1":
            qry = qry.filter(or_((SiparisTakip.siparis_durumu == 'muayeneye_gonderildi'),
                                 (SiparisTakip.siparis_durumu == 'muayene_onayladi'),
                                 (SiparisTakip.siparis_durumu == 'muayene_reddetti')))
        if muayene_durumu == 'SiparisDurumu.muayeneye_gonderildi':
            qry = qry.filter(SiparisTakip.siparis_durumu == 'muayeneye_gonderildi')
        if muayene_durumu == 'SiparisDurumu.muayene_onayladi':
            qry = qry.filter(SiparisTakip.siparis_durumu == 'muayene_onayladi')
        if muayene_durumu == 'SiparisDurumu.muayene_reddetti':
            qry = qry.filter(SiparisTakip.siparis_durumu == 'muayene_reddetti')

        if not search_form.validate():
            result = qry.order_by(desc(SiparisTakip.muayeneye_gonderilen_tarih)).offset(form_data['start']).limit(
                form_data['length']).all()
            return self.process_data(result, form_data, total_record)

        firma_adi = search_form.firma_adi.data
        malzeme_adi = search_form.malzeme_adi.data
        proje_no = search_form.proje_no.data
        muayeneye_gonderilen_tarih = search_form.date.muayeneye_gonderilen_tarih.data
        muayeneye_gonderilen_tarih_option = search_form.date.muayeneye_gonderilen_tarih_option.data
        yurutucu = search_form.yurutucu.data

        if proje_no:
            qry = qry.filter(Proje.proje_no.ilike('%' + proje_no + '%'))

        if yurutucu:
            qry = qry.filter(Person.ad.ilike('%' + yurutucu + '%'))

        if firma_adi:
            qry = qry.filter(BapFirma.adi.ilike('%' + firma_adi + '%'))

        if malzeme_adi:
            qry = qry.filter(ProjeKalemi.ad.ilike('%' + malzeme_adi + '%'))

        if muayeneye_gonderilen_tarih:
            if muayeneye_gonderilen_tarih_option == '0':
                qry = qry.filter(SiparisTakip.muayeneye_gonderilen_tarih <= muayeneye_gonderilen_tarih)
            if muayeneye_gonderilen_tarih_option == '1':
                qry = qry.filter(SiparisTakip.muayeneye_gonderilen_tarih == muayeneye_gonderilen_tarih)
            if muayeneye_gonderilen_tarih_option == '2':
                qry = qry.filter(SiparisTakip.muayeneye_gonderilen_tarih >= muayeneye_gonderilen_tarih)

        result = qry.order_by(desc(SiparisTakip.muayeneye_gonderilen_tarih)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
