from datetime import datetime, timedelta

from flask_login import current_user
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import ImmutableMultiDict
from flask_babel import gettext as _

from zopsedu.auth.models.auth import User
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaTeklifKalemi, FirmaSatinalmaTeklif
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.satinalma.forms.islem_formlari import DurumFormlari, IslemFormlari
from zopsedu.bap.satinalma.lib.satinalma_islemleri_get import satinalma_management_methods_get
from zopsedu.bap.satinalma.views.commons import get_satinalma_with_related_fields
from zopsedu.icerik.model import Icerik, IcerikTipi, IcerikBirimTipi
from zopsedu.lib.db import DB
from zopsedu.lib.satinalma_state_dispatcher import SatinalmaStateDispatcher
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models.helpers import StateTypes, ActionTypes, SiparisDurumu
from zopsedu.bap.satinalma.lib.common import kdv_dahil_fiyat_hesabi

satinalma_management_methods_post = {}


def proje_bilgisi(proje_id):
    return DB.session.query(Proje).filter(
        Proje.id == proje_id).first()


def form_to_dict(form_list):
    form_dict = {}

    for form in form_list:
        form_dict.update({
            form['name']: form['value']
        })

    return form_dict


class StateChangePost:
    @staticmethod
    def genel_modal_post(form=None, satinalma_id=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.GenelForm(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st5_post(form=None, satinalma_id=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST5(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                butce_kalemi_adi = "{} - {}({} Kalem)".format(
                    satinalma.butce_kalemi.gider_siniflandirma_kalemi.kodu,
                    satinalma.butce_kalemi.gider_siniflandirma_kalemi.aciklama,
                    len(satinalma.talep_kalemleri)
                )
                icerik = Icerik(birim_tipi=IcerikBirimTipi.bap,
                                tipi=IcerikTipi.satinalma,
                                baslik=butce_kalemi_adi,
                                icerik=genel_form.duyuru_icerigi.data,
                                aktif_mi=True,
                                baslangic_tarihi=genel_form.baslangic_tarihi.data,
                                bitis_tarihi=genel_form.bitis_tarihi.data,
                                ekleyen_id=current_user.id)

                DB.session.add(icerik)
                DB.session.flush()
                satinalma.duyuru_id = icerik.id
                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st6_post(form=None, satinalma_id=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST6(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_duyurusu = DB.session.query(Icerik).filter(
                    Icerik.id == satinalma.duyuru_id).first()

                satinalma_duyurusu.aktif_mi = False

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st7_post(form=None, satinalma_id=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST7(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                    joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                        TalepKalemleri.siparis_takip).joinedload(
                        SiparisTakip.kazanan_firma_teklif).joinedload(
                        FirmaTeklifKalemi.satinalma_teklif)).filter(
                    ProjeSatinAlmaTalebi.id == satinalma_id).first()

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                # satinalma talep kalemleri icin kabul edilmis firma teklifi sonrasi olusan siparis
                # takip modelinde siparis tarihi alani guncellenir
                for talep_kalemi in satinalma.talep_kalemleri:
                    siparis_takip = talep_kalemi.siparis_takip
                    if siparis_takip:
                        siparis_takip.siparis_tarihi = datetime.now()
                        siparis_takip.siparis_durumu = SiparisDurumu.firma_bekleniyor
                        siparis_takip.teslim_edilmesi_beklenen_tarih =datetime.now() + timedelta(days=siparis_takip.kazanan_firma_teklif.teslimat_suresi)

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st9_post(form=None, satinalma_id=None, action_code=None):
        """
        Satınalma talep kalemlerinin hepsinin siparisi verilmisse  ve bütün siparislerin siparis
        durumu "fatura_teslim_alindi" ise state degisimi yapilir.
        """
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST9(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                    joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                        TalepKalemleri.siparis_takip).joinedload(
                        SiparisTakip.kazanan_firma_teklif).joinedload(
                        FirmaTeklifKalemi.satinalma_teklif)).filter(
                    ProjeSatinAlmaTalebi.id == satinalma_id).first()

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                siparisi_tamamlanan_talep_ids = []
                for talep_kalemi in satinalma.talep_kalemleri:
                    siparis_takip = talep_kalemi.siparis_takip
                    if siparis_takip and siparis_takip.siparis_durumu == SiparisDurumu.fatura_teslim_alindi:
                        siparisi_tamamlanan_talep_ids.append(talep_kalemi.id)

                if not (len(satinalma.talep_kalemleri) == len(siparisi_tamamlanan_talep_ids)):
                    DB.session.rollback()
                    template = satinalma_management_methods_get[action_code](
                        satinalma_id=satinalma_id,
                        form=genel_form,
                        action_code=action_code)
                    hata_mesaji = _(
                        "Satınalma gerekli şartları sağlamadığı için durum değişimi yapılamadı")
                    return template, hata_mesaji

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st10_post(form=None, satinalma_id=None, action_code=None):
        """
        Satınalma siparislerinin durumlari "siparis_tamamlandi", "fatura_teslim_alindi " veya
        "siparis_iptal_edildi" olmalidir.
        Satınalma kısmen tamamlandıgında siparise cikilmayan talep kalemlerinin talep miktarları
        rezerv miktardan kullanılabilir miktara aktarılır.
        """
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST10(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                    joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                        TalepKalemleri.siparis_takip).joinedload(
                        SiparisTakip.kazanan_firma_teklif).joinedload(
                        FirmaTeklifKalemi.satinalma_teklif)).filter(
                    ProjeSatinAlmaTalebi.id == satinalma_id).first()

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                siparisi_sonuclanan_talep_ids = []
                siparisi_olan_talep_ids = []
                for talep_kalemi in satinalma.talep_kalemleri:
                    siparis_takip = talep_kalemi.siparis_takip
                    if siparis_takip:
                        siparisi_olan_talep_ids.append(talep_kalemi.id)
                        if siparis_takip.siparis_durumu in [SiparisDurumu.siparis_tamamlandi,
                                                            SiparisDurumu.siparis_iptal_edildi,
                                                            SiparisDurumu.fatura_teslim_alindi]:
                            siparisi_sonuclanan_talep_ids.append(talep_kalemi.id)
                    else:
                        # talep kalemi siparise cikilmamis ise talep miktari rezerv miktardan
                        # dusulur(kullanilabilir miktara aktarilir)
                        talep_miktari = talep_kalemi.talep_miktari
                        talep_kalemi.proje_kalemi.rezerv_edilen_miktar -= talep_miktari

                if not (len(siparisi_olan_talep_ids) == len(siparisi_sonuclanan_talep_ids)):
                    DB.session.rollback()
                    template = satinalma_management_methods_get[action_code](
                        satinalma_id=satinalma_id,
                        form=genel_form,
                        action_code=action_code)
                    hata_mesaji = _(
                        "Bütün siparişlerin gerekli duruma geldiğinden emin olunuz.")
                    return template, hata_mesaji

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st11_post(form=None, satinalma_id=None, action_code=None):
        """
        Satınalma talebi reddedildiğinde;
            - Yurutucu satınalma talebi yaptiginda rezerv edilen talep miktarlarlari kullanilabilir
              (Talep miktari rezerv miktardan dusulur)hale getirilir.
            - Bu statete gelindiginde baska bir islem yapilamaz
        """
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST11(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_kalemleri = satinalma.talep_kalemleri

                for talep_kalemi in satinalma_talep_kalemleri:
                    talep_miktari = talep_kalemi.talep_miktari
                    talep_kalemi.proje_kalemi.rezerv_edilen_miktar -= talep_miktari

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def st12_post(form=None, satinalma_id=None, action_code=None):
        """
        Satinalmanın iptal edilebilmesi için;
            Siparişe çıkılan ürünlerin durumlarının "siparis_iptal_edildi" olması gerekir
        Satınalma iptal edildiginde siparise cikilmayan talep kalemlerinin talep miktarları
        rezerv miktardan kullanılabilir miktara aktarılır.
        """
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.ST12(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                    joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                        TalepKalemleri.siparis_takip).joinedload(
                        SiparisTakip.kazanan_firma_teklif).joinedload(
                        FirmaTeklifKalemi.satinalma_teklif)).filter(
                    ProjeSatinAlmaTalebi.id == satinalma_id).first()

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                siparisi_sonuclanan_talep_ids = []
                siparisi_olan_talep_ids = []
                for talep_kalemi in satinalma.talep_kalemleri:
                    siparis_takip = talep_kalemi.siparis_takip
                    if siparis_takip:
                        siparisi_olan_talep_ids.append(talep_kalemi.id)
                        if siparis_takip.siparis_durumu == SiparisDurumu.siparis_iptal_edildi:
                            siparisi_sonuclanan_talep_ids.append(talep_kalemi.id)
                    else:
                        # talep kalemi siparise cikilmamis ise talep miktari rezerv miktardan
                        # dusulur(kullanilabilir miktara aktarilir)
                        talep_miktari = talep_kalemi.talep_miktari
                        talep_kalemi.proje_kalemi.rezerv_edilen_miktar -= talep_miktari

                if not (len(siparisi_olan_talep_ids) == len(siparisi_sonuclanan_talep_ids)):
                    DB.session.rollback()
                    template = satinalma_management_methods_get[action_code](
                        satinalma_id=satinalma_id,
                        form=genel_form,
                        action_code=action_code)
                    hata_mesaji = _(
                        "Bütün siparişlerin \"Siparis İptal Edildi\" durumuna geldiğinden emin olunuz.")
                    return template, hata_mesaji

                satinalma_dispatcher.state_change(next_app_state_code=action_code,
                                                  triggered_by=current_user.id,
                                                  bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                                  email_gonderilsin_mi=genel_form.email.data,
                                                  yurutucu_log=genel_form.yurutucu_log.data)

                DB.session.commit()
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template


class ActionChangePost:
    @staticmethod
    def sta1_post(satinalma_id, form=None, action_code=None):

        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA1(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)

                satinalma.ilgili_memur_id = genel_form.ilgili_memur.data
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta2_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA2(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                proje_satinalma_talebi = DB.session.query(ProjeSatinAlmaTalebi).options(
                    joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                        TalepKalemleri.proje_kalemi)).filter(
                    ProjeSatinAlmaTalebi.id == satinalma_id).one()

                for proje_satinalma_talep_kalemi in proje_satinalma_talebi.talep_kalemleri:
                    for talep_kalemi in genel_form.talep_kalemleri:
                        if proje_satinalma_talep_kalemi.proje_kalemi_id == talep_kalemi.talep_kalemi_id.data and \
                                proje_satinalma_talep_kalemi.talep_miktari >= talep_kalemi.talep_miktari.data:
                            proje_satinalma_talep_kalemi.talep_miktari = talep_kalemi.talep_miktari.data
                            break

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta3_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA3(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)

                satinalma.duyuru_duzenlensin_mi = True

                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta7_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA7(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in
                                       satinalma.talep_kalemleri]

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

                # proje yurutucusune gonderilecek custom mesaj
                description = ". "
                for form_siparis in genel_form.siparisler:
                    if form_siparis.secili_mi.data:
                        for siparis in siparisler:
                            if siparis.id == form_siparis.siparis_id.data:
                                description += siparis.satinalma_talep_kalemleri.proje_kalemi.ad + ", "
                                siparis.siparis_durumu = SiparisDurumu.teslim_alindi
                                siparis.teslim_tarihi = datetime.now()
                description += " isimli proje kalemleri teslim alındı."

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data,
                                               description=description)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta8_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA8(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in
                                       satinalma.talep_kalemleri]

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

                # proje yurutucusune gonderilecek custom mesaj
                description = ". "
                for form_siparis in genel_form.siparisler:
                    if form_siparis.secili_mi.data:
                        for siparis in siparisler:
                            if siparis.id == form_siparis.siparis_id.data:
                                description += siparis.satinalma_talep_kalemleri.proje_kalemi.ad + ", "
                                siparis.siparis_durumu = SiparisDurumu.muayeneye_gonderildi
                                siparis.muayeneye_gonderilen_tarih = datetime.now()
                description += " isimli proje kalemleri muayene kabul komisyonuna gönderildi."

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data,
                                               description=description)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta9_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA9(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in
                                       satinalma.talep_kalemleri]

                # siparisleri related modelleri ile birlikte getirir
                siparisler = DB.session.query(SiparisTakip).options(
                    joinedload(SiparisTakip.satinalma_talep_kalemleri).joinedload(
                        TalepKalemleri.proje_kalemi),
                    joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                        FirmaTeklifKalemi.satinalma_teklif).joinedload(FirmaSatinalmaTeklif.firma),
                    joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                        FirmaTeklifKalemi.satinalma_teklif).joinedload(
                        FirmaSatinalmaTeklif.firma).joinedload(BapFirma.user).joinedload(
                        User.person).load_only("id"),
                ).filter(
                    SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_ids),
                    SiparisTakip.siparis_durumu == SiparisDurumu.muayeneye_gonderildi
                ).all()

                # proje yurutucusune gonderilecek custom mesaj
                description = ". "
                mesaj_atilacak_firma_bilgisi = []
                for form_siparis in genel_form.siparisler:
                    if form_siparis.secili_mi.data:
                        for siparis in siparisler:
                            if siparis.id == form_siparis.siparis_id.data:
                                description += siparis.satinalma_talep_kalemleri.proje_kalemi.ad + ", "
                                siparis.siparis_durumu = SiparisDurumu.muayene_onayladi
                                siparis.kabul_tarihi = datetime.now()
                                mesaj_atilacak_firma_bilgisi.append({
                                    "yetkili_id": siparis.kazanan_firma_teklif.satinalma_teklif.firma.user.person.id,
                                    "proje_kalem_adi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                                    "siparis_numarasi": siparis.siparis_numarasi
                                })
                description += " isimli proje kalemleri muayene kabul komisyonuna tarafından " \
                               "kabul edildi."

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data,
                                               description=description)

                for firma_bilgisi in mesaj_atilacak_firma_bilgisi:
                    payload = {
                        "notification_receiver": firma_bilgisi["yetkili_id"],
                        "notification_title": "Muayene ve Kabul Tamamlandı",
                        "notification_message": "{} numaralı satınalma talebinin {} isimli kalemine "
                                                "yaptığınız {} numaralı siparişin muayene ve kabulü"
                                                " tamamlandı.".format(
                            satinalma.talep_numarasi,
                            firma_bilgisi["proje_kalem_adi"],
                            firma_bilgisi["siparis_numarasi"])
                    }

                    signal_sender(log=False, notification=True, **payload)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta10_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA10(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in
                                       satinalma.talep_kalemleri]

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

                # proje yurutucusune gonderilecek custom mesaj
                description = ". "
                for form_siparis in genel_form.siparisler:
                    if form_siparis.secili_mi.data:
                        for siparis in siparisler:
                            if siparis.id == form_siparis.siparis_id.data:
                                description += siparis.satinalma_talep_kalemleri.proje_kalemi.ad + ", "
                                siparis.siparis_durumu = SiparisDurumu.muayene_reddetti
                                siparis.kabul_tarihi = datetime.now()
                description += " isimli proje kalemleri muayene kabul komisyonuna tarafından " \
                               "reddedildi"

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data,
                                               description=description)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta11_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA11(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in
                                       satinalma.talep_kalemleri]

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

                # proje yurutucusune gonderilecek custom mesaj
                description = ". "
                for form_siparis in genel_form.siparis_faturalari:
                    if form_siparis.secili_mi.data:
                        for siparis in siparisler:
                            if siparis.id == form_siparis.siparis_id.data:
                                description += siparis.satinalma_talep_kalemleri.proje_kalemi.ad + ", "
                                siparis.siparis_durumu = SiparisDurumu.fatura_teslim_alindi
                                siparis.fatura_no = form_siparis.fatura_no.data
                                siparis.fatura_tarihi = form_siparis.fatura_tarihi.data
                description += " isimli proje kalemlerinin faturaları teslim alındı."

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data,
                                               description=description)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta13_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.STA13(imd)
        template = None
        if genel_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)
                satinalma_talep_ids = [talep_kalemi.id for talep_kalemi in
                                       satinalma.talep_kalemleri]

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

                # proje yurutucusune gonderilecek custom mesaj
                description = ". "
                for form_siparis in genel_form.siparisler:
                    if form_siparis.secili_mi.data:
                        for siparis in siparisler:
                            if siparis.id == form_siparis.siparis_id.data:
                                description += siparis.satinalma_talep_kalemleri.proje_kalemi.ad + ", "
                                proje_kalemi = siparis.satinalma_talep_kalemleri.proje_kalemi
                                siparis.siparis_durumu = SiparisDurumu.siparis_iptal_edildi
                                proje_kalemi.rezerv_edilen_miktar -= siparis.satinalma_talep_kalemleri.talep_miktari
                                kazanan_firma_teklifi = siparis.kazanan_firma_teklif
                                siparis_tutari = kdv_dahil_fiyat_hesabi(
                                    kazanan_firma_teklifi.teklif,
                                    kazanan_firma_teklifi.kdv_orani)
                                proje_kalemi.rezerv_butce -= siparis_tutari
                description += " isimli proje kalemlerinin siparişleri iptal edildi."

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                                               email_gonderilsin_mi=genel_form.email.data,
                                               yurutucu_log=genel_form.yurutucu_log.data,
                                               description=description)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=genel_form,
                                                                     action_code=action_code)
        return template

    @staticmethod
    def sta15_post(satinalma_id, form=None, action_code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        talep_kalemleri_form = IslemFormlari.STA15(imd)
        template = None
        if talep_kalemleri_form.validate():
            try:
                satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

                satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                                action_type=ActionTypes.satinalma,
                                                                entity_type=ProjeSatinAlmaTalebi,
                                                                entity=satinalma)

                for talep_kalemi in satinalma.talep_kalemleri:
                    for talep_kalemi_form in talep_kalemleri_form.talep_kalemleri:
                        if talep_kalemi_form.talep_kalemi_id.data == talep_kalemi.id and talep_kalemi_form.secili_mi.data:
                            talep_kalemi.teknik_sartname_duzenlensin_mi = True

                DB.session.commit()
                satinalma_dispatcher.do_action(next_app_action_code=action_code,
                                               triggered_by=current_user.id,
                                               bap_yetkilisi_notu=talep_kalemleri_form.bap_admin_log.data,
                                               email_gonderilsin_mi=talep_kalemleri_form.email.data,
                                               yurutucu_log=talep_kalemleri_form.yurutucu_log.data)
            except Exception as exc:
                raise Exception(exc)

        else:
            template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                     form=talep_kalemleri_form,
                                                                     action_code=action_code)
        return template


