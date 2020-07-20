"""Proje Satinalma Talepleri view classları"""
from decimal import Decimal

from flask import render_template, jsonify, request, render_template_string, redirect, flash, \
    get_flashed_messages, url_for
from flask_babel import gettext as _
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import lazyload, joinedload
from werkzeug.datastructures import ImmutableMultiDict

from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import ProjeYurutucusu
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.proje.forms.satinalma.satinalma_talepleri import ProjeSatinAlmaTalepleri, \
    DuyuruForm, TeknikSartnameDuzenlemeFormu
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, \
    get_next_states_info, get_actions_info
from zopsedu.icerik.model import Icerik
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.query_helper.user_query import bap_yetkili_and_admin_ids
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import File, AppState
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeSatinalmaTalepleriView(FlaskView):
    """
    Proje Satinalma Talepleri
    """

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_satinalma_talepleri_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma-talepleri", methods=["GET"],
           endpoint="satinalma_talepleri")
    def satinalma_talepleri(self, proje_id):
        """
        Satinalma Talpeleri view class

            """

        satinalma_form = ProjeSatinAlmaTalepleri()

        proje_yurutucusu_mu = ProjeYurutucusu()
        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            joinedload(Proje.satinalma_talepleri),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.kabul_edilen_proje_hakemleri),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
        ).filter(Proje.id == proje_id, or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                                           Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)
        proje_durum = DB.session.query(AppState).filter(
            AppState.id == proje.proje_durumu_id).first()

        proje_satinalma_talepleri_data = []
        # satinalma talepleri uyari mesajlari
        sa_talepleri_uyari_mesajlari = []

        for satinalma_talebi in proje.satinalma_talepleri:
            data = {
                "satinalma_id": satinalma_talebi.id,
                "talep_numarasi": satinalma_talebi.talep_numarasi,
                "created_at": satinalma_talebi.created_at,
                "state_code": satinalma_talebi.durumu.state_code,
                "state_description": satinalma_talebi.durumu.description,
                "duyuru_id": satinalma_talebi.duyuru_id,
                "duyuru_duzenlensin_mi": satinalma_talebi.duyuru_duzenlensin_mi,
                "teknik_sartname_duzenlensin_mi": False
            }
            if satinalma_talebi.duyuru_duzenlensin_mi:
                sa_talepleri_uyari_mesajlari.append(
                    _("{} numaralı satınalma talebi için işlemler bölümünden duyuru düzenmeniz "
                      "gerekmektedir.".format(satinalma_talebi.talep_numarasi))
                )

            for talep_kalemi in satinalma_talebi.talep_kalemleri:
                if talep_kalemi.teknik_sartname_duzenlensin_mi:
                    data["teknik_sartname_duzenlensin_mi"] = True
                    sa_talepleri_uyari_mesajlari.append(
                        _("{} numaralı satınalma talebi için işlemler bölümünden teknik şartname "
                          "düzenlemeniz gerekmektedir.".format(satinalma_talebi.talep_numarasi))
                    )
                    break

            proje_satinalma_talepleri_data.append(data)

        """
        proje_kalemleri_data {
            "Mal Malzeme Alımı": {
                "satinalma_talebi_yapilabilir_mi": True,
                "butce_kalemi_id": proje_kalemi.proje_turu_butce_kalemi.id,
                "proje_kalemleri": []
            }
            "Hizmet Alımı": {
                "satinalma_talebi_yapilabilir_mi": True,
                "butce_kalemi_id": proje_kalemi.proje_turu_butce_kalemi.id,
                "proje_kalemleri": []
            }
        }
        butce_kalemi adı: projeyenin harcama yapabilecegi butce kalemlerini temsil eder
        satinalma_talebi_yapilabilir_mi degeri kullanilabilir miktari ve kullanilabilir butcesine
        gore uretilir. ilgili degerlerden biri 0 ise basvuru yapmasi engellenir.
        butce_kalemi_id projenin harcama yapabilecegi butce kaleminin id sini temsil eder
        """
        proje_kalemleri_data = {}
        for proje_kalemi in proje.proje_kalemleri:
            butce_kalemi_adi = "{} {}".format(
                proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.kodu,
                proje_kalemi.proje_turu_butce_kalemi.gider_siniflandirma_kalemi.aciklama)
            if not proje_kalemleri_data.get(butce_kalemi_adi):
                proje_kalemleri_data[butce_kalemi_adi] = {
                    "satinalma_talebi_yapilabilir_mi": False,
                    "butce_kalemi_id": proje_kalemi.proje_turu_butce_kalemi.id,
                    "proje_kalemleri": []
                }

            kullanilabilir_miktar = proje_kalemi.toplam_miktar - proje_kalemi.kullanilan_miktar - proje_kalemi.rezerv_edilen_miktar
            kullanilabilir_butce = proje_kalemi.toplam_butce - proje_kalemi.rezerv_butce - proje_kalemi.kullanilan_butce
            kullanilabilir_butce = kullanilabilir_butce.quantize(Decimal(".01"))
            proje_kalemleri_data[butce_kalemi_adi]["proje_kalemleri"].append({
                "proje_kalemi_ad": proje_kalemi.ad,
                "toplam_miktar": proje_kalemi.toplam_miktar,
                "birim": proje_kalemi.birim.value,
                "kullanilan_miktar": proje_kalemi.kullanilan_miktar,
                "rezerv_edilen_miktar": proje_kalemi.rezerv_edilen_miktar,
                "kullanilabilir_miktar": kullanilabilir_miktar,
                "toplam_butce": proje_kalemi.toplam_butce,
                "kullanilan_butce": proje_kalemi.kullanilan_butce,
                "rezerv_edilen_butce": proje_kalemi.rezerv_butce,
                "kullanilabilir_butce": kullanilabilir_butce
            })

            if kullanilabilir_miktar > 0 and kullanilabilir_butce > 0:
                proje_kalemleri_data[butce_kalemi_adi]["satinalma_talebi_yapilabilir_mi"] = True

        return render_template("dashboard/proje_satinalma_talepleri.html",
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               proje_id=proje_id,
                               next_states_info=next_states_info,
                               actions_info=actions_info,
                               proje=proje,
                               satinalma_form=satinalma_form,
                               proje_satinalma_talepleri=proje_satinalma_talepleri_data,
                               proje_kalemleri_data=proje_kalemleri_data,
                               proje_durum=proje_durum,
                               satinalma_talepleri_uyari_mesajlari=sa_talepleri_uyari_mesajlari
                               )

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_satinalma_talepleri_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma-talep/<int:butce_kalemi_id>/talep-olustur",
           methods=["GET"])
    def satinalma_talep_get(self, proje_id, butce_kalemi_id):
        """
        Satinalma Talpeleri view class

        """

        proje_kalemleri = DB.session.query(ProjeKalemi).filter(
            ProjeKalemi.proje_id == proje_id,
            ProjeKalemi.proje_turu_butce_kalem_id == butce_kalemi_id).all()

        satinalma_talep_form = ProjeSatinAlmaTalepleri()

        satinalma_talebi_yapilabilir_mi = False

        for proje_kalemi in proje_kalemleri:
            kullanilabilir_miktar = proje_kalemi.toplam_miktar - proje_kalemi.kullanilan_miktar - proje_kalemi.rezerv_edilen_miktar
            kullanilabilir_butce = proje_kalemi.toplam_butce - proje_kalemi.rezerv_butce - proje_kalemi.kullanilan_butce
            kullanilabilir_butce = kullanilabilir_butce.quantize(Decimal(".01"))

            if kullanilabilir_miktar > 0 and kullanilabilir_butce > 0:
                satinalma_talebi_yapilabilir_mi = True
                satinalma_talep_form.talepler.append_entry({
                    "proje_kalemi_id": proje_kalemi.id,
                    "proje_kalemi_adi": proje_kalemi.ad,
                    "toplam_miktar": proje_kalemi.toplam_miktar,
                    "birim": proje_kalemi.birim.value,
                    "kullanilan_miktar": proje_kalemi.kullanilan_miktar,
                    "rezerv_edilen_miktar": proje_kalemi.rezerv_edilen_miktar,
                    "kullanilabilir_miktar": kullanilabilir_miktar,
                    # "toplam_butce": proje_kalemi.toplam_butce,
                    # "kullanilan_butce": proje_kalemi.kullanilan_butce,
                    # "rezerv_edilen_butce": proje_kalemi.rezerv_butce,
                    # "kullanilabilir_butce": kullanilabilir_butce
                })

        return render_template("dashboard/proje_satinalma_talep_basvuru.html",
                               proje_id=proje_id,
                               butce_kalemi_id=butce_kalemi_id,
                               satinalma_talep_form=satinalma_talep_form,
                               satinalma_talebi_yapilabilir_mi=satinalma_talebi_yapilabilir_mi)

    @login_required
    @auth.requires(Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma-talep/<int:butce_kalemi_id>/talep-olustur",
           methods=["POST"])
    def satinalma_talebi_kaydet(self, proje_id, butce_kalemi_id):

        """
        Talep Oluşturur

        """

        try:
            satinalma_talep_formu = ProjeSatinAlmaTalepleri(request.form)

            if not satinalma_talep_formu.validate():
                return render_template("dashboard/proje_satinalma_talep_basvuru.html",
                                       proje_id=proje_id,
                                       butce_kalemi_id=butce_kalemi_id,
                                       satinalma_talep_form=satinalma_talep_formu)

            # mkk ya eklenen uyelerin aynı kişi olma durumuna bakilir
            select_field_list = [satinalma_talep_formu.baskan, satinalma_talep_formu.yedek_uye,
                                 satinalma_talep_formu.yedek_uye2,
                                 satinalma_talep_formu.uye, satinalma_talep_formu.yedek_baskan,
                                 satinalma_talep_formu.uye2
                                 ]

            seen = set()
            for select_field in select_field_list:
                if select_field.data not in seen:
                    seen.add(select_field.data)
                else:
                    select_field.errors.append("Komisyon üyesini birden fazla kez dahil ettiniz")

            if not satinalma_talep_formu.validate():
                return render_template("dashboard/proje_satinalma_talep_basvuru.html",
                                       proje_id=proje_id,
                                       butce_kalemi_id=butce_kalemi_id,
                                       satinalma_talep_form=satinalma_talep_formu)

            genel_teknik_sartname = request.files.get(
                satinalma_talep_formu.genel_teknik_sartname_belge.name, None
            )
            genel_teknik_sartname_file = None
            if genel_teknik_sartname:
                genel_teknik_sartname_file = File(content=genel_teknik_sartname,
                                                  user_id=current_user.id)
                DB.session.add(genel_teknik_sartname_file)

            proje_kalemleri = DB.session.query(ProjeKalemi).filter(
                ProjeKalemi.proje_id == proje_id,
                ProjeKalemi.proje_turu_butce_kalem_id == butce_kalemi_id).all()

            satinalma_talebi = ProjeSatinAlmaTalebi(proje_id=proje_id,
                                                    butce_kalem_id=butce_kalemi_id,
                                                    mkk_baskan_id=satinalma_talep_formu.baskan.data,
                                                    mkk_uye1_id=satinalma_talep_formu.uye.data,
                                                    mkk_uye2_id=satinalma_talep_formu.uye2.data,
                                                    mkk_yedek_baskan_id=satinalma_talep_formu.yedek_baskan.data,
                                                    mkk_yedek_uye1_id=satinalma_talep_formu.yedek_uye.data,
                                                    mkk_yedek_uye2_id=satinalma_talep_formu.yedek_uye2.data,
                                                    )
            DB.session.add(satinalma_talebi)
            DB.session.flush()

            talep_kalemi_sayisi = 0
            for proje_kalemi in proje_kalemleri:
                for talep in satinalma_talep_formu.talepler:
                    kullanilabilir_miktar = proje_kalemi.toplam_miktar - proje_kalemi.kullanilan_miktar - proje_kalemi.rezerv_edilen_miktar
                    if proje_kalemi.id == talep.proje_kalemi_id.data and talep.secili_mi.data and (
                            kullanilabilir_miktar > 0):
                        if not (0 < talep.talep_edilen_miktar.data <= kullanilabilir_miktar):
                            flash("Talep edilen miktar sıfırdan büyük ve kullanılabilir miktardan "
                                  "küçük olmak zorunda.",
                                  "error")
                            break
                        teknik_sartname = request.files.get(talep.teknik_sartname_belge.name, None)
                        if teknik_sartname:
                            teknik_sartname_file = File(content=teknik_sartname,
                                                        user_id=current_user.id)
                            DB.session.add(teknik_sartname_file)
                            DB.session.flush()
                            talep_teknik_sartname_file_id = teknik_sartname_file.id
                        elif genel_teknik_sartname:
                            talep_teknik_sartname_file_id = genel_teknik_sartname_file.id
                        else:
                            # eger ilgili talebe ozel teknik sartname yuklenmemisse ve genel bir teknik
                            # şartnamede yuklememis ise hata donulur
                            flash("Teknik şartname yüklemek zorundasınız", "error")
                            break

                        talep_kalemi_sayisi += 1
                        # talep edilen miktar proje kaleminden rezerv edilir
                        proje_kalemi.rezerv_edilen_miktar += talep.talep_edilen_miktar.data
                        talep_kalemi = TalepKalemleri(satinalma_id=satinalma_talebi.id,
                                                      teknik_sartname_file_id=talep_teknik_sartname_file_id,
                                                      proje_kalemi_id=proje_kalemi.id,
                                                      talep_miktari=talep.talep_edilen_miktar.data)
                        DB.session.add(talep_kalemi)

            if not talep_kalemi_sayisi:
                flash("Satınalma talebini tamamlamak için en az bir kalem seçmelisiniz", "error")

            # eger bir hata var ise db session rollback edilip hatalari kullaniciya gostermek icin
            # ilgili sayfa render edilir
            if get_flashed_messages(category_filter=["error"]):
                DB.session.rollback()
                return render_template("dashboard/proje_satinalma_talep_basvuru.html",
                                       proje_id=proje_id,
                                       butce_kalemi_id=butce_kalemi_id,
                                       satinalma_talep_form=satinalma_talep_formu)
            # satinalma id si talep numarasi olarak atanir
            satinalma_talebi.talep_numarasi = str(satinalma_talebi.id)
            # st1 state id satinalma durum id olarak atanir
            satinalma_talebi.durum_id = 34

            proje = DB.session.query(Proje.proje_no.label("proje_no")).filter(
                Proje.id == proje_id).first()
            for bap_admin in bap_yetkili_and_admin_ids():
                payload = {
                    "notification_receiver": bap_admin.person_id,
                    "notification_title": "Satınalma Talebi Yapıldı",
                    "notification_message": "{} adlı kullanıcı {} numaralı projede satınalma talebi yaptı".format(
                        current_user.username,
                        proje.proje_no),
                }

                signal_sender(log=False, notification=True, **payload)

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "satinalma_talebi_olustur").type_index,
                "nesne": '',
                "nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı {} id li kullanici satinalma talebi yaptı .".format(
                    current_user.id,
                    current_user.username)
            }
            signal_sender(**signal_payload)
            DB.session.commit()

            flash("Satınalma talebi başarıyla oluşturuldu.", "success")
        except Exception as exc:
            flash("Satınalma talebi yaparken beklenmedik bir sorunla karşılaşıldı. "
                  "Lütfen daha sonra tekrar deneyin")
            DB.session.rollback()
            CustomErrorHandler.error_handler()
        return redirect(url_for("proje.satinalma_talepleri",
                                proje_id=proje_id))

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_satinalma_talepleri_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma-talepleri/duyuru-goster", methods=["POST"],
           endpoint="duyuru_goster")
    def duyuru_goster(self, proje_id):
        """
        Butce Kalemleri Ürünlerini Listeler

        """
        duyuru_id = request.get_json()['duyuru_id']
        duyuru_form = DuyuruForm()
        duyuru_icerigi = DB.session.query(Icerik.icerik.label("icerik"),
                                          Icerik.baslik.label("baslik"),
                                          Icerik.id.label("id")).filter(
            Icerik.id == duyuru_id).first()

        duyuru_form.duyuru_metni.data = duyuru_icerigi.icerik
        duyuru_form.duyuru_basligi.data = duyuru_icerigi.baslik
        duyuru_form.duyuru_id.data = duyuru_icerigi.id

        form_text = """
        {% from 'macros/_formhelpers.html' import render_text_field %}
        <form id="duyuru-duzenle-form">
        {{ form.csrf_token }}
        {{ form.duyuru_id}}
        {{render_text_field(form.duyuru_basligi)}}
        <br>
        {{ form.duyuru_metni }}
        </form>
        """
        data = {
            'duyuru': render_template_string(form_text, form=duyuru_form)
        }
        return jsonify(status="success", data=data)

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_satinalma_talepleri_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma-talepleri/duyuru-kaydet", methods=["POST"],
           endpoint="duyuru_kaydet")
    def duyuru_kaydet(self, proje_id):
        """
        Duyuruları Listeler

        """
        duyuru_duzenle_form = request.get_json()['duyuru_form']

        imd = ImmutableMultiDict(
            [(duyuru['name'], duyuru['value']) for duyuru in duyuru_duzenle_form])
        duyuru_form = DuyuruForm(imd)

        if not duyuru_form.validate():
            form_text = """
                    {% from 'macros/form_helpers/text_fields.html' import render_text_field %}
                    <form id="duyuru-duzenle-form">
                    {{ form.csrf_token }}
                    {{ form.duyuru_id}}
                    {{render_text_field(form.duyuru_basligi)}}
                    <br>
                    {{ form.duyuru_metni }}
                    </form>
                    """
            data = {
                'duyuru_form': render_template_string(form_text, form=duyuru_form)
            }
            return jsonify(status="error",
                           message="Lütfen doldurulması gereken alanları boş bırakmayınız.",
                           data=data), 400

        duyuru_yurutucunun_mu = DB.session.query(ProjeSatinAlmaTalebi).filter(
            ProjeSatinAlmaTalebi.proje_id == proje_id,
            ProjeSatinAlmaTalebi.duyuru_id == duyuru_form.duyuru_id.data).first()

        if not duyuru_yurutucunun_mu:
            return jsonify(status="error",
                           message="Değiştirmeye çalıştığınız duyuru size ait değil. "
                                   "Lütfen yetkili ile iletişime geçiniz."), 400

        try:
            duyuru_icerigi = DB.session.query(Icerik).filter(
                Icerik.id == duyuru_form.duyuru_id.data).first()
            duyuru_icerigi.baslik = duyuru_form.duyuru_basligi.data
            duyuru_icerigi.icerik = duyuru_form.duyuru_metni.data
            duyuru_yurutucunun_mu.duyuru_duzenlensin_mi = False

            payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("icerik").get(
                    "satinalma_duyurusu_duzenlendi").type_index,
                "ekstra_mesaj": "".format(),
                "nesne": 'İçerik',
                "nesne_id": duyuru_form.duyuru_id.data,
            }

            signal_sender(notification=True, **payload)

            for yetkili in bap_yetkili_and_admin_ids():
                payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("icerik").get(
                        "satinalma_duyurusu_duzenlendi").type_index,
                    "ekstra_mesaj": "{} id'li duyuru içeriği {} isimli kullanıcı tarafından değiştrildi".format(
                        duyuru_form.duyuru_id.data, current_user.username),
                    "notification_receiver": yetkili.person_id,
                    "notification_title": "{} İsimli Kullanıcı Duyuru İçeriği Düzenledi".format(
                        current_user.username),
                    "notification_message": "{} isimli kullanıcı duyuru içeriği düzenledi. Lütfen kontrol ediniz".format(
                        current_user.username),
                    "proje_id": proje_id
                }
                signal_sender(log=False, notification=True, **payload)
            DB.session.commit()
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                                             hata="Duyuru içeriği değiştirilirken bir hata oluştu. "
                                                  "Hata: {}, İçerik id: {}".format(exc,duyuru_form.duyuru_id.data)
                                             )
            return jsonify(status="error",
                           message="Bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.!"), 400

        return jsonify(status="success")

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_satinalma_talepleri_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma/<int:satinalma_id>/teknik-sartname-duzenle",
           methods=["GET"])
    def satinalma_teknik_sartname_duzenle(self, proje_id, satinalma_id):
        """
        Satinalma talep kalemleri teknik sartname duzenleme view methodu

        """
        satinalma_talep_kalemleri = DB.session.query(TalepKalemleri).filter(
            TalepKalemleri.satinalma_id == satinalma_id,
            TalepKalemleri.teknik_sartname_duzenlensin_mi == True
        ).all()

        if not satinalma_talep_kalemleri:
            flash(_("Teknik şartnamesi düzenlenecek talep kalemi bulunamadı."))
            return redirect(url_for("proje.satinalma_talepleri",
                                    proje_id=proje_id))

        teknik_sartname_duzenle_form = TeknikSartnameDuzenlemeFormu()
        for talep_kalemi in satinalma_talep_kalemleri:
            if talep_kalemi.teknik_sartname_duzenlensin_mi:
                teknik_sartname_duzenle_form.talep_kalemleri.append_entry({
                    "talep_kalemi_id": talep_kalemi.id,
                    "eski_teknik_sartname_id": talep_kalemi.teknik_sartname_file_id,
                    "proje_kalemi_adi": talep_kalemi.proje_kalemi.ad,
                    "talep_edilen_miktar": talep_kalemi.talep_miktari,
                    "birim": talep_kalemi.proje_kalemi.birim.value
                })

        return render_template("dashboard/teknik_sarname_duzenle.html",
                               proje_id=proje_id,
                               satinalma_id=satinalma_id,
                               teknik_sartname_duzenle_form=teknik_sartname_duzenle_form)

    @login_required
    @auth.requires(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_satinalma_talepleri_goruntuleme"]),
        Or(ProjeYurutucusu(), Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:proje_id>/dashboard/satinalma/<int:satinalma_id>/teknik-sartname-kaydet",
           methods=["POST"])
    def satinalma_teknik_sartname_post(self, proje_id, satinalma_id):
        """
        Satinalma talep kalemleri teknik sartname duzenleme kaydetme view,

        """
        teknik_sartname_duzenle_form = TeknikSartnameDuzenlemeFormu(request.form)

        if not teknik_sartname_duzenle_form.validate():
            return render_template("dashboard/teknik_sarname_duzenle.html",
                                   proje_id=proje_id,
                                   satinalma_id=satinalma_id,
                                   teknik_sartname_duzenle_form=teknik_sartname_duzenle_form)

        satinalma_talebi = DB.session.query(ProjeSatinAlmaTalebi).filter(
            ProjeSatinAlmaTalebi.id == satinalma_id).first()

        for talep_kalemi in satinalma_talebi.talep_kalemleri:
            for talep_kalemi_form in teknik_sartname_duzenle_form.talep_kalemleri:
                if talep_kalemi.id == talep_kalemi_form.talep_kalemi_id.data:
                    yeni_teknik_sartname = request.files.get(
                        talep_kalemi_form.yeni_teknik_sartname.name)
                    yeni_file = File(user_id=current_user.id,
                                     content=yeni_teknik_sartname)
                    DB.session.add(yeni_file)
                    DB.session.flush()
                    talep_kalemi.teknik_sartname_file_id = yeni_file.id
                    talep_kalemi.teknik_sartname_duzenlensin_mi = False

        DB.session.commit()
        payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "teknik_sartname_duzenle").type_index,
            "ekstra_mesaj": "{} id li satınalmanin talep kalemleri teknik şartname dosyası bap "
                            "yetkilisi talebiyle yürütücü tarafından düzenlendi".format(
                satinalma_id),
            "nesne": 'ProjeSatinAlmaTalebi',
            "nesne_id": satinalma_talebi.id,
        }

        signal_sender(notification=True, **payload)

        for yetkili in bap_yetkili_and_admin_ids():
            payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("icerik").get(
                    "satinalma_duyurusu_duzenlendi").type_index,
                "ekstra_mesaj": "{} id'li satınalmanın teknik şartname dosyaları {} isimli "
                                "kullanıcı tarafından değiştrildi".format(satinalma_id,
                                                                          current_user.username),
                "notification_receiver": yetkili.person_id,
                "notification_title": "{} İsimli Kullanıcı Teknik Şartname Düzenledi".format(
                    current_user.username),
                "notification_message": "{} isimli kullanıcı talep edilen teknik şartname düzenleme "
                                        "işlemini gerçekleştirdi. Lütfen kontrol ediniz".format(
                    current_user.username),
                "proje_id": proje_id
            }
            signal_sender(log=False, notification=True, **payload)
        flash(_("Teknik şartnameler başarıyla düzenlendi."))
        return redirect(url_for("proje.satinalma_talepleri",
                                proje_id=proje_id))
