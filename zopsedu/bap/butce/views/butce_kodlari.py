from flask import render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_classful import FlaskView, route
from flask_babel import gettext as _

from zopsedu.auth.lib import Permission, auth
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.detayli_hesap_planlari import DetayliHesapPlanlari
from zopsedu.lib.db import DB
from zopsedu.lib.sessions import SessionHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import GenelAyarlar
from zopsedu.bap.butce.forms.butce_kodlari import ButceKodlari, HesapKodlariSearch, \
    FonksiyonelKodlar
from zopsedu.yonetim.bap_yonetimi.common import genel_ayarlar_guncelle


# todo: genel ayarlar guncelle methodu genel biryere tasinmali mi?


class ButceKodlariView(FlaskView):
    """Bap Bütçe Kodları view classi"""

    @staticmethod
    @login_required
    @route('/butce-kodlari', methods=['GET'])
    @auth.requires(Permission(*permission_dict["bap"]["butce"]["butce_kodlari_goruntuleme"]),
                   menu_registry={"path": ".bap.butce.butce_kodlari_goruntuleme",
                                  "title": _("Bütçe Kodları")})
    def butce_kodlari_goruntuleme():
        """
        Butce kodlarinin goruntulendigi view
        """
        universite_id = SessionHandler.universite_id()
        genel_ayar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                              aktif_mi=True).first()
        hesap_kodu_search_form = HesapKodlariSearch()

        if genel_ayar and genel_ayar.bap_butce:
            kurum_kodlari_form = ButceKodlari(**genel_ayar.bap_butce)
            fonksiyonel_kodlar_form = FonksiyonelKodlar(**genel_ayar.bap_butce)
        else:
            kurum_kodlari_form = ButceKodlari()
            fonksiyonel_kodlar_form = FonksiyonelKodlar()
        return render_template("butce_kodlari_listeleme.html",
                               butce_kodlari_formu=kurum_kodlari_form,
                               fonksiyonel_kodlar=fonksiyonel_kodlar_form,
                               hesap_kodu_search_form=hesap_kodu_search_form)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["butce"]["butce_kodlari_kaydetme"]))
    @route('/butce-kodlari', methods=['POST'])
    def kurum_kodlari_kaydet():
        """
        Butce kodlarinin kaydedildigi view
        """
        butce_kodlari_form = ButceKodlari(request.form)
        universite_id = SessionHandler.universite_id()
        if not butce_kodlari_form.validate():
            flash(_("Lütfen hatalı yerleri düzeltip tekrar deneyin."))

            fonksiyonel_kodlar_form = FonksiyonelKodlar()
            hesap_kodu_search_form = HesapKodlariSearch()
            return render_template('butce_kodlari_listeleme.html',
                                   fonksiyonel_kodlar=fonksiyonel_kodlar_form,
                                   hesap_kodu_search_form=hesap_kodu_search_form,
                                   butce_kodlari_formu=butce_kodlari_form)

        butce_kodlari_form_data = dict(butce_kodlari_form.data)
        butce_kodlari_form_data.pop('csrf_token')
        eski_genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                                      aktif_mi=True).first()
        if eski_genel_ayarlar:
            yeni_data = eski_genel_ayarlar.to_dict()["bap_butce"]
            yeni_data.update(butce_kodlari_form_data)
            yeni_ayarlar = genel_ayarlar_guncelle(eski_genel_ayarlar,
                                                  guncellenecek_field="bap_butce",
                                                  yeni_data=yeni_data)
        else:
            yeni_ayarlar = GenelAyarlar(universite_id=universite_id,
                                        bap_butce=butce_kodlari_form_data)

        DB.session.add(yeni_ayarlar)
        DB.session.commit()
        flash(_("İşlem başarıyla gerçekleşti."))
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "butce_kodlari_kaydet").type_index,
            "nesne": 'GenelAyarlar',
            "nesne_id": yeni_ayarlar.id,
            "ekstra_mesaj": "{} adlı kullanıcı, bap bütçe kurum kodları ayarlarını güncelledi.".format(
                current_user.username)
        }
        signal_sender(**signal_payload)

        return redirect(url_for("butce.ButceKodlariView:butce_kodlari_goruntuleme"))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["butce"]["butce_kodlari_kaydetme"]))
    @route('/fonksiyonel-kodlar', methods=['POST'])
    def fonksiyonel_kodlari_kaydet():
        """
        Butce kodlarinin kaydedildigi view
        """
        fonksiyonel_kodlar_form = FonksiyonelKodlar(request.form)
        universite_id = SessionHandler.universite_id()
        if not fonksiyonel_kodlar_form.validate():
            flash(_("Lütfen hatalı yerleri düzeltip tekrar deneyin."))
            butce_kodlari_form = ButceKodlari()
            hesap_kodu_search_form = HesapKodlariSearch()
            return render_template('butce_kodlari_listeleme.html',
                                   fonksiyonel_kodlar=fonksiyonel_kodlar_form,
                                   hesap_kodu_search_form=hesap_kodu_search_form,
                                   butce_kodlari_formu=butce_kodlari_form)

        fonksiyonel_kodlar_form_data = dict(fonksiyonel_kodlar_form.data)
        fonksiyonel_kodlar_form_data.pop('csrf_token')
        eski_genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                                      aktif_mi=True).first()
        if eski_genel_ayarlar:
            yeni_data = eski_genel_ayarlar.to_dict()["bap_butce"]
            yeni_data.update(fonksiyonel_kodlar_form_data)
            yeni_ayarlar = genel_ayarlar_guncelle(eski_genel_ayarlar,
                                                  guncellenecek_field="bap_butce",
                                                  yeni_data=yeni_data)
        else:
            yeni_ayarlar = GenelAyarlar(universite_id=universite_id,
                                        bap_butce=fonksiyonel_kodlar_form_data)
        DB.session.add(yeni_ayarlar)
        DB.session.commit()
        flash(_("İşlem başarıyla gerçekleşti."))
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "butce_kodlari_kaydet").type_index,
            "nesne": 'GenelAyarlar',
            "nesne_id": yeni_ayarlar.id,
            "ekstra_mesaj": "{} adlı kullanıcı, bap bütçe fonksiyonel kod ayarlarını güncelledi.".format(
                current_user.username)
        }
        signal_sender(**signal_payload)

        return redirect(url_for("butce.ButceKodlariView:butce_kodlari_goruntuleme"))

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["butce"]["butce_kodlari_goruntuleme"]))
    @route('/butce-kodlari/detayli-hesap-kodlari/search', methods=['POST'])
    def detayli_hesap_kodlari_search(self):
        """
        Butce detaylı hesap kodlarinin search edildigi view
        """

        search_query = DB.session.query(DetayliHesapPlanlari)

        form_data = request.form.to_dict()
        search_form = HesapKodlariSearch(**form_data)

        universite_id = SessionHandler.universite_id()
        genel_ayarlar = DB.session.query(GenelAyarlar).filter_by(universite_id=universite_id,
                                                                 aktif_mi=True).first()

        if not search_form.validate():
            total_record = search_query.count()
            result = search_query.offset(form_data['start']).limit(
                form_data['length']).all()
            return self.process_data(result, form_data, total_record)
        if search_form.kod.data:
            search_query = search_query.filter(
                DetayliHesapPlanlari.hesap_kodu.ilike('%' + search_form.kod.data + '%'))
        if search_form.aciklama.data:
            search_query = search_query.filter(
                DetayliHesapPlanlari.ana_hesap_hesap_grubu_yardimci_hesap_adi.ilike(
                    '%' + search_form.aciklama.data + '%'))
        if genel_ayarlar:
            if genel_ayarlar.bap_butce:
                # detayli_hesap_kodlari icerisinde 38 li ve 39 ku universiteler icin ayri kodlar
                # bulunmakta. Eger ayarlar bolumunden kurum kodu girilmis ise ("39.01.00.00" gibi)
                # parse edilip 38 li veya 39 lu oldugu anlasilir query ona gore atilir.
                kurum_kodu = genel_ayarlar.bap_butce.get("kurum_kodu")
                yok_kurum_kodu = kurum_kodu.split(".")[0]
                try:
                    if int(yok_kurum_kodu) == 38 or int(yok_kurum_kodu) == 39:
                        search_query = search_query.filter(
                            DetayliHesapPlanlari.kurum_turu == int(yok_kurum_kodu))
                except Exception as exc:
                    pass

        total_record = search_query.count()
        result = search_query.offset(form_data['start']).limit(
            form_data['length']).all()
        return self.process_data(result, form_data, total_record)

    def process_data(self, result, form_data, total_record):
        data = [[
            r.hesap_kodu,
            r.ana_hesap_hesap_grubu_yardimci_hesap_adi] for r in result]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record})
