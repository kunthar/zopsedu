"""Proje view classları"""
from datetime import date
from decimal import *

from flask import render_template, request, redirect, flash, url_for, get_flashed_messages, abort
from flask_classful import FlaskView, route
from flask_babel import gettext as _
from flask_login import login_required, current_user
from flask_allows import And
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.helpers import form_errors_dict_to_set
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.proje_state_dispatcher import ProjeStateDispacther
from zopsedu.models import ProjeTuru, ProjeDestekleyenKurulus, Person
from zopsedu.models import Proje, ProjeCalisanlari
from zopsedu.auth.lib import auth, Permission
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.proje.views.basvuru.common import proje_turu_to_dict, \
    get_proje_turu_with_related_field, basvuru_formu_restriction, proje_ek_dosyalar_kaydet, \
    proje_diger_dosya_kaydet, butce_kaydet, get_proje_data, month_year_to_day
from zopsedu.bap.proje.views.basvuru.common import yurutucu_kaydet
from zopsedu.bap.lib.auth import TamamlanmamisProjeBasvurusu, ProjeYurutucusu
from zopsedu.bap.models.helpers import YardimciArastirmaciSecenekleri
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel
from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids


class ProjeBasvuruView(FlaskView):
    """Proje başvurusu view classı"""

    excluded_methods = ["basvuru_formu_restriction",
                        "proje_diger_dosya_kaydet",
                        "proje_ek_dosyalar_kaydet",
                        "yurutucu_kaydet",
                        "butce_kaydet"]

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
                   menu_registry={"path": ".bap.yeni_basvuru",
                                  "title": _("Proje Başvuru"), "order": 0})
    @route('/yeni-basvuru', methods=['GET'])
    def basvuru_icin_proje_turu_sec():
        """Proje başvurusu yapabilmek için başvuracağımız proje türünü seçmek için kullanırız"""
        proje_turleri = DB.session.query(ProjeTuru).filter_by(basvuru_aktif_mi=True,
                                                              guncel_mi=True).order_by(
            desc(ProjeTuru.updated_at)).all()
        return render_template('arastirma_projesi_basvuru/proje_basvuru_sec.html',
                               proje_turleri=proje_turleri)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]))
    @route('/yeni-basvuru/tur/<int:tur_id>', methods=['GET'], endpoint='proje_yeni_basvuru')
    def yeni_basvuru(tur_id):
        """Yeni proje başvurusu formları"""
        user_id = current_user.id
        try:
            p_tur = DB.session.query(ProjeTuru).filter_by(id=tur_id,
                                                          basvuru_aktif_mi=True,
                                                          guncel_mi=True).one()
        except NoResultFound as exc:
            CustomErrorHandler.error_handler(
                hata="Güncel olmayan veya var olmayan bir proje türü ile proje "
                     "basvurusu yapılmaya çalışıldı. Hata: {}, User id: {}, "
                     "Proje turu id: {}".format(exc, user_id, tur_id)
            )
            return abort(404)

        proje_tur_dict = proje_turu_to_dict(p_tur)

        # basvuruyu yapan ogretim elamanininin id sini getirir
        ogretim_elemani = DB.session.query(OgretimElemani.id.label("ogretim_elemani_id")).join(
            Personel,
            OgretimElemani.personel_id == Personel.id
        ).join(
            Person, Personel.person_id == Person.id
        ).filter(Person.user_id == current_user.id).one()
        yurutucu_id = ogretim_elemani.ogretim_elemani_id

        yeni_basvuru_formu = basvuru_formu_restriction(proje_tur_dict)
        yeni_basvuru_formu.proje_personeli.yurutucu.yurutucu_id.data = yurutucu_id

        yeni_proje = Proje(proje_turu=p_tur.id,
                           proje_turu_numarasi=p_tur.tur_kodu,
                           yurutucu=yurutucu_id,
                           user_id=user_id)
        DB.session.add(yeni_proje)
        DB.session.flush()
        proje_no = "{}{}".format(date.today().year, yeni_proje.id)
        yeni_proje.proje_no = proje_no
        # proje_basvuru_durumu=ProjeBasvuruDurumu.taslak
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get("proje_basvuru_basla").type_index,
            "nesne": 'Proje',
            "nesne_id": yeni_proje.id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} kategorisine proje başvuru islemine "
                            "basladi.".format(current_user.username, p_tur.kategori)
        }
        signal_sender(**signal_payload)
        # yeni_basvuru_formu.proje_id.data = yeni_proje.id

        return render_template(
            'arastirma_projesi_basvuru/arastirma_proje_basvurusu.html',
            yeni_basvuru_formu=yeni_basvuru_formu,
            proje_tur_dict=proje_tur_dict,
            proje_id=yeni_proje.id,
            revizyon_bekleniyor_mu=False,
            uyari_mesajlari=proje_tur_dict.get("genel_uyari_mesajlari", None)
        )

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/proje/<int:proje_id>/kaydet', methods=['POST'], endpoint='yeni_proje_kaydet')
    def proje_kaydet(proje_id):
        """
        Proje başvurusunun taslak olarak kaydedilmedi kaydedilen taslağın güncellenmesi ve
        başvurunun tamamlanıp sonuçlandırılması işini yapar
        """
        taslak_mi = request.args.get("taslak_mi", False)
        user_id = current_user.id
        form_data = request.form

        proje_turu_id = form_data.get("proje_turu")
        try:
            proje_turu = get_proje_turu_with_related_field(proje_turu_id)
        except NoResultFound as exc:
            CustomErrorHandler.error_handler(
                hata="Güncel olmayan veya var olmayan bir proje türü id si ile "
                     "başvuru yapılmaya çalışıldı. Hata: {}, User id: {}, "
                     "Proje Turu id: {}".format(exc, user_id, proje_turu_id))
            return abort(404)

        proje_tur_dict = proje_turu_to_dict(proje_turu)

        proje_formu = basvuru_formu_restriction(initial_form_data=form_data,
                                                proje_turu_dict=proje_tur_dict)
        proje = DB.session.query(Proje).filter_by(id=proje_id).one()
        revizyon_bekleniyor_mu = True if proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor else False

        if not taslak_mi and not proje_formu.validate():
            hata_listesi = set()

            form_errors_dict_to_set(proje_formu.errors, hata_listesi)
            proje_formu.proje_personeli.yurutucu.yurutucu_id.data = proje.yurutucu
            return render_template(
                'arastirma_projesi_basvuru/arastirma_proje_basvurusu.html',
                yeni_basvuru_formu=proje_formu,
                proje_tur_dict=proje_turu.to_dict(),
                proje_id=proje_id,
                proje_hakem_onerileri=proje.proje_hakem_onerileri,
                proje_calisanlari=[calisan for calisan in proje.proje_calisanlari if
                                   not (proje.yurutucu and proje.yurutucu == calisan.personel_id)],
                taslak_mi=taslak_mi,
                revizyon_bekleniyor_mu=revizyon_bekleniyor_mu,
                hata_mesajlari=hata_listesi
            )
        try:
            form_genel = proje_formu.genel_bilgiler
            proje.update_obj_data(form_genel.genel_bilgiler.data)
            proje.update_obj_data(form_genel.fakulte.data)
            proje.update_obj_data(form_genel.ozet_bilgiler.data)
            proje.onaylayan_yetkili_id = form_genel.onaylayan_yetkili.onaylayan_yetkili_id.data
            proje.onay_tarihi = form_genel.onaylayan_yetkili.onay_tarihi.data

            toplam_katki = Decimal(0)

            # yürütücü kaydeder
            # yurutucu calisan olarak kaydedilmis ise gerekli veriyi getirir
            yurutucu_calisan = DB.session.query(ProjeCalisanlari).filter_by(
                proje_id=proje_id,
                personel_id=proje.proje_yurutucu.personel_id).first()
            if not yurutucu_calisan:
                yurutucu_kaydet(proje_id,
                                proje_tur_dict,
                                proje_formu.proje_personeli.yurutucu,
                                proje.yurutucu,
                                taslak_mi)
            else:
                yurutucu = DB.session.query(ProjeCalisanlari).filter_by(
                    proje_id=proje_id,
                    personel_id=proje.proje_yurutucu.personel_id).first()
                yurutucu.update_obj_data(proje_formu.proje_personeli.yurutucu.data)

            # destekleyen kuruluş kaydeder
            if proje.proje_destekleyen_kurulus:

                proje.proje_destekleyen_kurulus.update_obj_data(
                    form_genel.destekleyen_kurulus.data
                )
            else:
                proje_destekleyen_kurulus = ProjeDestekleyenKurulus(
                    proje_id=proje.id,
                    **form_genel.destekleyen_kurulus.data
                )
                DB.session.add(proje_destekleyen_kurulus)

            # proje formu diger alanlarını kaydeder
            if proje_formu.diger:
                # proje basvurusu için ek dosyalari kaydeder
                proje_ek_dosyalar_kaydet(
                    user_id,
                    proje_id,
                    proje_formu.diger.ek_dosyalar,
                    proje.proje_belgeleri,
                    taslak_mi
                )

                # proje basvurusu için diğer dosyaları kaydeder
                var_olan_dosyalar = []
                if proje_formu.diger.proje_diger:
                    var_olan_dosyalar = proje_diger_dosya_kaydet(
                        user_id,
                        proje_id,
                        proje_formu.diger.proje_diger,
                        proje.proje_belgeleri)

                for dosya in proje.proje_belgeleri:
                    if dosya.id not in var_olan_dosyalar and not dosya.proje_turu_ek_dosya_id:
                        DB.session.delete(dosya)
            # proje basvurusu butce alanlarini kaydeder
            for proje_kalemi in proje.proje_kalemleri:
                DB.session.delete(proje_kalemi)
            DB.session.flush()
            onerilen_proje_butcesi, butce_hatalari = butce_kaydet(proje_id, proje_formu.butce.data)
            proje.teklif_edilen_butce = onerilen_proje_butcesi

            # proje başvurusu tamamlanmaya çalışılıyorsa gerekli kontroller yapılır
            if not taslak_mi:
                # proje turunden gelen proje sure alt ve ust limitleri
                sure_alt_limiti = proje_tur_dict.get("sure_alt_limiti")
                sure_ust_limiti = proje_tur_dict.get("sure_ust_limiti")
                sure_birimi = proje_tur_dict.get("sure_birimi")

                # karsilastirma yapabilmek icin teklif edilen, sure alt limitini ve sure ust
                # limitini gun cinsine ceviriyoruz
                min_sure = month_year_to_day(sure_alt_limiti,
                                             sure_birimi)
                max_sure = month_year_to_day(sure_ust_limiti,
                                             sure_birimi)
                teklif_edilen_proje_suresi = month_year_to_day(
                    proje_formu.genel_bilgiler.genel_bilgiler.proje_suresi.data,
                    proje_formu.genel_bilgiler.genel_bilgiler.proje_suresi_birimi.data)

                if teklif_edilen_proje_suresi < min_sure or teklif_edilen_proje_suresi > max_sure:
                    flash(_("Proje süreniz {} ile {} {} arasında olabilir".format(
                        sure_alt_limiti,
                        sure_ust_limiti,
                        sure_birimi)), "error")

                if proje.teklif_edilen_butce:
                    if proje_turu.butce.butce_alt_limiti > proje.teklif_edilen_butce:
                        flash(_("Proje bütçeniz en az {} TL olabilir".format(
                            proje_turu.butce.butce_alt_limiti)),
                            "error")
                    elif proje_turu.butce.butce_ust_limiti < proje.teklif_edilen_butce:
                        flash(_("Proje bütçeniz en fazla {} TL olabilir".format(
                            proje_turu.butce.butce_ust_limiti)),
                            "error")

                for calisan in proje.proje_calisanlari:
                    toplam_katki += Decimal(
                        calisan.projeye_katkisi) if calisan.projeye_katkisi else Decimal(0)
                    if proje_tur_dict.get("ozgecmis_yuklenmesi_zorunlu_mu"):
                        if calisan.ozgecmis.file_id is None and not calisan.ozgecmis.tecrube:
                            flash(_("Proje personeli İçin Özgeçmiş Yüklemeniz Zorunludur"), "error")
                            break
                    zorunlu_banka_bilgileri = proje_tur_dict.get(
                        "banka_bilgilerini_girmek_zorunlu_mu")
                    if zorunlu_banka_bilgileri and not calisan.banka_bilgisi:
                        flash(_("Proje personeli İçin Banka Bilgileri Girilmesi Zorunludur"),
                              "error")
                        break

                if proje_tur_dict.get("hakem_onerilsin_mi", None):
                    basvuru_hakem_oneri_sayisi = proje_tur_dict.get("basvuru_hakem_oneri_sayisi", 0)
                    if len(proje.proje_hakem_onerileri) < basvuru_hakem_oneri_sayisi:
                        flash(_("Projenizin değerlendirmeye alınabilmesi için en az {} adet hakem "
                                "önerisinde bulunmanız gerekmektedir"
                                ".").format(basvuru_hakem_oneri_sayisi), "error")

                if toplam_katki > 100:
                    flash(_("Personellerin toplam katkı değerleri en fazla 100 olabilir."), "error")
                form_personel = proje_turu.personel_ayarlari
                # projede bulunan personel sayisindan yurutucuyu cikarinca
                # projeye eklenen personel sayisi bulunur
                calisan_sayisi = len(proje.proje_calisanlari) - 1
                if form_personel.yardimci_arastirmaci_secenekleri == \
                        YardimciArastirmaciSecenekleri.sinirli:
                    if form_personel.yardimci_arastirmaci_alt_limiti > calisan_sayisi:
                        flash(_("{} personel eklediniz. En az {} personel eklemelisiniz.").format(
                            calisan_sayisi,
                            form_personel.yardimci_arastirmaci_alt_limiti), "error")
                    elif form_personel.yardimci_arastirmaci_ust_limiti < calisan_sayisi:
                        flash(_(
                            "{} personel eklediniz. En fazla {} personel ekleyebilirsiniz.").format(
                            calisan_sayisi,
                            form_personel.yardimci_arastirmaci_ust_limiti), "error")
                for butce_hata in butce_hatalari:
                    flash(butce_hata, "error")

                if get_flashed_messages(category_filter=["error"]):
                    DB.session.rollback()
                    proje_formu.proje_personeli.yurutucu.yurutucu_id.data = proje.yurutucu
                    return render_template(
                        'arastirma_projesi_basvuru/arastirma_proje_basvurusu.html',
                        yeni_basvuru_formu=proje_formu,
                        proje_tur_dict=proje_tur_dict,
                        proje_id=proje_id,
                        proje_hakem_onerileri=proje.proje_hakem_onerileri,
                        proje_calisanlari=[calisan for calisan in proje.proje_calisanlari if not (
                                proje.yurutucu and proje.yurutucu == calisan.personel_id)],
                        taslak_mi=taslak_mi,
                        revizyon_bekleniyor_mu=revizyon_bekleniyor_mu,
                        hata_mesajlari=get_flashed_messages(category_filter=["error"])
                    )

            if taslak_mi:
                proje.proje_basvuru_durumu = ProjeBasvuruDurumu.taslak
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_basvuru_guncelle").type_index,
                    "nesne": 'Proje',
                    "nesne_id": proje_id,
                    "ekstra_mesaj": "{} adlı kullanıcı, proje başvurusunu güncelledi.".format(
                        current_user.username)
                }
                signal_sender(**signal_payload)
                return redirect(
                    url_for('proje.proje_yeni_basvuru_taslak_with_id', proje_id=proje.id))

            # todo: revizyon tamamlaninca admine mesaj !!!
            proje.proje_basvuru_durumu = ProjeBasvuruDurumu.tamamlandi

            if not revizyon_bekleniyor_mu:
                proje.gelir_kasasi_id = proje_tur_dict.get("gelir_kasasi_id", None)
                proje.teklif_edilen_baslama_tarihi = date.today()
                ProjeStateDispacther.project_init(params={"proje_id": proje_id},
                                             triggered_by=current_user.id,
                                             proje_id=proje_id)
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_basvuru_tamamla").type_index,
                    "nesne": 'Proje',
                    "nesne_id": proje_id,
                    "ekstra_mesaj": "{} adlı kullanıcı, proje başvurusunu tamamladi.".format(
                        current_user.username)
                }

                signal_sender(**signal_payload)
            else:
                revizyon_signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                        "proje_basvuru_tamamla").type_index,
                    "nesne": 'Proje',
                    "nesne_id": proje_id,
                    "ekstra_mesaj": "{} adlı kullanıcı, projesinin revizyonunu tamamladi.".format(
                        current_user.username)
                }

                signal_sender(**revizyon_signal_payload)

                for bap_admin in bap_yetkili_and_admin_ids():
                    payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "proje_islem").type_index,
                        "ekstra_mesaj": "{} id li projenin revizyon işlemi tamamlandı".format(
                            proje.id),
                        "notification_receiver": bap_admin.person_id,
                        "notification_title": _("Proje revize edildi"),
                        "notification_message": "{} numaralı projenin revizyon işlemi proje yürütücüsü"
                                                " tarafından tamamlandı.".format(proje.proje_no),
                        "proje_id": proje.id
                    }

                    signal_sender(log=False, notification=True, **payload)

            DB.session.commit()
            return redirect(url_for('proje.proje_dashboard', proje_id=proje.id))
        except IntegrityError as exc:
            CustomErrorHandler.error_handler(
                hata="Bir hata meydana geldi. Hata: {}".format(exc)
            )
            DB.session.rollback()
            proje_formu.proje_personeli.yurutucu.yurutucu_id.data = proje.yurutucu
            return render_template(
                'arastirma_projesi_basvuru/arastirma_proje_basvurusu.html',
                yeni_basvuru_formu=proje_formu,
                proje_tur_dict=proje_turu.to_dict(),
                proje_id=proje_id,
                proje_hakem_onerileri=proje.proje_hakem_onerileri,
                proje_calisanlari=[calisan for calisan in proje.proje_calisanlari if
                                   not (proje.yurutucu and proje.yurutucu == calisan.personel_id)],
                revizyon_bekleniyor_mu=revizyon_bekleniyor_mu,
                taslak_mi=taslak_mi
            )

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            And(TamamlanmamisProjeBasvurusu(), ProjeYurutucusu())))
    @route('/yeni-basvuru/taslak/<int:proje_id>', methods=['GET'],
           endpoint='proje_yeni_basvuru_taslak_with_id')
    # pylint: disable=too-many-locals
    def get_proje_taslak_with_id(proje_id):
        """Id'si verilen kaydedilmiş taslak projeyi getirir"""
        user_id = current_user.id
        try:
            proje = DB.session.query(Proje).filter_by(
                id=proje_id,
                proje_basvuru_durumu=ProjeBasvuruDurumu.taslak).one()

        except NoResultFound as exc:
            CustomErrorHandler.error_handler(
                hata="Basvuru durumu taslak olmayan veya var olmayan bir proje ile "
                     "proje basvurusu taslağına ulaşılmaya calışıldı. Hata: {}, "
                     "User id: {}, Proje id: {}".format(exc, user_id, proje_id))
            return abort(404)
        proje_turu = get_proje_turu_with_related_field(proje.proje_turu)
        if not proje_turu:
            #  todo: current app logger customerror handlera cevrilecek
            CustomErrorHandler.error_handler(
                hata="Güncel olmayan bir proje türünün kayıtlı taslagına ulaşılmaya"
                     " çalışıldı. User id: {}, Proje id: {}".format(user_id, proje_id))
            flash("Taslak kaydı yaptığınız projenin başvuru koşulları BAP birimi tarafından "
                  "güncellenmiştir. Lütfen güncel proje türü üzerinden tekrar başvurunuzu "
                  "gerçekleştiriniz.")
            return redirect(url_for("proje.ProjeBasvuruView:basvuru_icin_proje_turu_sec"))
        proje_turu_dict = proje_turu_to_dict(proje_turu)
        yurutucu_calisan_id = None

        yurutucu_calisan = DB.session.query(ProjeCalisanlari).filter_by(
            proje_id=proje_id,
            personel_id=proje.yurutucu).first()
        if yurutucu_calisan:
            yurutucu_calisan_id = yurutucu_calisan.id

        form_data = get_proje_data(proje_turu_dict, proje)

        proje_formu = basvuru_formu_restriction(proje_turu_dict=proje_turu_dict, **form_data)
        return render_template(
            'arastirma_projesi_basvuru/arastirma_proje_basvurusu.html',
            yeni_basvuru_formu=proje_formu,
            proje_tur_dict=proje_turu.to_dict(),
            proje_id=proje_id,
            proje_hakem_onerileri=proje.proje_hakem_onerileri,
            proje_calisanlari=[calisan for calisan in proje.proje_calisanlari if
                               not (proje.yurutucu and proje.yurutucu == calisan.personel_id)],
            yurutucu_calisan_id=yurutucu_calisan_id,
            taslak_mi=True,
            revizyon_bekleniyor_mu=False,
            uyari_mesajlari=proje_turu_dict.get("genel_uyari_mesajlari", None)
        )
