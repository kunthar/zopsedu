"""Satinalma ile ilgil kesilen muhasebe fis islemlerinin tutuldugu modul"""
from decimal import Decimal
from datetime import date

from flask import render_template, request, abort, flash, redirect, url_for, render_template_string
from flask_babel import gettext as _
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import exists

from zopsedu.auth.lib import Permission, auth, Role as RoleReq
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.detayli_hesap_planlari import DetayliHesapPlanlari
from zopsedu.bap.models.firma_teklif import FirmaTeklifKalemi, FirmaSatinalmaTeklif
from zopsedu.bap.models.muhasebe_fisi import MuhasebeFisi, MuhasebeFisMaddesi
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.satinalma.forms.satinalma_dashboard.muhasebe_fisleri import \
    MuhasebeFisiListelemeInformation, MuhasebeFisiForm
from zopsedu.bap.satinalma.views.commons import get_satinalma_with_related_fields, \
    get_satinalma_next_states_info, \
    get_satinalma_actions_info
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.sessions import SessionHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import GenelAyarlar, VergiDairesi, Sablon
from zopsedu.models.helpers import SiparisDurumu
from zopsedu.bap.satinalma.lib.common import kdv_dahil_fiyat_hesabi
from zopsedu.bap.lib.query_helpers import BapQueryHelpers


