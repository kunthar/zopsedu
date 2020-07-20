"""Proje Türü View Metotları"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-nested-blocks

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from flask import render_template, request, redirect, flash, url_for
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required, current_user

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.helpers import form_errors_dict_to_set
from zopsedu.bap.models.proje_turu import ZopseduModelValueError
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import ProjeTuru, BAPBelge, Cikti, EkDosya, ButceKalemi, File, Proje
from zopsedu.bap.models.helpers import PROJE_TURU_UYARI_MESAJ_TIPLERI, ButceTercihleri
from zopsedu.bap.proje.forms.proje_turu.proje_turu import ProjeTuruFormu
from zopsedu.auth.lib import auth, Permission
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class ProjeTuruGuncelleView(FlaskView):
    """Proje Türü View"""

    excluded_methods = ["proje_turu_ek_dosya_olustur",
                        "proje_turu_cikti_olustur",
                        "init_proje_turu_form",
                        "get_forms_with_type"]

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["proje_turu"]["proje_turu_yaratma_formu_goruntuleme"]))
    @route('/<int:proje_turu_id>/guncelle',
           methods=["POST"],
           endpoint='proje_turu_guncelle_with_id')
    def proje_turu_guncelle(self, proje_turu_id):
        """
        Proje türünü güncellemek için kullanılacak method
        Args:
            proje_turu_id: güncellenecek proje tünün id si

        Returns:

        """
        proje = DB.session.query(Proje.proje_turu).filter(Proje.proje_turu == proje_turu_id).all()
        proje_turu_formu = ProjeTuruFormu(request.form)
        try:
            proje_turu = DB.session.query(ProjeTuru).options(
                joinedload(ProjeTuru.butce),
                joinedload(ProjeTuru.cikti),
                joinedload(ProjeTuru.personel_ayarlari),
                joinedload(ProjeTuru.ek_dosyalar),
            ).filter_by(id=proje_turu_id, guncel_mi=True).one()
        except NoResultFound:
            return redirect(url_for('.proje_turu'))

        if proje:
            flash(
                "Proje türüne proje başvurusu yapılmış. Bu yüzden proje türünü güncelleyemezsiniz.",
                "error")
            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=proje_turu_formu,
                                   proje_turu_id=proje_turu_id,
                                   guncel_mi=proje_turu.guncel_mi,
                                   basvuru_yapilmis_mi=True)

        if not proje_turu_formu.validate():
            hata_listesi = set()

            form_errors_dict_to_set(proje_turu_formu.errors, hata_listesi)

            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=proje_turu_formu,
                                   proje_turu_id=proje_turu_id,
                                   guncel_mi=proje_turu.guncel_mi,
                                   basvuru_yapilmis_mi=False,
                                   hata_mesajlari=hata_listesi)

        if proje_turu.ad != proje_turu_formu.ad.data and DB.session.query(ProjeTuru).filter(
                ProjeTuru.ad == proje_turu_formu.ad.data and
                ProjeTuru.tur_kodu != proje_turu.tur_kodu).scalar():
            proje_turu_formu.ad.errors.append(
                _("Proje Türü Adı Kullanılmaktadır. Lütfen Başka Bir Ad ile Tekrar Deneyiniz"))

            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=proje_turu_formu,
                                   proje_turu_id=proje_turu_id,
                                   guncel_mi=proje_turu.guncel_mi,
                                   basvuru_yapilmis_mi=False)

        try:
            proje_turu.update_obj_data(proje_turu_formu.data)
        except ZopseduModelValueError as exc:
            form_field = getattr(proje_turu_formu, exc.field_name, None)
            form_field.errors.append(str(exc))

        genel_uyari_mesajlari = {}
        for uyari_mesaji in PROJE_TURU_UYARI_MESAJ_TIPLERI:
            mesaj = getattr(proje_turu_formu, uyari_mesaji, None)
            if mesaj:
                genel_uyari_mesajlari[uyari_mesaji] = mesaj.data
        proje_turu.genel_uyari_mesajlari = genel_uyari_mesajlari

        try:
            proje_turu.personel_ayarlari.update_obj_data(proje_turu_formu.personel_ayarlari.data)
        except ZopseduModelValueError as exc:
            form_field = getattr(proje_turu_formu, exc.field_name, None)
            form_field.errors.append(str(exc))

        try:
            proje_turu.butce.update_obj_data(proje_turu_formu.butce_ayarlari.data)

            var_olan_butce_kalemleri = []
            if proje_turu.butce_tercihi == ButceTercihleri.proje_yurutucusu_onersin.name:
                butce_kalemleri_alt_limit = 0
                butce_kalemleri_ust_limit = 0
                for butce_kalemi in proje_turu_formu.butce_kalemleri:
                    butce_kalemleri_alt_limit += butce_kalemi.butce_alt_limiti.data
                    butce_kalemleri_ust_limit += butce_kalemi.butce_ust_limiti.data
                    if butce_kalemi.secili_mi.data:
                        if butce_kalemi.butce_ust_limiti.data > proje_turu.butce.butce_ust_limiti:
                            hata_mesaji = "{} değeri üst limiti bütçe üst limitinden büyük olamaz".format(
                                butce_kalemi.butce_kalemi_adi.data)
                            proje_turu_formu.errors.update(
                                {proje_turu_formu.butce_ayarlari.form.butce_ust_limiti.name: hata_mesaji})
                            butce_kalemi.butce_ust_limiti.errors.append(hata_mesaji)
                        for kayitli_kalem in proje_turu.butce_kalemleri:
                            if kayitli_kalem.gider_siniflandirma_id == \
                                    butce_kalemi.gider_siniflandirma_id.data:
                                kayitli_kalem.update_obj_data(butce_kalemi.data)
                                var_olan_butce_kalemleri.append(kayitli_kalem.gider_siniflandirma_id)
                                break
                        else:
                            yeni_kalem = ButceKalemi(
                                proje_turu_id=proje_turu.id,
                                gider_siniflandirma_id=butce_kalemi.gider_siniflandirma_id.data,
                                butce_alt_limiti=butce_kalemi.butce_alt_limiti.data,
                                butce_ust_limiti=butce_kalemi.butce_ust_limiti.data)
                            DB.session.add(yeni_kalem)
                            DB.session.flush()
                            var_olan_butce_kalemleri.append(yeni_kalem.gider_siniflandirma_id)
                for butce_kalemi in proje_turu.butce_kalemleri:
                    if butce_kalemi.gider_siniflandirma_id not in var_olan_butce_kalemleri:
                        DB.session.delete(butce_kalemi)
            elif proje_turu.butce_tercihi == ButceTercihleri.butce_ile_ilgili_islem_yapmasin.name:
                for butce_kalemi in proje_turu.butce_kalemleri:
                    DB.session.delete(butce_kalemi)

        except ZopseduModelValueError as exc:
            form_field = getattr(proje_turu_formu, exc.field_name, None)
            form_field.errors.append(str(exc))

        try:
            var_olan_ciktilar = []
            for cikti in proje_turu_formu.ciktilar:
                if cikti.cikti_id.data:
                    for kayitli_cikti in proje_turu.cikti:
                        if cikti.cikti_id.data == kayitli_cikti.id:
                            var_olan_ciktilar.append(kayitli_cikti.id)
                            kayitli_cikti.adi = cikti.adi.data
                            kayitli_cikti.cikti_sablonu_id = cikti.cikti_sablonu_id.data
                            kayitli_cikti.gorunurluk = cikti.gorunurluk.data
                            kayitli_cikti.belge_ciktisi_alinacak_mi = cikti. \
                                belge_ciktisi_alinacak_mi.data
                else:
                    cikti_obj = Cikti(
                        proje_turu_id=proje_turu_id,
                        adi=cikti.adi.data,
                        sablon_id=cikti.cikti_sablonu_id.data,
                        gorunurluk=cikti.gorunurluk.data,
                        belge_ciktisi_alinacak_mi=cikti.belge_ciktisi_alinacak_mi.data)
                    DB.session.add(cikti_obj)
                    DB.session.flush()
                    var_olan_ciktilar.append(cikti_obj.id)

            for cikti in proje_turu.cikti:
                if cikti.id not in var_olan_ciktilar:
                    DB.session.delete(cikti)

        except ZopseduModelValueError as exc:
            form_field = getattr(proje_turu_formu, exc.field_name, None)
            form_field.errors.append(str(exc))

        try:
            var_olan_dosyalar = []
            for ek_dosya in proje_turu_formu.ek_dosyalar:
                if ek_dosya.ek_dosya_id.data:
                    for kayitli_ek_dosya in proje_turu.ek_dosyalar:
                        if ek_dosya.ek_dosya_id.data == kayitli_ek_dosya.id:
                            var_olan_dosyalar.append(kayitli_ek_dosya.id)
                            request_file = request.files.get(ek_dosya.belge.file_id.name, None)
                            if request_file:
                                file = File(content=request_file, user_id=current_user.id)
                                DB.session.add(file)
                                DB.session.flush()
                                kayitli_ek_dosya.belge.file_id = file.id

                            kayitli_ek_dosya.belge.adi = ek_dosya.belge.adi.data
                            kayitli_ek_dosya.belge.aciklama = ek_dosya.belge.aciklama.data
                            kayitli_ek_dosya.zorunlu_mu = ek_dosya.zorunlu_mu.data
                            kayitli_ek_dosya.proje_icerik_dosyasi_mi = ek_dosya. \
                                proje_icerik_dosyasi_mi.data
                            kayitli_ek_dosya.belgenin_ciktisi_alinacak_mi = ek_dosya. \
                                belgenin_ciktisi_alinacak_mi.data
                else:
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
                        DB.session.flush()
                        var_olan_dosyalar.append(ek_dosya_obj.id)
            for ek_dosya in proje_turu.ek_dosyalar:
                if ek_dosya.id not in var_olan_dosyalar:
                    DB.session.delete(ek_dosya)

        except ZopseduModelValueError as exc:
            form_field = getattr(proje_turu_formu, exc.field_name, None)
            form_field.errors.append(str(exc))

        if proje_turu_formu.errors:

            DB.session.rollback()

            hata_listesi = set()
            form_errors_dict_to_set(proje_turu_formu.errors, hata_listesi)

            return render_template("proje_turu/proje_turu.html",
                                   proje_turu_formu=proje_turu_formu,
                                   proje_turu_id=proje_turu_id,
                                   guncel_mi=proje_turu.guncel_mi,
                                   basvuru_yapilmis_mi=False,
                                   hata_mesajlari=hata_listesi)
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("proje_turu_guncelle").type_index,
            "nesne": 'Proje Turu',
            "nesne_id": proje_turu.id,
            "ekstra_mesaj": "{} adli user, {} kategorili, {} isimli proje türünü "
                            "guncelledi.".format(current_user.username,
                                                 proje_turu.kategori,
                                                 proje_turu.ad)
        }
        signal_sender(**signal_payload)
        flash(_("İşleminiz başarıyla gerçekleştirildi."))
        return redirect(url_for('proje.ProjeTuruView:proje_turu_listele'))

