"""Proje Türü View Metotları"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-nested-blocks

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from flask import render_template, request, redirect, current_app, url_for, flash
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required, current_user

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.helpers import form_errors_dict_to_set
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_turu import ZopseduModelValueError
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import ProjeTuru, BAPBelge, PersonelAyarlari, Butce, Cikti, EkDosya, \
    Form, ButceKalemi, File
from zopsedu.bap.models.helpers import PROJE_TURU_UYARI_MESAJ_TIPLERI, ButceTercihleri
from zopsedu.bap.proje.forms.proje_turu.proje_turu import ProjeTuruFormu
from zopsedu.auth.lib import auth, Permission
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class ProjeTuruKaydetView(FlaskView):
    """Proje Türü View"""

    excluded_methods = ["proje_turu_ek_dosya_olustur",
                        "proje_turu_cikti_olustur",
                        "init_proje_turu_form",
                        "init_sabit_butce_kalemleri",
                        "get_forms_with_type"]

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/kaydet', methods=["POST"], endpoint='proje_turu_kaydet')
    def kaydet(self):
        """Yeni proje turu kaydet"""
        versiyonlanacak_proje_turu_id = request.args.get("id", None)
        proje_turu_formu = ProjeTuruFormu(request.form)
        eski_proje_turu = None

        if not proje_turu_formu.validate():
            hata_listesi = set()

            form_errors_dict_to_set(proje_turu_formu.errors, hata_listesi)
            proje = None
            if versiyonlanacak_proje_turu_id:
                proje = DB.session.query(Proje.proje_turu).filter(
                    Proje.proje_turu == versiyonlanacak_proje_turu_id).all()

            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=proje_turu_formu,
                                   guncel_mi=True,
                                   proje_turu_id=versiyonlanacak_proje_turu_id if versiyonlanacak_proje_turu_id else None,
                                   basvuru_yapilmis_mi=True if proje else False,
                                   hata_mesajlari=hata_listesi)

        # Bu kontrol requestin proje_türü oluşturmak için veya var olan bir proje türünü
        # versiyonlamak için mi atıldığını kontrol eder
        if versiyonlanacak_proje_turu_id:
            # url parametresi id değeri varsa versiyonlama işlemi yapılacak demektir.
            # gelen id geçerli bir proje_turu id olup olmadığı kontrol edilir.
            eski_proje_turu = DB.session.query(ProjeTuru).filter_by(
                id=versiyonlanacak_proje_turu_id).first()
            if not eski_proje_turu:
                return redirect("/bap/proje-turu")
            else:
                # Proje türü adı kontrolü yapılır.Eğer farklı tür kodlu bir proje_turu bu adı
                # kullanıyorsa gerekli hata mesajı dönülür
                if proje_turu_formu.ad.data != eski_proje_turu.ad:
                    mevcut_proje_turu = DB.session.query(ProjeTuru).filter(
                        ProjeTuru.ad == proje_turu_formu.ad.data and
                        ProjeTuru.tur_kodu != eski_proje_turu.tur_kodu).scalar()
                    if mevcut_proje_turu:
                        proje = DB.session.query(Proje.proje_turu).filter(
                            Proje.proje_turu == versiyonlanacak_proje_turu_id).all()
                        proje_turu_formu.ad.errors.append(
                            _("Proje Türü Adı Kullanılmaktadır. Lütfen Başka Bir Ad ile "
                              "Tekrar Deneyiniz"))
                        return render_template("proje_turu/proje_turu.html",
                                               proje_turu_formu=proje_turu_formu,
                                               proje_turu_id=versiyonlanacak_proje_turu_id,
                                               guncel_mi=eski_proje_turu.guncel_mi,
                                               basvuru_yapilmis_mi=True if proje else False)
            tur_kodu = eski_proje_turu.tur_kodu

        else:
            # Url ile birlikte bir id değeri gelmediği için
            # yeni bir proje türü kaydedilecek demektir.
            if DB.session.query(ProjeTuru).filter_by(ad=proje_turu_formu.ad.data).first():
                proje_turu_formu.ad.errors.append(
                    _("Proje Türü Adı Kullanılmaktadır. Lütfen Başka Bir Ad ile Tekrar Deneyiniz"))
                return render_template("proje_turu/proje_turu.html",
                                       proje_turu_formu=proje_turu_formu,
                                       basvuru_yapilmis_mi=False,
                                       aktif_mi=True)

            max_tur_kodu = DB.session.query(func.max(ProjeTuru.tur_kodu)).first()[0]
            tur_kodu = max_tur_kodu + 1 if max_tur_kodu else 1
        try:
            try:
                # formun içerisindeki uyarı mesajlarından dict oluşturulur.
                genel_uyari_mesajlari = {}
                for uyari_mesaji in PROJE_TURU_UYARI_MESAJ_TIPLERI:
                    mesaj = getattr(proje_turu_formu, uyari_mesaji, None)
                    if mesaj:
                        genel_uyari_mesajlari[uyari_mesaji] = mesaj.data

                # proje_turu_formu içerisindeki veri ProjeTuru modeli fieldlarına göre filtrelenir.
                # Sadece eşleşen fieldlardan oluşmuş bir dict elde edilir
                proje_turu_data = ProjeTuru.data_to_dict(proje_turu_formu.data)
                # proje_turu modelinden instance oluşturulur.
                proje_turu = ProjeTuru(guncel_mi=True,
                                       tur_kodu=tur_kodu,
                                       **proje_turu_data)
                proje_turu.genel_uyari_mesajlari = genel_uyari_mesajlari
                DB.session.add(proje_turu)
                DB.session.flush()
            except ZopseduModelValueError as exc:
                form_field = getattr(proje_turu_formu, exc.field_name, None)
                form_field.errors.append(str(exc))
                DB.session.rollback()
                return render_template("proje_turu/proje_turu.html",
                                       proje_turu_formu=proje_turu_formu,
                                       basvuru_yapilmis_mi=False,
                                       guncel_mi=True)

            try:
                # proje_turu_formu içerisindeki veri Butce modeli fieldlarına göre filtrelenir.
                # Sadece eşleşen fieldlardan oluşmuş bir dict elde edilir
                butce_data = proje_turu_formu.butce_ayarlari.data
                butce = Butce(proje_turu_id=proje_turu.id,
                              **butce_data)
                DB.session.add(butce)
                DB.session.flush()
                if proje_turu.butce_tercihi == ButceTercihleri.proje_yurutucusu_onersin.name:
                    butce_kalemleri_alt_limit = 0
                    butce_kalemleri_ust_limit = 0
                    for butce_kalemi in proje_turu_formu.butce_kalemleri:
                        if butce_kalemi.secili_mi.data:
                            if butce_kalemi.butce_ust_limiti.data > butce.butce_ust_limiti:
                                hata_mesaji = "{} değeri üst limiti bütçe üst limitinden büyük olamaz".format(
                                    butce_kalemi.butce_kalemi_adi.data)
                                proje_turu_formu.errors.update(
                                    {proje_turu_formu.butce_ayarlari.form.butce_ust_limiti.name: hata_mesaji})
                                butce_kalemi.butce_ust_limiti.errors.append(hata_mesaji)
                            butce_kalemleri_alt_limit += butce_kalemi.butce_alt_limiti.data
                            butce_kalemleri_ust_limit += butce_kalemi.butce_ust_limiti.data
                            butce_kalemi_obj = ButceKalemi(
                                proje_turu_id=proje_turu.id,
                                gider_siniflandirma_id=butce_kalemi.gider_siniflandirma_id.data,
                                butce_alt_limiti=butce_kalemi.butce_alt_limiti.data,
                                butce_ust_limiti=butce_kalemi.butce_ust_limiti.data
                            )
                            DB.session.add(butce_kalemi_obj)
            except ZopseduModelValueError as exc:
                form_field = getattr(proje_turu_formu, exc.field_name, None)
                form_field.errors.append(str(exc))

            try:
                # proje_turu_formu içerisindeki veri PersonelAyarlari modeli fieldlarına göre
                # filtrelenir. Sadece eşleşen fieldlardan oluşmuş bir dict elde edilir
                personel_ayarlari_data = proje_turu_formu.personel_ayarlari.data
                personel_ayarlari = PersonelAyarlari(proje_turu_id=proje_turu.id,
                                                     **personel_ayarlari_data)
                DB.session.add(personel_ayarlari)
            except ZopseduModelValueError as exc:
                form_field = getattr(proje_turu_formu, exc.field_name, None)
                form_field.errors.append(str(exc))

            try:
                self.proje_turu_cikti_olustur(proje_turu.id, proje_turu_formu.ciktilar)
            except ZopseduModelValueError as exc:
                form_field = getattr(proje_turu_formu, exc.field_name, None)
                form_field.errors.append(str(exc))

            try:
                self.proje_turu_ek_dosya_olustur(proje_turu.id, proje_turu_formu.ek_dosyalar)

            except ZopseduModelValueError as exc:
                form_field = getattr(proje_turu_formu, exc.field_name, None)
                form_field.errors.append(str(exc))

            if proje_turu_formu.errors:
                DB.session.rollback()
                hata_listesi = set()

                form_errors_dict_to_set(proje_turu_formu.errors, hata_listesi)

                return render_template("proje_turu/proje_turu.html",
                                       proje_turu_formu=proje_turu_formu,
                                       guncel_mi=True,
                                       proje_turu_id=versiyonlanacak_proje_turu_id if versiyonlanacak_proje_turu_id else None,
                                       basvuru_yapilmis_mi=False,
                                       hata_mesajlari=hata_listesi)
            # Bütün işlemler başarılı bir şekilde gerçekleşirse eski versiyon proje türünün
            # güncel_mi field ı false yapılır.
            if eski_proje_turu:
                eski_proje_turu.guncel_mi = False
                eski_proje_turu.basvuru_aktif_mi = False

            DB.session.commit()

            if versiyonlanacak_proje_turu_id:
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_turu_versiyonla").type_index,
                    "nesne": 'Proje Turu',
                    "nesne_id": proje_turu.id,
                    "ekstra_mesaj": "{} adli user, {} id'li proje türünü versiyonladi.".format(
                        current_user.username,
                        versiyonlanacak_proje_turu_id)
                }
                signal_sender(**signal_payload)
            else:
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_turu_olusturuldu").type_index,
                    "nesne": 'Proje Turu',
                    "nesne_id": proje_turu.id,
                    "ekstra_mesaj": "{} adli user, {} kategorili, {} isimli yeni proje türü "
                                    "olusturdu.".format(current_user.username,
                                                        proje_turu.kategori,
                                                        proje_turu.ad)
                }
                signal_sender(**signal_payload)

        except IntegrityError as exc:
            CustomErrorHandler.error_handler(hata="Bir hata oluştur. Hata: {}".format(exc))
            DB.session.rollback()
            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=proje_turu_formu,
                                   errors="Beklenmedik hata")  # todo: cem, handle in template

        flash(_("İşleminiz başarıyla gerçekleştirildi."))
        return redirect(url_for('proje.ProjeTuruView:proje_turu_listele'))

    @staticmethod
    def proje_turu_ek_dosya_olustur(proje_turu_id, form_ek_dosyalar):
        """
        Form_ek_dosyalar argumanındaki verilerden ek_dosyalar modelinden instance oluşturur.
        proje_turu_id aracılıgıyla proje türü modeliyle relation kurulur.
        Args:
            proje_turu_id(Int): ilişkilendirilecek proje türünün id si
            form_ek_dosyalar(Form): verilerin bulunduğu formun ek dosyalar bölümü

        Returns:

        """
        for ek_dosya in form_ek_dosyalar:
            request_file = request.files.get(ek_dosya.belge.file_id.name, None)
            if request_file:
                file = File(content=request_file, user_id=current_user.id)
                DB.session.add(file)
                DB.session.flush()
                bap_belge = BAPBelge(adi=ek_dosya.belge.adi.data,
                                     file_id=file.id,
                                     aciklama=ek_dosya.belge.adi.data)
                DB.session.add(bap_belge)
                DB.session.flush()
                ek_dosya_obj = EkDosya(
                    proje_turu_id=proje_turu_id,
                    dosya_id=bap_belge.id,
                    zorunlu_mu=ek_dosya.zorunlu_mu.data,
                    proje_icerik_dosyasi_mi=ek_dosya.proje_icerik_dosyasi_mi.data,
                    belgenin_ciktisi_alinacak_mi=ek_dosya.belgenin_ciktisi_alinacak_mi.data
                )
                DB.session.add(ek_dosya_obj)

    @staticmethod
    def proje_turu_cikti_olustur(proje_turu_id, form_ciktilar):
        """
        form_ciktilar argumanındaki verilerden cikti modelinden instance oluşturur.
        proje_turu_id aracılıgıyla proje türü modeliyle relation kurulur.
        Args:
            proje_turu_id(Int): ilişkilendirilecek proje türünün id si
            form_ciktilar: formun cıktılar bölümü

        Returns:

        """
        for cikti in form_ciktilar:
            cikti_obj = Cikti(proje_turu_id=proje_turu_id,
                              adi=cikti.adi.data,
                              sablon_id=cikti.cikti_sablonu_id.data,
                              gorunurluk=cikti.gorunurluk.data,
                              belge_ciktisi_alinacak_mi=cikti.belge_ciktisi_alinacak_mi.data)
            DB.session.add(cikti_obj)