class SatinalmaMuhasebeFisleri(FlaskView):
    """
        Satinalma muhasebe fisi islemleri
    """

    def get_siparis_with_firma_and_talep_kalemleri(self, siparis_id):
        """
        id si verilen siparisin faturası teslim alındı ise satınalma talep kalemleri ve firma ile
        birlikte getirir
        :param siparis_id: siparis id
        :return: SiparisTakip instance
        """
        siparis = DB.session.query(SiparisTakip).options(
            joinedload(SiparisTakip.satinalma_talep_kalemleri),
            joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                FirmaTeklifKalemi.satinalma_teklif).joinedload(
                FirmaSatinalmaTeklif.firma)
        ).filter(
            SiparisTakip.siparis_durumu == SiparisDurumu.fatura_teslim_alindi,
            SiparisTakip.id == siparis_id
        ).first()
        return siparis

    def get_proje_for_muhasebe_fisi(self, proje_id):
        """
        "proje_id" li projeyi proje yurutucusu fakultesi ve bolumu join edilmis sekilde getirir
        :param proje_id: satinalma proje id
        :return: Proje model instance
        """
        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu),
            joinedload(Proje.fakulte),
            joinedload(Proje.bolum),
            joinedload(Proje.gelir_kasasi)
        ).filter(Proje.id == proje_id).first()
        return proje

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_muhasebe_fisi_goruntule"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/muhase-fisleri', methods=['GET'])
    def muhasebe_fisleri(self, satinalma_id):
        """
        muhasebe fislerini listeleyen view methodu
        :param satinalma_id: ilgili satinalma id
        """

        try:
            satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
            states_info = get_satinalma_next_states_info(satinalma_id=satinalma_id)
            actions_info = get_satinalma_actions_info(satinalma_id=satinalma_id)
            proje = DB.session.query(Proje).filter(Proje.id == satinalma.proje_id).first()

            satinalma_talep_kalemleri_ids = [talep_kalemi.id for talep_kalemi in
                                             satinalma.talep_kalemleri]

            satinalma_muhasebe_fisleri = DB.session.query(MuhasebeFisi).filter(
                MuhasebeFisi.satinalma_talep_id == satinalma_id
            ).all()

            satinalma_siparisleri = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(
                    FirmaSatinalmaTeklif.firma)
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_kalemleri_ids),
                SiparisTakip.siparis_durumu == SiparisDurumu.fatura_teslim_alindi
            ).all()

            siparis_data = []

            for siparis in satinalma_siparisleri:
                kdv_dahil_fiyat = kdv_dahil_fiyat_hesabi(siparis.kazanan_firma_teklif.teklif,
                                                         siparis.kazanan_firma_teklif.kdv_orani)
                if not siparis.satinalma_talep_kalemleri.muhasebe_fis_id:
                    siparis_data.append({
                        "siparis_id": siparis.id,
                        "proje_kalemi": siparis.satinalma_talep_kalemleri.proje_kalemi.ad,
                        "miktar": siparis.satinalma_talep_kalemleri.talep_miktari,
                        "birim": siparis.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                        "kdv_dahil_tutar": kdv_dahil_fiyat,
                        "tutar": siparis.kazanan_firma_teklif.teklif,
                        "siparis_numarasi": siparis.siparis_numarasi,
                        "firma_adi": siparis.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                        "kabul_tarihi": siparis.kabul_tarihi
                    })

            muhasebe_information_form = MuhasebeFisiListelemeInformation()
        except Exception as exc:
            CustomErrorHandler.error_handler(hata="Satinalma muhasebe fişi listesi görüntülenirken "
                                                  "hata oluştu.Hata: {}, Satinalma id: {}".format(
                                                 satinalma_id,
                                                 exc)
                                             )
            return abort(500)

        return render_template("satinalma_dashboard/muhasebe_fisleri.html",
                               muhasebe_information_form=muhasebe_information_form,
                               muhesabe_fisleri=satinalma_muhasebe_fisleri,
                               satinalma_siparisleri=siparis_data,
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               proje=proje,
                               actions_info=actions_info,
                               states_info=states_info)

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_muhasebe_fisi_olustur"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/siparis/<int:siparis_id>/muhase-fisi-olustur', methods=['GET'])
    def muhasebe_fisi_olustur_get(self, satinalma_id, siparis_id):
        """
        Muhasebe fisi olusturma ekrani
        :param satinalma_id: ilgili satinalma id
        :param firma_id: muhasebe fisinin kesilecegi firma id
        """

        try:
            universite_id = SessionHandler.universite_id()
            satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
            proje = self.get_proje_for_muhasebe_fisi(satinalma.proje_id)

            siparis = self.get_siparis_with_firma_and_talep_kalemleri(siparis_id)
            if not siparis:
                flash(_("Böyle bir sipariş bulunamadı"), category="error")
                return redirect(url_for("satinalma.SatinalmaMuhasebeFisleri:muhasebe_fisleri",
                                        satinalma_id=satinalma_id))

            if siparis.satinalma_talep_kalemleri.muhasebe_fis_id:
                flash(_("Bu sipariş için daha önce muhasebe fişi oluşturdunuz."), category="error")
                return redirect(url_for("satinalma.SatinalmaMuhasebeFisleri:muhasebe_fisleri",
                                        satinalma_id=satinalma_id))

            proje_bilgiler_data = self.get_proje_bilgileri(proje)

            genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                                     aktif_mi=True).first()

            firma_bilgileri = siparis.kazanan_firma_teklif.satinalma_teklif.firma
            kisi_bilgileri = self.get_kisi_bilgiler(firma_bilgileri)
            kdv_dahil_alacak = kdv_dahil_fiyat_hesabi(siparis.kazanan_firma_teklif.teklif,
                                                      siparis.kazanan_firma_teklif.kdv_orani)

            proje_kalemi = siparis.satinalma_talep_kalemleri.proje_kalemi
            proje_kalemi_data = self.get_proje_kalemi_data(proje_kalemi, kdv_dahil_alacak)
            fatura_bilgisi_data = self.get_fatura_bilgileri(siparis)

            muhasebe_fis_formu = self.init_muhasebe_fisi_form(genel_ayarlar,
                                                              kisi_bilgileri,
                                                              kdv_dahil_alacak,
                                                              proje,
                                                              fatura_bilgisi_data)
            # simdiki yil ve siparis id birlesiminden belge numarasi uretir
            belge_numarasi = "{}{}".format(date.today().year, siparis.id)
            muhasebe_fis_formu.fis_genel_bilgileri.belge_numarasi.data = belge_numarasi

        except Exception as exc:
            CustomErrorHandler.error_handler(hata="Satinalma muhasebe fişi listesi görüntülenirken "
                                                  "hata oluştu.Hata: {}, Satinalma id: {}".format(
                                                 satinalma_id,
                                                 exc)
                                             )
            return abort(500)

        return render_template("satinalma_dashboard/muhasebe_fisi_olustur.html",
                               muhasebe_fis_formu=muhasebe_fis_formu,
                               proje_bilgileri=proje_bilgiler_data,
                               proje_kalemi_data=proje_kalemi_data,
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               siparis_id=siparis_id)

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_muhasebe_fisi_olustur"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/siparis/<int:siparis_id>/muhase-fisi-olustur', methods=['POST'])
    def muhasebe_fisi_olustur_post(self, satinalma_id, siparis_id):
        """
        Muhasebe fisi olusturma kaydeden view methodu
        :param satinalma_id: ilgili satinalma id
        :param siparis_id: muhasebe fisinin kesilecegi siparis id
        """

        # todo: kasa bilgileri gosterilecek!
        try:
            universite_id = SessionHandler.universite_id()
            satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
            proje = self.get_proje_for_muhasebe_fisi(satinalma.proje_id)

            proje_bilgiler_data = self.get_proje_bilgileri(proje)

            genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                                     aktif_mi=True).first()
            fonksiyonel_kod_choices = self.get_fonksiyonel_kod_choices(
                genel_ayarlar.bap_butce.get("fonksiyonel_kodlar", None)
            )

            siparis = self.get_siparis_with_firma_and_talep_kalemleri(siparis_id)
            kdv_dahil_tutar = kdv_dahil_fiyat_hesabi(siparis.kazanan_firma_teklif.teklif,
                                                     siparis.kazanan_firma_teklif.kdv_orani)
            proje_kalemi = siparis.satinalma_talep_kalemleri.proje_kalemi
            proje_kalemi_data = self.get_proje_kalemi_data(proje_kalemi, kdv_dahil_tutar)

            muhasebe_fis_formu = MuhasebeFisiForm(request.form)
            for fis_maddesi in muhasebe_fis_formu.fis_maddeleri:
                fis_maddesi.fonksiyonel_kod.choices = fonksiyonel_kod_choices

            if not muhasebe_fis_formu.validate():
                return render_template("satinalma_dashboard/muhasebe_fisi_olustur.html",
                                       muhasebe_fis_formu=muhasebe_fis_formu,
                                       proje_bilgileri=proje_bilgiler_data,
                                       proje_kalemi_data=proje_kalemi_data,
                                       satinalma=satinalma,
                                       satinalma_id=satinalma_id,
                                       siparis_id=siparis_id)

            # belge numarasinin daha once atanmis olma durumu kontrol edilir
            belge_numarasi_exist = DB.session.query(exists().where(
                MuhasebeFisi.muhasebe_fis_no == muhasebe_fis_formu.fis_genel_bilgileri.belge_numarasi.data)).scalar()

            if belge_numarasi_exist:
                oneri_belge_numarasi = "{}{}".format(date.today().year, siparis_id)
                hata_mesaji = "Muhasebe fişi belge numarası kullanılmaktadır. (Öneri belge " \
                              "numarası {})".format(oneri_belge_numarasi)
                muhasebe_fis_formu.fis_genel_bilgileri.belge_numarasi.errors.append(hata_mesaji)
                return render_template("satinalma_dashboard/muhasebe_fisi_olustur.html",
                                       muhasebe_fis_formu=muhasebe_fis_formu,
                                       proje_bilgileri=proje_bilgiler_data,
                                       proje_kalemi_data=proje_kalemi_data,
                                       satinalma=satinalma,
                                       satinalma_id=satinalma_id,
                                       siparis_id=siparis_id)

            proje_kalemi = siparis.satinalma_talep_kalemleri.proje_kalemi
            talep_edilen_miktar = siparis.satinalma_talep_kalemleri.talep_miktari
            # firma teklifi kabul edildigi zaman firmanin teklifinin kdv dahil tutari rezerv
            # butce olarak proje kalemine eklenmisti. Muhasebe fisi olusturuldugu anda rezerv
            # edilen para kullanilan paraya aktarilir
            proje_kalemi.rezerv_butce = proje_kalemi.rezerv_butce - kdv_dahil_tutar
            proje_kalemi.kullanilan_butce = proje_kalemi.kullanilan_butce + kdv_dahil_tutar
            # proje yurutucusu satinalma talebi yaptigi anda talep edilen miktar rezerv edilmisti
            # Muhasebe fisi olusturuldugu anda rezerv miktar kullanilan miktara aktarilir
            proje_kalemi.rezerv_edilen_miktar = proje_kalemi.rezerv_edilen_miktar - talep_edilen_miktar
            proje_kalemi.kullanilan_miktar = proje_kalemi.kullanilan_miktar + talep_edilen_miktar

            proje_bilgileri_data = self.get_proje_bilgileri(proje)
            yeni_muhasebe_fisi = self.muhasebe_fisi_kaydet(
                muhasebe_fis_formu,
                proje_bilgileri_data["proje_no"],
                proje_bilgileri_data["proje_yurutucu_ad_soyad"],
                satinalma_id=satinalma_id,
                fis_tutari=kdv_dahil_tutar
            )
            DB.session.add(yeni_muhasebe_fisi)
            DB.session.flush()
            self.muhasebe_fis_maddesi_kaydet(muhasebe_fis_formu.fis_maddeleri,
                                             yeni_muhasebe_fisi.id)

            siparis.satinalma_talep_kalemleri.muhasebe_fis_id = yeni_muhasebe_fisi.id
            siparis.siparis_durumu = SiparisDurumu.siparis_tamamlandi

            projenin_bagli_oldugu_kasa = proje.gelir_kasasi
            projenin_bagli_oldugu_kasa.rezerv_para -= kdv_dahil_tutar
            projenin_bagli_oldugu_kasa.harcanan_para += kdv_dahil_tutar

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("muhasebe_fisi_olusturuldu").type_index,
                "nesne": 'Proje',
                "nesne_id": proje.id,
                "ekstra_mesaj": "{} isimli kullanıcı {} id'li projenin {} id'li proje kaleminde "
                                "yapilan satınalma sonucu {} id 'li {} TL tutarında muhasebe fişi "
                                "oluşturdu".format(
                    current_user.username,
                    proje.id,
                    proje_kalemi.id,
                    yeni_muhasebe_fisi.id,
                    kdv_dahil_tutar
                )
            }
            signal_sender(**signal_payload)

            DB.session.commit()

            flash(_("Muhasebe fişi başarıyla oluşturulmuştur."), category="success")
            return redirect(url_for("satinalma.SatinalmaMuhasebeFisleri:muhasebe_fisleri",
                                    satinalma_id=satinalma_id))

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(hata="Satinalma muhasebe fişi listesi görüntülenirken "
                                                  "hata oluştu.Hata: {}, Satinalma id: {}".format(
                                                 satinalma_id,
                                                 exc)
                                             )
            return abort(500)

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_muhasebe_fisi_olustur"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/muhasebe-fisi/<int:muhasebe_fis_id>', methods=['GET'])
    def get_odeme_emri_sablonu(self, satinalma_id, muhasebe_fis_id):
        """
        Odeme emri sablonunu ilgili muhasebe fisi alanlari ile render edip kullaniciya doner
        """
        try:
            muhasebe_fisi_data = BapQueryHelpers.get_muhasebe_fisi_bilgileri(muhasebe_fis_id)
            # sablon tipi id 49 --> Ödeme Emri Şablonu
            odeme_emri_sablonu = DB.session.query(Sablon).filter(
                Sablon.sablon_tipi_id == 49,
                Sablon.kullanilabilir_mi == True
            ).order_by(desc(Sablon.updated_at)).first()
            muhasebe_fisi = DB.session.query(MuhasebeFisi).filter(
                MuhasebeFisi.id == muhasebe_fis_id).first()
            muhasebe_fisi.odeme_emri_tamamlandi = True
            DB.session.commit()
            return render_template_string(odeme_emri_sablonu.sablon_text, data=muhasebe_fisi_data)

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(hata="Muhasebe fişi ödeme emrine çevrilirken bir hata "
                                                  "oluştu.Hata: {}, Satinalma id: {}, "
                                                  "Muhasebe Fisi id: {}".format(
                                                 satinalma_id,
                                                 muhasebe_fis_id,
                                                 exc)
                                             )
            return abort(500)

    def get_kisi_bilgiler(self, firma_bilgileri):
        """
        Firma bilgilerinden muhasebe fisi formu icin uygun formatta kisi bilgileri olusturur
        :param firma_bilgileri:
        :return:
        """
        kisi_bilgileri = {
            "adi_soyadi": "{} {} - {}".format(
                firma_bilgileri.yetkili_adi,
                firma_bilgileri.yetkili_adi,
                firma_bilgileri.adi
            ),
            "banka_sube": firma_bilgileri.banka_sube_adi,
            "vergi_no": firma_bilgileri.vergi_kimlik_numarasi,
            "hesap_no": firma_bilgileri.iban,
            "vergi_dairesi_id": firma_bilgileri.vergi_dairesi_id,
        }

        return kisi_bilgileri

    def get_fatura_bilgileri(self, siparis):
        """
        Siparis fatura bilgilerinden muhasebe formu icin uygun formatta data olusturur
        :param siparis: Siparis model instance
        :return:
        """
        fatura_bilgileri = {
            "fatura_no": siparis.fatura_no,
            "fatura_tarihi": siparis.fatura_tarihi,
        }

        return fatura_bilgileri

    def get_proje_bilgileri(self, proje):
        """
        proje model instancendan proje bilgileri dict olusturur
        :param proje: Proje model instance
        :return: dict
        """
        proje_bilgiler_data = {
            "proje_no": proje.proje_no,
            "proje_adi": proje.proje_basligi,
            "proje_yurutucu_ad_soyad": "{} {} {}".format(
                proje.proje_yurutucu.hitap_unvan.ad,
                proje.proje_yurutucu.personel.person.ad,
                proje.proje_yurutucu.personel.person.soyad),
            "proje_fakulte": proje.fakulte.ad,
            "proje_bolum": proje.bolum.ad,
        }
        return proje_bilgiler_data

    def init_muhasebe_fisi_form(self, genel_ayarlar, kisi_bilgileri, kdv_dahil_alacak, proje,
                                fatura_bilgisi):
        """
        :param genel_ayarlar: uygulama genel ayarlari
        :param kisi_bilgileri: muhasebe fisinin kesilecegi kisi
        :param kdv_dahil_alacak: firmanin teklifi ve kdv oranindan olusan kdv dahil alacak
        :return: MuhasebeFisiForm
        """
        kurumsal_kod = ""
        genel_ayarlar_butce = {}
        fonksiyonel_kod_choices = []

        if genel_ayarlar:
            genel_ayarlar_butce.update(genel_ayarlar.bap_butce)
            kurumsal_kod = genel_ayarlar_butce.get("kurum_kodu", "")
            fonksiyonel_kod_choices = self.get_fonksiyonel_kod_choices(
                genel_ayarlar_butce.get("fonksiyonel_kodlar", None)
            )

        genel_ayarlar_butce.update(
            {"fakulte_bolum": "{}/{}".format(proje.fakulte.ad, proje.bolum.ad)})
        muhasebe_fis_formu = MuhasebeFisiForm(fis_genel_bilgileri=genel_ayarlar_butce,
                                              odeme_yapilacak_kisi_bilgileri=kisi_bilgileri,
                                              fatura_bilgileri=fatura_bilgisi)

        for index, fis_maddesi in enumerate(muhasebe_fis_formu.fis_maddeleri, start=0):
            fis_maddesi.kurumsal_kod.data = kurumsal_kod
            fis_maddesi.fonksiyonel_kod.choices = fonksiyonel_kod_choices
            fis_maddesi.fonksiyonel_kod.default = fonksiyonel_kod_choices[0]

            if index % 2 == 0:
                fis_maddesi.borc.data = kdv_dahil_alacak
                fis_maddesi.alacak.data = Decimal("0.00")
            else:
                fis_maddesi.borc.data = Decimal("0.00")
                fis_maddesi.alacak.data = kdv_dahil_alacak

        return muhasebe_fis_formu

    def get_fonksiyonel_kod_choices(self, fonksiyonel_kodlar):
        """
        genel ayarlari kaydedilmis fonksiyonel kodlari alip muhasebe fisi maddelerinde kullanmak
        üzere list of tuple a cevirir
        :param fonksiyonel_kodlar: List of dict
        :return: List of tuple
        """
        fonksiyonel_kod_choices = []
        for fonksiyonel_kod in fonksiyonel_kodlar:
            fonksiyonel_kod_choices.append((fonksiyonel_kod.get("kod"),
                                            fonksiyonel_kod.get("kod")))
        return fonksiyonel_kod_choices

    def muhasebe_fisi_kaydet(self, muhasebe_fisi_formu, proje_no, yurutucu_ad_soyad,
                             satinalma_id, fis_tutari):
        vergi_dairesi = DB.session.query(VergiDairesi).filter(
            VergiDairesi.id == muhasebe_fisi_formu.odeme_yapilacak_kisi_bilgileri.vergi_dairesi_id.data).first()
        yeni_muhasebe_fisi = MuhasebeFisi(
            satinalma_talep_id=satinalma_id,
            muhasebe_fis_no=muhasebe_fisi_formu.fis_genel_bilgileri.belge_numarasi.data,
            muhasebe_fis_tarihi=muhasebe_fisi_formu.fis_genel_bilgileri.belge_tarihi.data,
            butce_yili=muhasebe_fisi_formu.fis_genel_bilgileri.yil.data,
            kurum_adi=muhasebe_fisi_formu.fis_genel_bilgileri.kurum_adi.data,
            kurum_kodu=muhasebe_fisi_formu.fis_genel_bilgileri.kurum_kodu.data,
            birim_adi=muhasebe_fisi_formu.fis_genel_bilgileri.birim_adi.data,
            birim_kodu=muhasebe_fisi_formu.fis_genel_bilgileri.birim_kodu.data,
            muhasebe_birim_adi=muhasebe_fisi_formu.fis_genel_bilgileri.muhasebe_birimi_adi.data,
            muhasebe_birim_kodu=muhasebe_fisi_formu.fis_genel_bilgileri.muhasebe_birimi_kodu.data,
            proje_no=proje_no,
            proje_yurutucusu=yurutucu_ad_soyad,
            fakulte_bolum=muhasebe_fisi_formu.fis_genel_bilgileri.fakulte_bolum.data,
            ad_soyad=muhasebe_fisi_formu.odeme_yapilacak_kisi_bilgileri.adi_soyadi.data,
            vergi_kimlik_no=muhasebe_fisi_formu.odeme_yapilacak_kisi_bilgileri.vergi_no.data,
            banka_sube=muhasebe_fisi_formu.odeme_yapilacak_kisi_bilgileri.banka_sube.data,
            banka_iban=muhasebe_fisi_formu.odeme_yapilacak_kisi_bilgileri.hesap_no.data,
            bagli_oldugu_vergi_dairesi=vergi_dairesi.adi,
            fatura_no=muhasebe_fisi_formu.fatura_bilgileri.fatura_no.data,
            fatura_tarihi=muhasebe_fisi_formu.fatura_bilgileri.fatura_tarihi.data,
            fatura_aciklama=muhasebe_fisi_formu.fatura_bilgileri.aciklama.data,
            fis_tutari=fis_tutari
        )

        return yeni_muhasebe_fisi

    def muhasebe_fis_maddesi_kaydet(self, fis_maddeleri_formu, muhasebe_fisi_id):
        for fis_maddesi in fis_maddeleri_formu:
            detayli_hesap_kodu = DB.session.query(DetayliHesapPlanlari).filter(
                DetayliHesapPlanlari.id == fis_maddesi.hesap_kodu.data).first()

            hesap_kod_duzeyleri = self.detayli_hesap_kodu_parser(detayli_hesap_kodu.hesap_kodu)

            yeni_fis_maddesi = MuhasebeFisMaddesi(
                muhasebe_fis_id=muhasebe_fisi_id,
                hesap_kodu=hesap_kod_duzeyleri["hesap_kodu"],
                ekonomik_hesap_kodu=hesap_kod_duzeyleri["ekonomik_kod"],
                kurumsal_kod=fis_maddesi.kurumsal_kod.data,
                fonksiyonel_kod=fis_maddesi.fonksiyonel_kod.data,
                finans_kodu=fis_maddesi.finans_kodu.data,
                borc=fis_maddesi.borc.data,
                alacak=fis_maddesi.alacak.data,
                hesap_ayrinti_adi=detayli_hesap_kodu.ana_hesap_hesap_grubu_yardimci_hesap_adi,
            )
            DB.session.add(yeni_fis_maddesi)

    def detayli_hesap_kodu_parser(self, hesap_kodu):
        """
        Muhasebe fis maddelerini kaydederken hesap kodunu ve ekonomik kodu ayrı ayrı kaydediyoruz.
        630.03.07.00.00 seklinde bir kod geliyor. 630 lu kısım hesap kodu. 03.07.00.00 lı kısım
        ekonomik kodu temsil ediyor. Duruma gore sadece "630" seklinde bir kodda gelebiliyor.
        :param hesap_kodu: detayli hesap plani tablosunda yer alan kod
        :return:
        """
        hesap_kod_duzeyleri = {
            "hesap_kodu": "",
            "ekonomik_kod": "",
        }
        # genel kodu "." ya gore 1 kere split eder
        hesap_kodu_array = hesap_kodu.split(".", 1)
        hesap_kod_duzeyleri["hesap_kodu"] = hesap_kodu_array[0]
        if len(hesap_kodu_array) > 1:
            hesap_kod_duzeyleri["ekonomik_kod"] = hesap_kodu_array[1]

        return hesap_kod_duzeyleri

    def get_proje_kalemi_data(self, proje_kalemi, kdv_dahil_tutar):
        data = {
            "proje_kalemi_adi": proje_kalemi.ad,
            "butce_kalemi_kodu": proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.kodu,
            "butce_kalemi_adi": proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama,
            "fis_tutari": kdv_dahil_tutar,
            "toplam_butce": proje_kalemi.toplam_butce,
            "rezerv_butce": proje_kalemi.rezerv_butce,
            "kullanilan_butce": proje_kalemi.kullanilan_butce,
        }
        return data

