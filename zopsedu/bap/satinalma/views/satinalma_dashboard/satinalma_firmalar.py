"""BAP Satinalma firmalar modülü View Modulu"""
from datetime import datetime, timedelta

from flask import render_template, request, abort, jsonify
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import Permission, auth, Role as RoleReq
from zopsedu.auth.models.auth import User
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif, FirmaTeklifKalemi, \
    TeknikSartnameUygunlukDegerlendirmesi
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.bap.satinalma.forms.satinalma_dashboard.firmalar import FirmalarBolumuInformation
from zopsedu.bap.satinalma.views.commons import get_satinalma_next_states_info, \
    get_satinalma_actions_info
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import AppStateTracker
from zopsedu.models.helpers import JobTypes
from zopsedu.bap.satinalma.lib.common import proje_kalemi_kullanilabilir_butce_hesapla, \
    kdv_dahil_fiyat_hesabi


class SatinalmaFirmalar(FlaskView):
    """
        Satinalma teklif veren firmalari view
    """

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_firmalar_goruntuleme"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/firma-teklifleri', methods=['GET'])
    def satinalma_firma_teklifleri_listele(self, satinalma_id):
        """
        Satinalmaya yapilmis firma tekliflerine ulasmak icin kullanilir
        :param satinalma_id: satinalma_id(int)
        :return: http response
        """
        try:
            satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                joinedload(ProjeSatinAlmaTalebi.proje),
                joinedload(ProjeSatinAlmaTalebi.talep_kalemleri).joinedload(
                    TalepKalemleri.firma_teklif_kalemleri)).filter(
                ProjeSatinAlmaTalebi.id == satinalma_id).first()

            states_info = get_satinalma_next_states_info(satinalma_id=satinalma_id)
            actions_info = get_satinalma_actions_info(satinalma_id=satinalma_id)
            proje = DB.session.query(Proje).filter(Proje.id == satinalma.proje_id).first()

            firma_teklifleri = DB.session.query(FirmaSatinalmaTeklif).options(
                joinedload(FirmaSatinalmaTeklif.firma),
                joinedload(FirmaSatinalmaTeklif.teklif_kalemleri).joinedload(
                    FirmaTeklifKalemi.satinalma_talep_kalemi)).filter(
                FirmaSatinalmaTeklif.satinalma_id == satinalma_id,
                FirmaSatinalmaTeklif.teklif_tamamlandi_mi == True).all()

            satinalma_talep_kalemleri_ids = [talep_kalemi.id for talep_kalemi in
                                             satinalma.talep_kalemleri]

            # teklifi kabul edilen firmalari bulunur.
            siparis_takipleri = DB.session.query(SiparisTakip).options(
                joinedload(SiparisTakip.satinalma_talep_kalemleri),
                joinedload(SiparisTakip.kazanan_firma_teklif).joinedload(
                    FirmaTeklifKalemi.satinalma_teklif).joinedload(
                    FirmaSatinalmaTeklif.firma).lazyload("*")
            ).filter(
                SiparisTakip.satinalma_talep_kalemleri_id.in_(satinalma_talep_kalemleri_ids)).all()

            teklif_kabul_edilen_talepler = set()
            siparis_takip_data = []
            # kabul edilen firma tekliflerini(siparis takipleri) listeler
            for siparis_takip in siparis_takipleri:
                kazanan_firma = siparis_takip.kazanan_firma_teklif
                kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(kazanan_firma.teklif,
                                                          kazanan_firma.kdv_orani)
                siparis_takip_data.append({
                    "siparis_takip_id": siparis_takip.id,
                    "kalem_adi": siparis_takip.satinalma_talep_kalemleri.proje_kalemi.ad,
                    "kalem_aciklama": siparis_takip.satinalma_talep_kalemleri.proje_kalemi.gerekce,
                    "birim": siparis_takip.satinalma_talep_kalemleri.proje_kalemi.birim.value,
                    "miktar": siparis_takip.satinalma_talep_kalemleri.talep_miktari,
                    "firma_adi": siparis_takip.kazanan_firma_teklif.satinalma_teklif.firma.adi,
                    "marka_model": siparis_takip.kazanan_firma_teklif.marka_model,
                    "teklif": siparis_takip.kazanan_firma_teklif.teklif,
                    "kdv_orani": siparis_takip.kazanan_firma_teklif.kdv_orani,
                    "teslimat_suresi": siparis_takip.kazanan_firma_teklif.teslimat_suresi,
                    "kdv_dahil_teklif": kdv_dahil_teklif,
                    "siparis_durumu": siparis_takip.siparis_durumu.value if siparis_takip.siparis_durumu else "-"
                })
                teklif_kabul_edilen_talepler.add(siparis_takip.satinalma_talep_kalemleri_id)

            # firmalarin satinalma talep kalemlerine yaptigi teklif kalemleri datasi olusturulur
            # (kazanan firmasi belirlernmis yani siparis takibi olusturulmus talep kalemleri haric)
            firma_teklif_data = []
            firma_dosyalari_data = []
            for firma_teklif in firma_teklifleri:
                for teklif_kalemi in firma_teklif.teklif_kalemleri:
                    if teklif_kalemi.satinalma_talep_kalemi.id not in teklif_kabul_edilen_talepler:
                        kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(teklif_kalemi.teklif,
                                                                  teklif_kalemi.kdv_orani)
                        firma_teklif_data.append({
                            "satinalma_talep_kalem_id": teklif_kalemi.satinalma_talep_kalemi.id,
                            "firma_teklif_kalemi_id": teklif_kalemi.id,
                            "firma_id": firma_teklif.firma.id,
                            "kalem_adi": teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.ad,
                            "kalem_aciklama": teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.gerekce,
                            "birim": teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.birim.value,
                            "miktar": teklif_kalemi.satinalma_talep_kalemi.talep_miktari,
                            "firma_adi": firma_teklif.firma.adi,
                            "marka_model": teklif_kalemi.marka_model,
                            "teklif": teklif_kalemi.teklif,
                            "kdv_orani": teklif_kalemi.kdv_orani,
                            "teslimat_suresi": teklif_kalemi.teslimat_suresi,
                            "kdv_dahil_teklif": kdv_dahil_teklif,
                            "teknik_sartname_uygunlugu": teklif_kalemi.teknik_sartname_uygunlugu
                        })
                for teklif_dosya in firma_teklif.teklif_dosyalari:
                    firma_dosyalari_data.append({
                        "firma_teklif_dosya_id": firma_teklif.id,
                        "firma_adi": firma_teklif.firma.adi,
                        "file_id": teklif_dosya.file_id,
                        "aciklama": teklif_dosya.aciklama,
                        "dosya_kategorisi": teklif_dosya.dosya_kategori.value
                    })

            information_form = FirmalarBolumuInformation()
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(hata="Satinalma firma teklifleri görüntülenirken hata "
                                                  "oluştu.Hata: {}, Satinalma id: {}".format(
                satinalma_id, exc))
            return abort(500)

        return render_template("satinalma_dashboard/satinalma_firmalar.html",
                               firma_teklifleri=firma_teklif_data,
                               firma_teklif_dosyalari=firma_dosyalari_data,
                               siparis_takip_data=siparis_takip_data,
                               information_form=information_form,
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               proje=proje,
                               actions_info=actions_info,
                               states_info=states_info)

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_firma_teklif_kabul_etme"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/talep-kalemi/<int:talep_kalemi_id>/'
           'firma-teklif-kalemi/<int:firma_teklif_kalemi_id>',
           methods=['POST'])
    def firma_teklif_kabul_et(self, satinalma_id, talep_kalemi_id, firma_teklif_kalemi_id):
        try:
            # sadece st6 durumunda bu işlemin yapilmasini saglanir
            satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                joinedload(ProjeSatinAlmaTalebi.durumu),
                lazyload("*")
            ).filter(ProjeSatinAlmaTalebi.id == satinalma_id).first()

            if not satinalma.durumu.id == 39:
                return jsonify(status="error",
                               error_message="Sadece \"{}\" durumunda bu işlemi "
                                             "gerçekleştirebilirsin".format(
                                   satinalma.durumu.description)), 405

            # ilgili talep kalemi icin daha önce bir teklifi kabul etmis ise gerekli hata
            # mesaji donulur
            siparis_takip = DB.session.query(SiparisTakip).filter(
                SiparisTakip.kazanan_firma_teklif_id == firma_teklif_kalemi_id,
                SiparisTakip.satinalma_talep_kalemleri_id == talep_kalemi_id).first()

            if siparis_takip:
                return jsonify(status="error",
                               error_message="İlgili talep kalemi için kabul edilmis "
                                             "bir teklif mevcut. Başka bir teklif kabul etmek "
                                             "için daha önce kabul ettiğiniz teklifi iptal ediniz"
                               ), 409

            firma_teklif_kalemi = DB.session.query(FirmaTeklifKalemi).filter(
                FirmaTeklifKalemi.id == firma_teklif_kalemi_id,
                FirmaTeklifKalemi.satinalma_talep_kalemi_id == talep_kalemi_id).first()

            if not firma_teklif_kalemi:
                return jsonify(status="error", error_message="Böyle bir teklif bulunamadı"), 404

            # siparis numarasi proje numarasi, firma_teklif_kalemi_id ve talep_kalemi_id nin
            # birlesiminden olusur
            siparis_numarasi = "{}{}{}".format(satinalma.proje_id,
                                               firma_teklif_kalemi_id,
                                               talep_kalemi_id)
            yeni_siparis_takip = SiparisTakip(satinalma_talep_kalemleri_id=talep_kalemi_id,
                                              kazanan_firma_teklif_id=firma_teklif_kalemi_id,
                                              siparis_numarasi=siparis_numarasi)

            DB.session.add(yeni_siparis_takip)
            talep_kalemi = DB.session.query(TalepKalemleri).filter(
                TalepKalemleri.id == talep_kalemi_id).first()

            # proje kaleminde bulunan rezerv butce kdv dahil firma teklifi kadar artirilir
            proje_kalemi = talep_kalemi.proje_kalemi
            kullanilabilir_butce = proje_kalemi_kullanilabilir_butce_hesapla(proje_kalemi)
            teklif_kdv_dahil_tutari = kdv_dahil_fiyat_hesabi(firma_teklif_kalemi.teklif,
                                                             firma_teklif_kalemi.kdv_orani)
            if not (kullanilabilir_butce >= teklif_kdv_dahil_tutari):
                # eger yeterli kullanilabilir butce yoksa kullanıcıya hata donulur
                return jsonify(
                    status="error",
                    error_message="Proje kaleminin yeterli kullanılabilir bütçesi bulunmamakta. "
                                  "Proje kaleminin kullanılabilir bütcesi {}, firmanın kdv dahil "
                                  "teklif tutarı {}".format(kullanilabilir_butce,
                                                            teklif_kdv_dahil_tutari)
                ), 404

            proje_kalemi.rezerv_butce = proje_kalemi.rezerv_butce + teklif_kdv_dahil_tutari

            state_tracker = AppStateTracker(state_id=satinalma.durum_id,
                                            triggered_by=current_user.id,
                                            params={"proje_id": satinalma.proje_id,
                                                    "satinalma_id": satinalma.id},
                                            date=datetime.now(),
                                            description="Firma teklifi kabul edildi",
                                            job_type=JobTypes.satinalma_action)
            DB.session.add(state_tracker)

            DB.session.commit()

            ekstra_mesaj = "{} id li talep kalemi için {} id li firma teklifi kabul edildi. {} id " \
                           "li siparis takip kaydı oluşturuldu".format(talep_kalemi_id,
                                                                       firma_teklif_kalemi_id,
                                                                       yeni_siparis_takip.id)
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "firma_teklifi_kabul_edildi").type_index,
                "nesne": "SiparisTakip",
                "nesne_id": yeni_siparis_takip.id,
                "ekstra_mesaj": ekstra_mesaj
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Firma teklifi kabul edilirken beklenmedik bir hata oluştu."
                     "Hata: {}, Satinalma id: {}, Firma Teklif Kalemi Id: {}".format(
                    satinalma_id,
                    exc,
                    firma_teklif_kalemi_id))
            return jsonify(status="error"), 500

    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["satinalma"]["satinalma_firma_teklif_silme"]),
           RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/siparis-takip/<int:siparis_takip_id>',
           methods=['DELETE'])
    def firma_teklif_sil(self, satinalma_id, siparis_takip_id):
        try:
            # sadece st6 durumunda bu işlemin yapilmasini saglanir
            satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                joinedload(ProjeSatinAlmaTalebi.durumu),
                lazyload("*")
            ).filter(ProjeSatinAlmaTalebi.id == satinalma_id).first()

            if not satinalma.durumu.id == 39:
                return jsonify(status="error",
                               error_message="Sadece \"{}\" durumunda bu işlemi "
                                             "gerçekleştirebilirsin".format(
                                   satinalma.durumu.description)), 405

            siparis_takip = DB.session.query(SiparisTakip).filter(
                SiparisTakip.id == siparis_takip_id
            ).options(
                joinedload(SiparisTakip.kazanan_firma_teklif),
                joinedload(SiparisTakip.satinalma_talep_kalemleri),
            ).first()

            if not siparis_takip:
                return jsonify(status="error",
                               error_message="İlgili siparis bulunamadı"), 404

            # proje kaleminin rezerv butcesi firmanin kdv dahil teklifi kadar azaltilir
            firma_teklif = siparis_takip.kazanan_firma_teklif
            proje_kalemi = siparis_takip.satinalma_talep_kalemleri.proje_kalemi

            kdv_dahil_teklif = kdv_dahil_fiyat_hesabi(firma_teklif.teklif,
                                                      firma_teklif.kdv_orani)

            proje_kalemi.rezerv_butce = proje_kalemi.rezerv_butce - kdv_dahil_teklif

            DB.session.delete(siparis_takip)
            state_tracker = AppStateTracker(state_id=satinalma.durum_id,
                                            triggered_by=current_user.id,
                                            params={"proje_id": satinalma.proje_id,
                                                    "satinalma_id": satinalma.id},
                                            date=datetime.now(),
                                            description="Kabul edilen firma teklifi iptal edildi",
                                            job_type=JobTypes.satinalma_action)
            DB.session.add(state_tracker)
            DB.session.commit()

            ekstra_mesaj = "{} id li talep kalemi için kabul edilen {} id li firma teklif kalemi " \
                           "iptal edildi.".format(siparis_takip.satinalma_talep_kalemleri_id,
                                                  siparis_takip.kazanan_firma_teklif_id)
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "kabul_edilen_firma_teklifi_silindi").type_index,
                "nesne": "SiparisTakip",
                "ekstra_mesaj": ekstra_mesaj
            }
            signal_sender(**signal_payload)

            return jsonify(status="success")

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Kabul edilen firma teklifi iptal edilirken beklenmedik bir hata oluştu."
                     "Hata: {}, Satinalma id: {}".format(
                    satinalma_id,
                    exc))
            return jsonify(status="error"), 500

    @staticmethod
    @login_required
    @auth.requires(Or(Permission(
        *permission_dict["bap"]["satinalma"]["firma_tekliflerinin_teknik_sartnameye_uygunlugu"]),
        RoleReq('BAP Yetkilisi'), RoleReq("BAP Admin")))
    @route('/<int:satinalma_id>/talep-kalemi/<int:talep_kalemi_id>/firma-teklif-kalemi/'
           '<int:firma_teklif_kalemi_id>/teknik-sartname/degerlendir', methods=['POST'])
    def firma_tekllif_teknik_sartname_degerlendirmesi(satinalma_id, talep_kalemi_id,
                                                      firma_teklif_kalemi_id):
        """
        Firma teklif kaleminin ilgili teknikşartnameye uygunlugunun degistirildigi view methodu
        :param satinalma_id: satinalma id
        :param talep_kalemi_id: satınalma talep kalemi id
        :param firma_teklif_kalemi_id: firma teklif kalemi id
        """

        try:
            # sadece st6 durumunda bu işlemin yapilmasini saglanir
            satinalma = DB.session.query(ProjeSatinAlmaTalebi).options(
                joinedload(ProjeSatinAlmaTalebi.durumu),
                lazyload("*")
            ).filter(ProjeSatinAlmaTalebi.id == satinalma_id).first()

            if not satinalma.durumu.id == 39:
                return jsonify(status="error",
                               error_message="Sadece \"{}\" durumunda bu işlemi "
                                             "gerçekleştirebilirsin".format(
                                   satinalma.durumu.description)), 405
            teknik_sartnameye_uygun_mu = request.get_json().get("uygunMu")

            if teknik_sartnameye_uygun_mu is None:
                return jsonify("error"), 500

            firma_teklif = DB.session.query(FirmaTeklifKalemi).options(
                joinedload(FirmaTeklifKalemi.satinalma_teklif).joinedload(
                    FirmaSatinalmaTeklif.firma).joinedload(
                    BapFirma.user).joinedload(User.person).load_only("id"),
                joinedload(FirmaTeklifKalemi.satinalma_teklif).lazyload("*"),
                joinedload(FirmaTeklifKalemi.satinalma_talep_kalemi).joinedload(
                    TalepKalemleri.proje_kalemi).load_only("ad")
            ).filter(
                FirmaTeklifKalemi.satinalma_talep_kalemi_id == talep_kalemi_id,
                FirmaTeklifKalemi.id == firma_teklif_kalemi_id
            ).first()

            if not firma_teklif:
                return jsonify(status="error", error_message="Böyle bir teklif bulunamadı"), 404

            firma_teklif.teknik_sartname_uygunlugu = TeknikSartnameUygunlukDegerlendirmesi.uygun if \
                teknik_sartnameye_uygun_mu else TeknikSartnameUygunlukDegerlendirmesi.uygun_degil

            state_tracker = AppStateTracker(state_id=satinalma.durum_id,
                                            triggered_by=current_user.id,
                                            params={"proje_id": satinalma.proje_id,
                                                    "satinalma_id": satinalma.id},
                                            date=datetime.now(),
                                            description="Firma teklifi teknik şartname uygunluğu değerlendirildi",
                                            job_type=JobTypes.satinalma_action)
            DB.session.add(state_tracker)

            DB.session.commit()

            ekstra_mesaj = "{} id li firma teklifinin teknik şartname uygunluğu {} olarak " \
                           "değiştirildi.".format(firma_teklif.id,
                                                  firma_teklif.teknik_sartname_uygunlugu.value)
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "firma_teklif_teknik_sartname_degerlendirmesi").type_index,
                "nesne": "FirmaTeklifKalemi",
                "ekstra_mesaj": ekstra_mesaj
            }
            signal_sender(**signal_payload)

            payload = {
                "notification_receiver": firma_teklif.satinalma_teklif.firma.user.person.id,
                "notification_title": "Teknik Şartnameye Uygunluk Değerlendirildig",
                "notification_message": "{} numaralı satınalma talebinin {} isimli kalemine "
                                        "yaptığınız teklifin teknik şartnameye uygunluğu {} olarak "
                                        "belirlendi".format(satinalma.talep_numarasi,
                                                            firma_teklif.satinalma_talep_kalemi.proje_kalemi.ad,
                                                            firma_teklif.teknik_sartname_uygunlugu.value),
            }

            signal_sender(log=False, notification=True, **payload)

            return jsonify(status="success")

        except Exception as exc:
            CustomErrorHandler.error_handler(
                hata="Firma teklifi teknik şartname uygunlugu değerlendirilirken bir hata oluştu."
                     "Hata: {}, Satinalma id: {}, Firma Teklif Kalemi Id: {}".format(
                    satinalma_id,
                    exc,
                    firma_teklif_kalemi_id))
            return jsonify(status="error"), 500
