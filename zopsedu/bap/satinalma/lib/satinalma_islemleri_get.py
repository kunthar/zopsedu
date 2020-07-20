from decimal import Decimal

from flask import render_template, render_template_string
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from zopsedu.bap.models.firma_teklif import FirmaTeklifKalemi, FirmaSatinalmaTeklif
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.satinalma.forms.islem_formlari import DurumFormlari, IslemFormlari
from zopsedu.bap.satinalma.lib.common import kdv_dahil_fiyat_hesabi
from zopsedu.lib.db import DB
from zopsedu.models import AppAction, AppState, Sablon
from zopsedu.models.helpers import SiparisDurumu

satinalma_management_methods_get = {}


def satinalma_bilgisi(satinalma_id):
    return DB.session.query(ProjeSatinAlmaTalebi).filter(
        ProjeSatinAlmaTalebi.id == satinalma_id).first()


def proje_bilgisi(proje_id):
    return DB.session.query(Proje).filter(Proje.id == proje_id).first()


def satinalma_durum_aciklamasi(state_code):
    return DB.session.query(AppState.description.label("aciklama"), AppState.state_code.label("kodu")).filter(
        AppState.state_code == state_code).first()


def satinalma_islem_aciklmasi(action_code):
    return DB.session.query(AppAction.description.label("aciklama"), AppAction.action_code.label("kodu")).filter(
        AppAction.action_code == action_code).first()