action_methods = {
    "STA1": ActionChangePost.sta2_post,
    "STA2": ActionChangePost.sta2_post,
    "STA3": ActionChangePost.sta3_post,
    "STA7": ActionChangePost.sta7_post,
    "STA8": ActionChangePost.sta8_post,
    "STA9": ActionChangePost.sta9_post,
    "STA10": ActionChangePost.sta10_post,
    "STA11": ActionChangePost.sta11_post,
    "STA13": ActionChangePost.sta13_post,
    "STA15": ActionChangePost.sta15_post,
}

state_change_methods = {
    "ST2": StateChangePost.genel_modal_post,
    "ST3": StateChangePost.genel_modal_post,
    "ST4": StateChangePost.genel_modal_post,
    "ST5": StateChangePost.st5_post,
    "ST6": StateChangePost.st6_post,
    "ST7": StateChangePost.st7_post,
    "ST8": StateChangePost.genel_modal_post,
    "ST9": StateChangePost.st9_post,
    "ST10": StateChangePost.st10_post,
    "ST11": StateChangePost.st11_post,
    "ST12": StateChangePost.st12_post,
    "ST13": StateChangePost.genel_modal_post,
}

satinalma_management_methods_post.update(state_change_methods)
satinalma_management_methods_post.update(action_methods)
