"""BAP Proje Degerlendirme View Modulu"""

from flask import render_template, abort, current_app, jsonify, redirect, url_for, request
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_allows import Or, And
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, lazyload

from sqlalchemy.orm.exc import NoResultFound

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.lib.auth import ProjeYurutucusu, AtanmisHakem
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.proje.forms.dashboard.degerlendirme import DegerlendirmeGuncelleForm
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import ProjeDegerlendirmeleri, ProjeHakemleri
from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.bap.hakem_dashboard.forms import ProjeDegerlendirmeForm
from zopsedu.bap.proje.views.dashboard.common import get_proje_with_related_fields, \
    get_next_states_info, \
    get_actions_info
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.personel import Personel


class ProjeDegerlendirmeView(FlaskView):
    """ProjeDegerlendirmeleri View"""

    @staticmethod
    @login_required
    @auth.requires(Or(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_degerlendirme_goruntuleme"]),
        Role('BAP Yetkilisi'), Role("BAP Admin")))
    @route('<int:proje_id>/dashboard/degerlendirme', methods=["GET"],
           endpoint='degerlendirme_listele')
    def degerlendirme_listele(proje_id):
        """Proje degerlemdirmelerini goruntulemek icin kullanilir"""
        proje_yurutucusu_mu = ProjeYurutucusu()
        atanmis_hakem = AtanmisHakem()

        proje = DB.session.query(Proje).options(
            joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
                OgretimElemani.personel).load_only("id").joinedload(
                Personel.person).load_only("ad", "soyad"),
            lazyload(Proje.proje_detayi),
            lazyload(Proje.proje_hakem_onerileri),
            lazyload(Proje.proje_destekleyen_kurulus),
            lazyload(Proje.proje_kalemleri),
        ).filter(Proje.id == proje_id,
                 or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                     Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).first()

        next_states_info = get_next_states_info(proje_id=proje_id)
        actions_info = get_actions_info(proje_id=proje_id)

        proje_degerlendirmeleri = []
        """
        Proje degerlendirme teklifini kabul eden hakemlerin tamamlanan degerlendirmelerini 
        listeleyip proje_degerlendirme templatetine gonderir
        """
        for proje_hakemi in proje.kabul_edilen_proje_hakemleri:
            for proje_degerlendirme in proje_hakemi.tamamlanan_proje_degerlendirmeleri:
                hakem_ad_soyad = ""
                hakem = proje_hakemi.hakem
                if hakem.person_id:
                    hakem_ad_soyad = hakem.person.ad + hakem.person.soyad
                elif hakem.personel_id:
                    hakem_ad_soyad = hakem.personel.person.ad + hakem.personel.person.soyad
                proje_degerlendirmeleri.append({
                    "hakem_ad_soyad": hakem_ad_soyad,
                    "degerlendirme_sonucu": proje_degerlendirme.sonuc,
                    "degerlendirme_id": proje_degerlendirme.id,
                    "degerlendirme_incelendi_mi": proje_degerlendirme.degerlendirme_incelendi_mi,
                    "rapor_tipi": proje_degerlendirme.rapor.rapor_tipi,
                    "degerlendirilen_rapor_file_id": proje_degerlendirme.rapor.file_id
                })

        degerlendirme_guncelleme_formu = DegerlendirmeGuncelleForm()
        return render_template('dashboard/proje_degerlendirmeleri.html',
                               proje_degerlendirmeleri=proje_degerlendirmeleri,
                               proje_id=proje_id,
                               next_states_info=next_states_info,
                               actions_info=actions_info,
                               proje_yurutucusu_mu=proje_yurutucusu_mu,
                               atanmis_hakem_mi=atanmis_hakem,
                               degerlendirme_guncelleme_formu=degerlendirme_guncelleme_formu,
                               proje=proje)

    # todo: işlevli mi ???
    @staticmethod
    @login_required
    # todo: proje yurutucusu olma durumu eklenmesi gerekiyormu.
    # todo: aynı kontrol buna benzer(proje kararlari, proje mesajlari vb)
    # todo: viewlarda yapilmalimi kontrol et
    @auth.requires(Or(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_degerlendirme_goruntuleme"]),
        Role('BAP Yetkilisi'), Role("BAP Admin")))
    @route('<int:proje_id>/dashboard/degerlendirme/<int:degerlendirme_id>', methods=["GET"],
           endpoint='degerlendirme_detay')
    def degerlendirme_detay(proje_id, degerlendirme_id):
        """Proje degerlendirme detayı goruntulemek icin kullanilir"""
        user_id = current_user.id
        try:
            # todo: degerlendirme tamamlandimi kontrol et
            # todo: degerlendirme ilgili projeye mi ait kontrol et
            proje_degerlendirme = DB.session.query(
                ProjeDegerlendirmeleri
            ).join(
                ProjeDegerlendirmeleri.degerlendirme_hakemi
            ).filter(
                ProjeDegerlendirmeleri.id == degerlendirme_id,
                ProjeDegerlendirmeleri.degerlendirme_sonuclandi_mi == True,
                ProjeHakemleri.proje_id == proje_id).one()
        except NoResultFound as exc:
            CustomErrorHandler.error_handler(
                hata="Var olmayan bir proje değerlendirmesine ulaşılmaya çalışıldı."
                     "User id: {}, Hata: {}".format(user_id, exc))
            return abort(404)
        # todo: degerlendirme sablon uzerinden mi yapilacak var olan form ile mi devam edilecek ?
        degerlendirme_form = ProjeDegerlendirmeForm(**proje_degerlendirme.degerlendirme)
        return render_template(
            'dashboard/proje_degerlendirme_detay.html',
            degerlendirme_form=degerlendirme_form,
            proje_id=proje_id)

    @staticmethod
    @login_required
    @auth.requires(Or(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_degerlendirme_goruntuleme"]),
        Role('BAP Yetkilisi'), Role("BAP Admin")))
    @route('hakem_rapor_gorusleri_oku/<int:degerlendirme_id>/',
           methods=["GET"],
           endpoint='hakem_rapor_gorusleri_oku')
    def hakem_rapor_gorusleri_oku(degerlendirme_id):
        try:
            proje_degerlendirme = DB.session.query(ProjeDegerlendirmeleri).filter(
                ProjeDegerlendirmeleri.id == degerlendirme_id,
                ProjeDegerlendirmeleri.degerlendirme_sonuclandi_mi == True).first()
            if not proje_degerlendirme:
                return jsonify(status="error",
                               hata_mesaji="İlgili değerlendirme bulunamadı"), 400
            degerlendirme = {
                "rapor_turu": proje_degerlendirme.rapor.rapor_tipi.value,
                "degerlendirme_sonucu": proje_degerlendirme.sonuc.value,
                "gonderim_tarihi": proje_degerlendirme.degerlendirme_gonderim_tarihi.strftime(
                    "%d.%m.%Y"),
                "metin": proje_degerlendirme.degerlendirme,
            }
        except Exception as exc:
            return jsonify(status="error")

        return jsonify(status="success", degerlendirme=degerlendirme)

    @staticmethod
    @login_required
    @auth.requires(And(Permission(
        *permission_dict["bap"]["proje"]["dashboard"]["proje_degerlendirme_goruntuleme"]),
        Or(Role('BAP Yetkilisi'), Role("BAP Admin"))))
    @route('degerlendirme/<int:degerlendirme_id>/guncelle',
           methods=["POST"])
    def degerlendirme_guncelle(degerlendirme_id):
        """
        Yetkili tarafindan yapilir. Degerlendirme metninde hakemin ismi yazma durumunda silmek
        icin kullanilir.
        :param degerlendirme_id:
        :return:
        """
        proje_degerlendirme = DB.session.query(ProjeDegerlendirmeleri).filter(
            ProjeDegerlendirmeleri.id == degerlendirme_id,
            ProjeDegerlendirmeleri.degerlendirme_sonuclandi_mi == True).first()
        if not proje_degerlendirme:
            return redirect(
                url_for("proje.degerlendirme_listele", proje_id=proje_degerlendirme.rapor.proje_id))
        degerlendirme_guncelle_form = DegerlendirmeGuncelleForm(request.form)
        proje_degerlendirme.degerlendirme = degerlendirme_guncelle_form.degerlendirme_metni.data
        DB.session.commit()

        return redirect(
            url_for("proje.degerlendirme_listele", proje_id=proje_degerlendirme.rapor.proje_id))