class StateChangeGet:
    @staticmethod
    def genel_modal_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.GenelForm()

        satinalma = satinalma_bilgisi(satinalma_id)

        aciklma = satinalma_durum_aciklamasi(action_code)

        proje = proje_bilgisi(satinalma.proje_id)

        return render_template("satinalma_dashboard/durum_degisim_modal/genel_modal.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form)



    @staticmethod
    def st5_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST5()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)
        duyuru_sablonu = DB.session.query(Sablon).filter(
            Sablon.sablon_tipi_id == 50,
            Sablon.kullanilabilir_mi == True
        ).order_by(
            desc(Sablon.updated_at)
        ).first()

        if not form:
            proje_kalemleri_data = {
                "talep_kalemleri": [],
                "talep_numarasi": satinalma.talep_numarasi,
            }
            for talep_kalemi in satinalma.talep_kalemleri:
                proje_kalemleri_data["talep_kalemleri"].append({
                    "proje_kalemi_adi": talep_kalemi.proje_kalemi.ad,
                    "birimi": talep_kalemi.proje_kalemi.birim.value,
                    "miktar": talep_kalemi.talep_miktari,
                    "teknik_sartname_id": talep_kalemi.teknik_sartname_file_id,
                })
            duyuru_metni = render_template_string(duyuru_sablonu.sablon_text, data=proje_kalemleri_data)
            modal_form.duyuru_icerigi.data = duyuru_metni

        return render_template("satinalma_dashboard/durum_degisim_modal/st5.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form)

    @staticmethod
    def st6_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST6()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        return render_template("satinalma_dashboard/durum_degisim_modal/st6.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form)

    @staticmethod
    def st7_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST7()

        satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                TalepKalemleri.siparis_takip).joinedload(
                SiparisTakip.kazanan_firma_teklif).joinedload(
                FirmaTeklifKalemi.satinalma_teklif)).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).first()

        aciklama = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        talep_kalemleri_with_firma_teklif = []

        for talep_kalemi in satinalma.talep_kalemleri:
            data = {
                "kalem_adi": talep_kalemi.proje_kalemi.ad,
                "birim": talep_kalemi.proje_kalemi.birim.value,
                "miktar": talep_kalemi.talep_miktari,
                "firma_adi": "-",
                "marka_model": "-",
                "teklif": "-",
                "kdv_orani": "-",
                "teslimat_suresi": "-",
                "kdv_dahil_teklif": 0,
                "siparis_takip_no": "-"
            }
            if talep_kalemi.siparis_takip:
                kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                                                          talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani)
                data.update({
                    "firma_adi": talep_kalemi.siparis_takip.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "marka_model": talep_kalemi.siparis_takip.kazanan_firma_teklif.marka_model,
                    "teklif": talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                    "kdv_orani": talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani,
                    "teslimat_suresi": talep_kalemi.siparis_takip.kazanan_firma_teklif.teslimat_suresi,
                    "kdv_dahil_teklif": kdv_dahil_teklif,
                    "siparis_takip_no": talep_kalemi.siparis_takip.siparis_numarasi
                })
            talep_kalemleri_with_firma_teklif.append(data)

        return render_template("satinalma_dashboard/durum_degisim_modal/st7.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form,
                               talep_kalemleri_data=talep_kalemleri_with_firma_teklif,
                              )

    @staticmethod
    def st9_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST9()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        talep_kalemleri_with_siparis_info = []
        for talep_kalemi in satinalma.talep_kalemleri:
            data = {
                "kalem_adi": talep_kalemi.proje_kalemi.ad,
                "birim": talep_kalemi.proje_kalemi.birim.value,
                "miktar": talep_kalemi.talep_miktari,
                "firma_adi": "-",
                "teklif": "-",
                "kdv_orani": "-",
                "teslimat_suresi": "-",
                "kdv_dahil_teklif": 0,
                "siparis_takip_no": "-",
                "siparis_durumu": "-"
            }
            if talep_kalemi.siparis_takip:
                kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                                                          talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani)
                data.update({
                    "firma_adi": talep_kalemi.siparis_takip.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "teklif": talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                    "kdv_orani": talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani,
                    "teslimat_suresi": talep_kalemi.siparis_takip.kazanan_firma_teklif.teslimat_suresi,
                    "kdv_dahil_teklif": kdv_dahil_teklif,
                    "siparis_takip_no": talep_kalemi.siparis_takip.siparis_numarasi,
                    "siparis_durumu": talep_kalemi.siparis_takip.siparis_durumu.value
                })
            talep_kalemleri_with_siparis_info.append(data)

        return render_template("satinalma_dashboard/durum_degisim_modal/st9.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               talep_kalemleri_with_siparis_info=talep_kalemleri_with_siparis_info,
                               form=modal_form
                              )

    @staticmethod
    def st10_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST10()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        talep_kalemleri_with_siparis_info = []
        for talep_kalemi in satinalma.talep_kalemleri:
            data = {
                "kalem_adi": talep_kalemi.proje_kalemi.ad,
                "birim": talep_kalemi.proje_kalemi.birim.value,
                "miktar": talep_kalemi.talep_miktari,
                "firma_adi": "-",
                "teklif": "-",
                "kdv_orani": "-",
                "teslimat_suresi": "-",
                "kdv_dahil_teklif": 0,
                "siparis_takip_no": "-",
                "siparis_durumu": "-"
            }
            if talep_kalemi.siparis_takip:
                kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                                                          talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani)
                data.update({
                    "firma_adi": talep_kalemi.siparis_takip.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "teklif": talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                    "kdv_orani": talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani,
                    "teslimat_suresi": talep_kalemi.siparis_takip.kazanan_firma_teklif.teslimat_suresi,
                    "kdv_dahil_teklif": kdv_dahil_teklif,
                    "siparis_takip_no": talep_kalemi.siparis_takip.siparis_numarasi,
                    "siparis_durumu": talep_kalemi.siparis_takip.siparis_durumu.value
                })
            talep_kalemleri_with_siparis_info.append(data)

        return render_template("satinalma_dashboard/durum_degisim_modal/st9.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               talep_kalemleri_with_siparis_info=talep_kalemleri_with_siparis_info,
                               form=modal_form
                            )

    @staticmethod
    def st11_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST11()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        return render_template("satinalma_dashboard/durum_degisim_modal/st11.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form
                            )

    @staticmethod
    def st12_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.ST12()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_durum_aciklamasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        talep_kalemleri_with_siparis_info = []
        for talep_kalemi in satinalma.talep_kalemleri:
            data = {
                "kalem_adi": talep_kalemi.proje_kalemi.ad,
                "birim": talep_kalemi.proje_kalemi.birim.value,
                "miktar": talep_kalemi.talep_miktari,
                "firma_adi": "-",
                "teklif": "-",
                "kdv_orani": "-",
                "teslimat_suresi": "-",
                "kdv_dahil_teklif": 0,
                "siparis_takip_no": "-",
                "siparis_durumu": "-"
            }
            if talep_kalemi.siparis_takip:
                kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                                                          talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani)
                data.update({
                    "firma_adi": talep_kalemi.siparis_takip.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "teklif": talep_kalemi.siparis_takip.kazanan_firma_teklif.teklif,
                    "kdv_orani": talep_kalemi.siparis_takip.kazanan_firma_teklif.kdv_orani,
                    "teslimat_suresi": talep_kalemi.siparis_takip.kazanan_firma_teklif.teslimat_suresi,
                    "kdv_dahil_teklif": kdv_dahil_teklif,
                    "siparis_takip_no": talep_kalemi.siparis_takip.siparis_numarasi,
                    "siparis_durumu": talep_kalemi.siparis_takip.siparis_durumu.value
                })
            talep_kalemleri_with_siparis_info.append(data)

        return render_template("satinalma_dashboard/durum_degisim_modal/st9.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               talep_kalemleri_with_siparis_info=talep_kalemleri_with_siparis_info,
                               form=modal_form
                               )


