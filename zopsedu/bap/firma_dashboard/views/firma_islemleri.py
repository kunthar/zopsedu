"""Bap Firma modulu"""
from datetime import datetime
from decimal import Decimal
from hashlib import sha512

from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import lazy_gettext as _
from flask_classful import FlaskView, route
from sqlalchemy.sql import or_, desc

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import FirmaYetkilisi
from zopsedu.bap.models.firma_teklif import FirmaTeklifKalemi, DosyaKategori, FirmaTeklifDosya
from zopsedu.bap.models.proje import Proje
from zopsedu.icerik.model import Icerik
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import Person
from zopsedu.models import ProjeSatinAlmaTalebi, AppState, \
    FirmaSatinalmaTeklif, Sablon
from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.models.auth import User, Role as RoleModel, UserRole, RolTipleri
from zopsedu.bap.firma_dashboard.forms.firma_islemleri import FirmaKayitFormu
from zopsedu.lib.db import DB
from zopsedu.models import BapFirma, File
from zopsedu.bap.firma_dashboard.forms.satinalma_teklif import TeklifFormu, TeklifDosyalari
from zopsedu.bap.lib.query_helpers import BapQueryHelpers


# todo: izinnler, user activity, signal !!
class BapFirmaIslemleriView(FlaskView):
    """Bap firma islemleri view classi"""

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["firma_anasayfa_goruntuleme"]),
                   menu_registry={'path': '.bap.firma_dashboard', 'title': _("Anasayfa"),
                                  "order": 0})
    @route('/dashboard', methods=['GET'])
    def firma_dashboard():
        user_id = current_user.id
        firma = DB.session.query(BapFirma).filter(BapFirma.user_id == user_id).one()

        firma_satinalma_teklifleri = DB.session.query(FirmaSatinalmaTeklif).filter(
            FirmaSatinalmaTeklif.firma_id == firma.id).order_by(
            desc(FirmaSatinalmaTeklif.created_at)).all()

        firma_teklifleri = []
        for satinalama_teklif in firma_satinalma_teklifleri:
            toplam_tutar = Decimal("0.00")
            for teklif_kalemi in satinalama_teklif.teklif_kalemleri:
                toplam_tutar += teklif_kalemi.teklif
            data = {
                "teklif_id": satinalama_teklif.id,
                "teklif_tarihi": satinalama_teklif.updated_at,
                "satinalma_durum": satinalama_teklif.satinalma.durumu.description,
                "teklif_verilen_kalem_sayisi": len(satinalama_teklif.teklif_kalemleri),
                "satinalma_kalem_sayisi": len(satinalama_teklif.satinalma.talep_kalemleri),
                "toplam_tutar": toplam_tutar,
                "hizmet_kalemi_adi": satinalama_teklif.teklif_kalemleri[
                    0].satinalma_talep_kalemi.proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama,
                "teklif_tamamlandimi": satinalama_teklif.teklif_tamamlandi_mi,
                "firma_id": firma.id,
                "satinalma_id": satinalama_teklif.satinalma_id
            }
            firma_teklifleri.append(data)

        return render_template("firma_dashboard.html", firma_teklifleri=firma_teklifleri)

    @staticmethod
    @route('/firma-kayit', methods=['GET'])
    def get_firma_kayit():
        """Firma Kayit Ekranini Getirir"""
        firma_kayit_formu = FirmaKayitFormu()
        return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

    @staticmethod
    @route('/firma-kayit', methods=['POST'])
    def firma_kaydet():
        """Firma Kaydeder"""
        firma_kayit_formu = FirmaKayitFormu(request.form)
        file = None

        if not firma_kayit_formu.validate():
            return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

        yetkili_kullanici_bilgileri = firma_kayit_formu.yetkili_user_bilgileri.data
        kullanici_varmi = DB.session.query(User).filter(or_(
            User.username == yetkili_kullanici_bilgileri["yetkili_kullanici_adi"],
            User.email == yetkili_kullanici_bilgileri["yetkili_email"]
        )).first()
        if kullanici_varmi:
            DB.session.rollback()
            flash("Geçersiz kullanıcı adı veya yetkili email adresi. "
                  "Lütfen başka bir kullanıcı ismi veya email ile yeniden deneyiniz.")
            return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

        firma_faaliyet_belgesi = request.files.get(firma_kayit_formu.firma_faaliyet_belgesi_id.name)
        if firma_faaliyet_belgesi:
            file = File(content=firma_faaliyet_belgesi)
            DB.session.add(file)
            DB.session.flush()
        else:
            flash("Firma faaliyet belgesi yüklemek zorundasınız")
            return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

        password = sha512(yetkili_kullanici_bilgileri["password"].encode()).hexdigest()
        # girilen bilgilerden firma icin yetkili bir kullanici yaratilir
        yetkili_kullanici_bilgileri.pop("re_password")
        firma_yetkili_kullanici = User(
            username=yetkili_kullanici_bilgileri["yetkili_kullanici_adi"],
            email=yetkili_kullanici_bilgileri["yetkili_email"],
            password=password)
        DB.session.add(firma_yetkili_kullanici)
        DB.session.flush()

        yeni_person = Person(user_id=firma_yetkili_kullanici.id,
                             ad=firma_kayit_formu.yetkili_adi.data,
                             soyad=firma_kayit_formu.yetkili_soyadi.data,
                             birincil_eposta=firma_kayit_formu.yetkili_user_bilgileri.yetkili_email.data)
        DB.session.add(yeni_person)

        # firma rolunun id si bulunur
        firma_rolu = DB.session.query(RoleModel).filter(RoleModel.name == "BAP Firma").first()

        # firma rolu ve yetkili kullanici arasinda user_role instance olusturulur
        user_role = UserRole(user_id=firma_yetkili_kullanici.id,
                             role_id=firma_rolu.id,
                             rol_tipi=RolTipleri.firma,
                             is_default=True)

        DB.session.add(user_role)
        # girilen bilgilerle yeni firma olusturulur
        yeni_firma = BapFirma(user_id=firma_yetkili_kullanici.id,
                              firma_faaliyet_belgesi_id=file.id,
                              vergi_dairesi_id=firma_kayit_formu.vergi_dairesi_id.data,
                              adres=firma_kayit_formu.adres.data,
                              adi=firma_kayit_formu.adi.data,
                              telefon=firma_kayit_formu.telefon.data,
                              email=firma_kayit_formu.email.data,
                              vergi_kimlik_numarasi=firma_kayit_formu.vergi_kimlik_numarasi.data,
                              faaliyet_belgesi_verilis_tarihi=firma_kayit_formu.faaliyet_belgesi_verilis_tarihi.data,
                              iban=firma_kayit_formu.iban.data,
                              banka_sube_adi=firma_kayit_formu.banka_sube_adi.data,
                              yetkili_adi=firma_kayit_formu.yetkili_adi.data,
                              yetkili_soyadi=firma_kayit_formu.yetkili_soyadi.data,
                              )

        DB.session.add(yeni_firma)
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "firma_kaydet").type_index,
            "nesne": 'BapFirma',
            "nesne_id": yeni_firma.id,
            "ekstra_mesaj": "{} adlı kullanıcı, yeni firma kaydı yaptı.".format(
                current_user.username)
        }
        signal_sender(**signal_payload)

        flash("Firma kayıt işleminiz başarıyla gerçekleşti. "
              "Firma bilgileriniz onaylandıktan sonra sisteme giriş yapabilirsiniz.")
        return render_template("firma_kayit.html", firma_kayit_formu=firma_kayit_formu)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["satinalma_duyuru_listeleme"]),
                   menu_registry={'path': '.bap.satinalma_duyurulari',
                                  'title': _("Satınalma Duyuruları"), "order": 1})
    @route('/satinalma/duyuru', methods=['GET'])
    def satinalma_duyuru_listele():
        # duyuru stateindeki satinalmalari getirebilmek icin ilgili(Satınalma duyurusu yapıldı)
        # state in id si bulunur
        duyuru_state = DB.session.query(AppState).filter(AppState.state_code == "ST5").one()

        # bu sayfaya ulasan kisi firma yetkilisi ise daha once teklif yaptigi satinalmalari
        # gostermemek icin teklif yaptigi satinalmalarin id si getirilir.
        firma = DB.session.query(BapFirma).filter(BapFirma.user_id == current_user.id).first()
        teklif_yapilan_satinalmalar = []
        if firma:
            teklif_yapilan_satinalmalar = [satinalma_teklif.satinalma_id for satinalma_teklif in
                                           firma.firma_teklifleri]

        duyuru_asamasindaki_satinalmalar = DB.session.query(
            ProjeSatinAlmaTalebi.id.label("satinalma_id"),
            Icerik.baslangic_tarihi.label("duyuru_baslangic_tarihi"),
            Icerik.bitis_tarihi.label("duyuru_bitis_tarihi"),
            Icerik.icerik.label("duyuru_icerigi"),
            Icerik.baslik.label("duyuru_baslik"),
            Proje.proje_no.label("proje_no")
        ).join(Icerik, ProjeSatinAlmaTalebi.duyuru_id == Icerik.id).filter(
            ProjeSatinAlmaTalebi.durum_id == duyuru_state.id,
            Icerik.baslangic_tarihi < datetime.now(),
            Icerik.bitis_tarihi > datetime.now(),
            Icerik.aktif_mi == True
        ).join(
            Proje, ProjeSatinAlmaTalebi.proje_id == Proje.id
        ).all()
        return render_template("satinalma_duyuru_listesi.html",
                               satinalma_listesi=duyuru_asamasindaki_satinalmalar,
                               teklif_yapilan_satinalmalar=teklif_yapilan_satinalmalar,
                               firma_id=firma.id)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["satinalmaya_teklif_yapma"]),
                   FirmaYetkilisi())
    @route('/<int:firma_id>/satinalma/<int:satinalma_id>/basvuru', methods=['GET'])
    def get_satinalma_teklif_yap(satinalma_id, firma_id):
        satinalma = BapQueryHelpers.get_satinalma_with_related_field(satinalma_id)

        teklif_formu = TeklifFormu()
        for talep_kalemi in satinalma.talep_kalemleri:
            data = {
                "talep_kalemi": {
                    "talep_kalemi_id": talep_kalemi.id,
                    "kalem_adi": talep_kalemi.proje_kalemi.ad,
                    "sayi": talep_kalemi.talep_miktari,
                    "birim": talep_kalemi.proje_kalemi.birim.name,
                    "teknik_sartname_id": talep_kalemi.teknik_sartname_file_id
                }
            }
            teklif_formu.urunler.append_entry(data)

        return render_template("satinalma_teklif.html", teklif_formu=teklif_formu,
                               firma_id=firma_id)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["satinalmaya_teklif_yapma"]),
                   FirmaYetkilisi())
    @route('/<int:firma_id>/satinalma/<int:satinalma_id>/basvuru', methods=['POST'])
    def post_satinalma_teklif_yap(satinalma_id, firma_id):
        teklif_formu = TeklifFormu(request.form)
        kaydedilecek_teklifler = []
        hata_mesajlari = []
        firma = DB.session.query(BapFirma).filter(BapFirma.user_id == current_user.id).first()
        if not firma:
            hata_mesajlari.append(_("Teklif verebilmeniz için firma yetkilisi olmanız gerekir"))
            return render_template("satinalma_teklif.html", teklif_formu=teklif_formu,
                                   hata_mesajlari=hata_mesajlari)

        daha_once_teklif_verildi_mi = DB.session.query(FirmaSatinalmaTeklif).filter(
            FirmaSatinalmaTeklif.firma_id == firma.id,
            FirmaSatinalmaTeklif.satinalma_id == satinalma_id).all()
        if daha_once_teklif_verildi_mi:
            hata_mesajlari.append(_("Daha önce teklif verdiginiz için tekrar teklif veremezsiniz."))
            return render_template("satinalma_teklif.html", teklif_formu=teklif_formu,
                                   hata_mesajlari=hata_mesajlari)

        for teklif in teklif_formu.urunler:
            if teklif.birim_fiyati.data:
                if not all(
                        [teklif.kdv_orani.data, teklif.teslimat_suresi.data,
                         teklif.marka_model.data]):
                    hata_mesajlari.append(_(
                        "Teklif vermek istediğiniz ürünün bütün alanlarını doldurmak zorundasınız"))
                    break
                else:
                    kaydedilecek_teklifler.append(teklif)
        if not kaydedilecek_teklifler:
            hata_mesajlari.append(_("Kaydı tamamlamak için en az bir ürüne teklif vermelisiniz"))

        satinalma = BapQueryHelpers.get_satinalma_with_related_field(satinalma_id)

        if hata_mesajlari:
            for talep_kalemi in satinalma.talep_kalemleri:
                for teklif in teklif_formu.urunler:
                    if teklif.talep_kalemi.talep_kalemi_id.data == talep_kalemi.id:
                        teklif.talep_kalemi.kalem_adi.data = talep_kalemi.proje_kalemi.ad
                        teklif.talep_kalemi.sayi.data = talep_kalemi.talep_miktari
                        teklif.talep_kalemi.birim.data = talep_kalemi.proje_kalemi.birim.name
                        teklif.talep_kalemi.teknik_sartname_id.data = talep_kalemi.teknik_sartname_file_id
            return render_template("satinalma_teklif.html", teklif_formu=teklif_formu,
                                   hata_mesajlari=hata_mesajlari)
        try:
            yeni_satinalma_teklif = FirmaSatinalmaTeklif(firma_id=firma.id,
                                                         satinalma_id=satinalma_id,
                                                         aciklama=teklif_formu.aciklama.data)
            DB.session.add(yeni_satinalma_teklif)
            DB.session.flush()
            for teklif in kaydedilecek_teklifler:
                for talep_kalemi in satinalma.talep_kalemleri:
                    if teklif.talep_kalemi.talep_kalemi_id.data == talep_kalemi.id:
                        toplam_fiyat = teklif.birim_fiyati.data * talep_kalemi.talep_miktari
                        yeni_teklif = FirmaTeklifKalemi(teklif_id=yeni_satinalma_teklif.id,
                                                        satinalma_talep_kalemi_id=talep_kalemi.id,
                                                        marka_model=teklif.marka_model.data,
                                                        kdv_orani=teklif.kdv_orani.data,
                                                        teklif=toplam_fiyat,
                                                        teslimat_suresi=teklif.teslimat_suresi.data)
                        DB.session.add(yeni_teklif)

            DB.session.commit()
            flash("Teklifleriniz başarıyla kaydedilmiştir. "
                  "Teklifi tamamlamak için gerekli dosyaları yükleyiniz")
        except Exception as exc:
            DB.session.rollback()
            hata_mesajlari.append(_("Kayıt işlemi yapılırken bir hata oluştu. "
                                    "Lütfen daha sonra tekrar deneyiniz"))
            CustomErrorHandler.error_handler(
                                             hata="Satinalmaya firma teklif verirken bir hata oluştu"
                                                  "Satinalma:{}, User:{}, Firma: {}, Hata:{}".format(
                                                 satinalma_id, current_user.username, firma.id,
                                                 exc))
            return render_template("satinalma_teklif.html", teklif_formu=teklif_formu,
                                   hata_mesajlari=hata_mesajlari)
        return redirect(url_for("firma.BapFirmaIslemleriView:get_satinalma_teklif_dosya_yukle",
                                satinalma_id=satinalma_id, firma_id=firma.id))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["satinalmaya_teklif_yapma"]),
                   FirmaYetkilisi())
    @route('/<int:firma_id>/satinalma/<int:satinalma_id>/basvuru-tamamla', methods=['GET'])
    def get_satinalma_teklif_dosya_yukle(satinalma_id, firma_id):

        firma_teklif = DB.session.query(FirmaSatinalmaTeklif).filter(
            FirmaSatinalmaTeklif.satinalma_id == satinalma_id,
            FirmaSatinalmaTeklif.firma_id == firma_id).first()

        guncel_teklif_mektup_sablonu = DB.session.query(Sablon.id.label("sablon_id")).filter(
            Sablon.sablon_tipi_id == 48,
            Sablon.kullanilabilir_mi == True,
            Sablon.query_id != None
        ).order_by(
            desc(Sablon.created_at)
        ).first()

        if not firma_teklif:
            return redirect(url_for("firma.BapFirmaIslemleriView:firma_dashboard"))

        teklif_dosya_formu = TeklifDosyalari()

        teklif_kalemleri_data = get_teklif_kalemleri_data(firma_teklif.teklif_kalemleri)

        return render_template("teklif_dosya_kaydet.html",
                               teklif_dosya_formu=teklif_dosya_formu,
                               teklif_kalemleri_data=teklif_kalemleri_data,
                               firma_id=firma_id,
                               satinalma_id=satinalma_id,
                               firma_teklif_id=firma_teklif.id,
                               teklif_mektubu_sablon_id=guncel_teklif_mektup_sablonu.sablon_id)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["satinalmaya_teklif_yapma"]),
                   FirmaYetkilisi())
    @route('/satinalma/<int:satinalma_id>/firma/<int:firma_id>/basvuru/tamamla', methods=['POST'])
    def post_satinalma_teklif_dosya_yukle(satinalma_id, firma_id):

        firma_teklif = DB.session.query(FirmaSatinalmaTeklif).filter(
            FirmaSatinalmaTeklif.satinalma_id == satinalma_id,
            FirmaSatinalmaTeklif.firma_id == firma_id,
            FirmaSatinalmaTeklif.teklif_tamamlandi_mi == False
        ).first()

        if not firma_teklif:
            return redirect(url_for("firma.BapFirmaIslemleriView:firma_dashboard"))

        teklif_dosya_formu = TeklifDosyalari(request.form)
        if not teklif_dosya_formu.validate():
            teklif_kalemleri_data = get_teklif_kalemleri_data(firma_teklif.teklif_kalemleri)
            return render_template("teklif_dosya_kaydet.html",
                                   teklif_dosya_formu=teklif_dosya_formu,
                                   teklif_kalemleri_data=teklif_kalemleri_data,
                                   firma_id=firma_id,
                                   satinalma_id=satinalma_id)

        hata_mesajlari = []

        for teklif_dosya in teklif_dosya_formu.dosyalar:
            if teklif_dosya.kategori.data == DosyaKategori.teklif_mektubu:
                break
        else:
            hata_mesajlari.append(_("Teklif mektubu dosyası yüklemek zorundasınız"))

        if hata_mesajlari:
            teklif_kalemleri_data = get_teklif_kalemleri_data(firma_teklif.teklif_kalemleri)
            return render_template("teklif_dosya_kaydet.html",
                                   teklif_dosya_formu=teklif_dosya_formu,
                                   teklif_kalemleri_data=teklif_kalemleri_data,
                                   firma_id=firma_id,
                                   satinalma_id=satinalma_id,
                                   hata_mesajlari=hata_mesajlari)
        try:
            for teklif_dosya in teklif_dosya_formu.dosyalar:
                file = request.files.get(teklif_dosya.dosya.name)
                yeni_file = File(user_id=current_user.id, content=file)
                DB.session.add(yeni_file)
                DB.session.flush()
                firma_teklif_dosya = FirmaTeklifDosya(teklif_id=firma_teklif.id,
                                                      file_id=yeni_file.id,
                                                      aciklama=teklif_dosya.aciklama.data,
                                                      dosya_kategori=teklif_dosya.kategori.data.name)
                DB.session.add(firma_teklif_dosya)

            firma_teklif.teklif_tamamlandi_mi = True

            payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "firma_satinalma_teklifi_yapti").type_index,
                "ekstra_mesaj": "{} id li satınalmaya {} isimli kullanıcı tarafından teklif yapıldı.".format(
                    satinalma_id,
                    current_user.username),
                "nesne": "FirmaSatinalmaTeklif",
                "nesne_id": firma_teklif.id,
            }
            signal_sender(**payload)

            proje = DB.session.query(Proje.proje_no.label("proje_no")).filter(
                Proje.id == firma_teklif.satinalma.proje_id).first()
            for bap_admin in bap_yetkili_and_admin_ids():
                payload = {
                    "notification_receiver": bap_admin.person_id,
                    "notification_title": "Satınalma talebine firma teklif yaptı",
                    "notification_message": "{} numaralı projenin {} numaralı satınalma talebine {}"
                                            " isimli firmanın yetkilisi tarafından teklif yapıldı.".format(
                        proje.proje_no,
                        firma_teklif.satinalma.talep_numarasi,
                        firma_teklif.firma.adi),
                }

                signal_sender(log=False, notification=True, **payload)

            DB.session.commit()
            flash("Satınalma teklifiniz başarıyla kaydedilmiştir.")
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Satınalma firma teklifine dosya eklenirken bir hata meydana geldi."
                     "Satinalma:{}, User:{}, Firma Teklif: {}, Hata:{}".format(satinalma_id,
                                                                               current_user.username,
                                                                               firma_teklif.id,
                                                                               exc))
            flash("Beklenmedik bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.")
        return redirect(url_for("firma.BapFirmaIslemleriView:firma_dashboard"))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["firma"]["satinalma_teklif_goruntuleme"]),
                   FirmaYetkilisi())
    @route('/<int:firma_id>/teklif/<int:teklif_id>', methods=['GET'])
    def firma_teklif_detay_goruntule(teklif_id, firma_id):

        firma_teklif = DB.session.query(FirmaSatinalmaTeklif).filter(
            FirmaSatinalmaTeklif.id == teklif_id,
            FirmaSatinalmaTeklif.firma_id == firma_id,
            FirmaSatinalmaTeklif.teklif_tamamlandi_mi == True).first()

        if not firma_teklif:
            return redirect(url_for("firma.BapFirmaIslemleriView:firma_dashboard"))

        teklif_kalemleri_data = get_teklif_kalemleri_data(firma_teklif.teklif_kalemleri)

        return render_template("teklif_detay.html",
                               teklif_kalemleri_data=teklif_kalemleri_data,
                               teklif_dosyalari=firma_teklif.teklif_dosyalari)


def get_teklif_kalemleri_data(teklif_kalemleri):
    teklif_kalemleri_data = []
    for teklif_kalemi in teklif_kalemleri:
        data = {
            "marka_model": teklif_kalemi.marka_model,
            "kdv_orani": teklif_kalemi.kdv_orani,
            "teklif": teklif_kalemi.teklif,
            "teslimat_suresi": teklif_kalemi.teslimat_suresi,
            "kalem_adi": teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.ad,
            "talep_miktari": teklif_kalemi.satinalma_talep_kalemi.talep_miktari,
            "birimi": teklif_kalemi.satinalma_talep_kalemi.proje_kalemi.birim.value
        }
        teklif_kalemleri_data.append(data)
    return teklif_kalemleri_data