class ActionChangeGet:
    @staticmethod
    def sta1_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA1()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        return render_template("satinalma_dashboard/islem_modal/sta1.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form
                               )

    @staticmethod
    def sta2_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA2()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        proje_satinalma_talebi = DB.session.query(ProjeSatinAlmaTalebi).options(
            joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                TalepKalemleri.proje_kalemi)).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).one()

        for index, talep_kalemi in enumerate(proje_satinalma_talebi.talep_kalemleri):
            data = {
                'talep_kalemi_id': talep_kalemi.id,
                'kalem_adi': talep_kalemi.proje_kalemi.ad,
                'talep_miktari': talep_kalemi.talep_miktari,
                'birim': talep_kalemi.proje_kalemi.birim,
            }

            modal_form.talep_kalemleri.append_entry(data)
            modal_form.talep_kalemleri[index].talep_miktari.render_kw = {'min': 1,
                                                                         'max': talep_kalemi.talep_miktari,
                                                                         'type': 'number'}

        return render_template("satinalma_dashboard/islem_modal/sta2.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form
                               )

    @staticmethod
    def sta3_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA3()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklma = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        return render_template("satinalma_dashboard/islem_modal/sta3.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklma,
                               form=modal_form
                               )

    @staticmethod
    def sta7_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA7()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in satinalma.talep_kalemleri]

            # siparisleri related modelleri ile birlikte getirir
            siparisler = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                    TalepKalemleri.proje_kalemi),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                SiparisTakip.siparis_durumu == SiparisDurumu.firma_bekleniyor
            ).all()

            for siparis in siparisler:
                modal_form.siparisler.append_entry({
                    "secili_mi": False,
                    "siparis_id": siparis.id,
                    "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "proje_kalemi_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "talep_miktari": siparis.satinalma_talep_kalemleri.talep_miktari,
                    "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                })

        return render_template("satinalma_dashboard/islem_modal/sta7_8_9_10.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                               )

    @staticmethod
    def sta8_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA8()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in satinalma.talep_kalemleri]

            # siparisleri related modelleri ile birlikte getirir
            siparisler = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                    TalepKalemleri.proje_kalemi),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                SiparisTakip.siparis_durumu == SiparisDurumu.teslim_alindi
            ).all()

            for siparis in siparisler:
                modal_form.siparisler.append_entry({
                    "secili_mi": False,
                    "siparis_id": siparis.id,
                    "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "proje_kalemi_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "talep_miktari": siparis.satinalma_talep_kalemleri.talep_miktari,
                    "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                })

        return render_template("satinalma_dashboard/islem_modal/sta7_8_9_10.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                              )

    @staticmethod
    def sta9_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA9()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in satinalma.talep_kalemleri]

            # siparisleri related modelleri ile birlikte getirir
            siparisler = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                    TalepKalemleri.proje_kalemi),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                SiparisTakip.siparis_durumu == SiparisDurumu.muayeneye_gonderildi
            ).all()

            for siparis in siparisler:
                modal_form.siparisler.append_entry({
                    "secili_mi": False,
                    "siparis_id": siparis.id,
                    "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "proje_kalemi_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "talep_miktari": siparis.satinalma_talep_kalemleri.talep_miktari,
                    "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                })

        return render_template("satinalma_dashboard/islem_modal/sta7_8_9_10.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                               )

    @staticmethod
    def sta10_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA10()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in satinalma.talep_kalemleri]

            # siparisleri related modelleri ile birlikte getirir
            siparisler = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                    TalepKalemleri.proje_kalemi),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                SiparisTakip.siparis_durumu == SiparisDurumu.muayeneye_gonderildi
            ).all()

            for siparis in siparisler:
                modal_form.siparisler.append_entry({
                    "secili_mi": False,
                    "siparis_id": siparis.id,
                    "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "proje_kalemi_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "talep_miktari": siparis.satinalma_talep_kalemleri.talep_miktari,
                    "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                })

        return render_template("satinalma_dashboard/islem_modal/sta7_8_9_10.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                               )

    @staticmethod
    def sta11_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA11()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in satinalma.talep_kalemleri]

            # siparisleri related modelleri ile birlikte getirir
            siparisler = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                    TalepKalemleri.proje_kalemi),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                SiparisTakip.siparis_durumu == SiparisDurumu.muayene_onayladi
            ).all()

            for siparis in siparisler:
                modal_form.siparis_faturalari.append_entry({
                    "secili_mi": False,
                    "siparis_id": siparis.id,
                    "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "proje_kalemi_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "talep_miktari": siparis.satinalma_talep_kalemleri.talep_miktari,
                    "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                })

        return render_template("satinalma_dashboard/islem_modal/sta11.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                              )

    @staticmethod
    def sta13_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA13()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in satinalma.talep_kalemleri]

            # siparisleri related modelleri ile birlikte getirir
            siparisler = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                    TalepKalemleri.proje_kalemi),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                SiparisTakip.siparis_durumu != SiparisDurumu.siparis_tamamlandi,
                SiparisTakip.siparis_durumu != SiparisDurumu.siparis_iptal_edildi
            ).all()

            for siparis in siparisler:
                modal_form.siparisler.append_entry({
                    "secili_mi": False,
                    "siparis_id": siparis.id,
                    "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "proje_kalemi_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "talep_miktari": siparis.satinalma_talep_kalemleri.talep_miktari,
                    "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                })

        return render_template("satinalma_dashboard/islem_modal/sta7_8_9_10.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                               )

    @staticmethod
    def sta15_get(satinalma_id, form=None, action_code=None):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.STA15()

        satinalma = satinalma_bilgisi(satinalma_id)
        aciklama = satinalma_islem_aciklmasi(action_code)
        proje = proje_bilgisi(satinalma.proje_id)

        if not form:
            talep_kalemleri = satinalma.talep_kalemleri
            for talep_kalemi in talep_kalemleri:
                modal_form.talep_kalemleri.append_entry({
                    "talep_kalemi_id": talep_kalemi.id,
                    "kalem_adi": talep_kalemi.proje_kalemi.ad,
                    "talep_miktari": talep_kalemi.talep_miktari,
                    "birim": talep_kalemi.proje_kalemi.birim.value,
                    "teknik_sartname_id": talep_kalemi.teknik_sartname_file_id
                })

        return render_template("satinalma_dashboard/islem_modal/sta15.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje.id,
                               app_state_description=aciklama,
                               form=modal_form
                               )


action_methods = {
    "STA1": ActionChangeGet.sta1_get,
    "STA2": ActionChangeGet.sta2_get,
    "STA3": ActionChangeGet.sta3_get,
    "STA7": ActionChangeGet.sta7_get,
    "STA8": ActionChangeGet.sta8_get,
    "STA9": ActionChangeGet.sta9_get,
    "STA10": ActionChangeGet.sta10_get,
    "STA11": ActionChangeGet.sta11_get,
    "STA13": ActionChangeGet.sta13_get,
    "STA15": ActionChangeGet.sta15_get,
}

state_change_methods = {
    "ST2": StateChangeGet.genel_modal_get,
    "ST3": StateChangeGet.genel_modal_get,
    "ST4": StateChangeGet.genel_modal_get,
    "ST5": StateChangeGet.st5_get,
    "ST6": StateChangeGet.st6_get,
    "ST7": StateChangeGet.st7_get,
    "ST8": StateChangeGet.genel_modal_get,
    "ST9": StateChangeGet.st9_get,
    "ST10": StateChangeGet.st10_get,
    "ST11": StateChangeGet.st11_get,
    "ST12": StateChangeGet.st12_get,
    "ST13": StateChangeGet.genel_modal_get
}

satinalma_management_methods_get.update(state_change_methods)
satinalma_management_methods_get.update(action_methods)
