"""Proje Yurutucu Dashboard view classları"""
from flask import render_template, json
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_babel import gettext as _
from sqlalchemy import desc, or_, func, Integer

from zopsedu.bap.anasayfa.views.common import get_bap_duyurular
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.lib.db import DB
from zopsedu.auth.lib import auth, Role
from zopsedu.models import Proje, Mesaj, ProjeMesaj, Personel, AppState, AppStateTracker
from zopsedu.models import Person, User
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.models.helpers import AppStates, JobTypes


class ProjeYurutucuDashboard(FlaskView):
    """
    Proje Yurutucu Dashboard view methodlarini icerir
    """

    @staticmethod
    @login_required
    @route("kontrol-paneli", methods=["GET"])
    @auth.requires(Role("Öğretim Üyesi"),
                   menu_registry={'path': '.yurutucu_dashboard',
                                  'title': _("Kontrol Paneli")})
    @auth.requires(Role("Öğretim Üyesi"))
    def genel():
        """Proje yurutucusu dashboard genel bilgiler"""
        ogretim_gorevlisi = DB.session.query(User). \
            join(Person, Person.user_id == User.id). \
            join(Personel, Person.id == Personel.person_id). \
            add_columns(Personel.id.label("ogretim_gorevlisi_id")). \
            filter(User.id == current_user.id).one()
        ogretim_gorevlisi_id = ogretim_gorevlisi.ogretim_gorevlisi_id

        # tamamlanan proje sayisi
        tamamlanan_proje_sayisi = DB.session.query(Proje.id).join(AppState,
                                                                  AppState.id == Proje.proje_durumu_id).filter(
            AppState.current_app_state == AppStates.son, Proje.yurutucu == ogretim_gorevlisi_id).count()

        # devam eden proje sayisi
        devam_eden_proje_sayisi = DB.session.query(Proje.id).join(AppState,
                                                                  AppState.id == Proje.proje_durumu_id).filter(
            or_(AppState.current_app_state == AppStates.basvuru_kabul, AppState.current_app_state == AppStates.devam),
            Proje.yurutucu == ogretim_gorevlisi_id).count()

        # tamamlanmis basvurular arasinda yurutucu oldugu projeleri getirir.
        yurutucu_oldugu_projeler = DB.session.query(Proje.id.label("proje_id"),
                                                    Proje.yurutucu,
                                                    Proje.proje_basvuru_durumu,
                                                    Proje.kabul_edilen_butce
                                                    ). \
            filter(Proje.yurutucu == ogretim_gorevlisi_id,
                   or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                       Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor)).all()

        proje_kalemleri = DB.session.query(ProjeKalemi.kullanilan_butce.label("kullanilan_butce")). \
            join(Proje, Proje.id == ProjeKalemi.proje_id). \
            filter(Proje.yurutucu == ogretim_gorevlisi_id).all()
        harcanan_butce = 0

        for proje_kalemi in proje_kalemleri:
            harcanan_butce += proje_kalemi.kullanilan_butce

        toplam_butce = 0
        proje_idleri = []
        proje_idleri_dict = []
        islem_gecmisi=[]
        for proje in yurutucu_oldugu_projeler:
            toplam_butce += proje.kabul_edilen_butce if proje.kabul_edilen_butce else 0
            proje_idleri_dict.append({"proje_id": proje.proje_id})
            proje_idleri.append(proje.proje_id)

        # yurutucusu oldugu ve tamamlanmis projelerin islem gecmislerini getirir
        proje_islem_gecmisleri = []
        for id in proje_idleri_dict:
            islem_gecmisi = DB.session.query(AppStateTracker).\
                filter(AppStateTracker.params.contains(id),
                       or_(AppStateTracker.job_type == JobTypes.project_state_change,
                           AppStateTracker.job_type == JobTypes.project_action)). \
                join(Proje, Proje.id == AppStateTracker.params["proje_id"].astext.cast(Integer)).\
                join(Person, Person.user_id == AppStateTracker.triggered_by). \
                join(AppState, AppStateTracker.state_id == AppState.id). \
                add_columns(
                AppState.state_code.label("state_code"),
                Person.ad.label("ad"),
                Person.soyad.label("soyad"),
                Proje.proje_basligi.label("proje_basligi"),
                Proje.id.label("proje_id")
            ).order_by(desc(AppStateTracker.created_at)).limit(15).all()


        # yurutucusu oldugu ve tamamlanmis projelerin mesajlarini getirir
        proje_mesajlari = DB.session.query(ProjeMesaj).join(
            Proje, ProjeMesaj.proje_id == Proje.id).join(
            Mesaj, Mesaj.id == ProjeMesaj.mesaj_id).join(
            Person, Person.id == Mesaj.alici).add_columns(Proje.proje_basligi,
                                                          Proje.id.label("proje_id"),
                                                          Mesaj.okundu,
                                                          Mesaj.gonderim_zamani,
                                                          Mesaj.baslik,
                                                          Person.ad.label("gonderen_ad"),
                                                          Person.soyad.label("gonderen_soyad")).filter(
            ProjeMesaj.proje_id.in_(proje_idleri)).order_by(desc(Mesaj.created_at)).limit(15).all()

        bap_duyurular = get_bap_duyurular()

        return render_template('yurutucu_dashboard/genel.html',
                               tamamlanan_proje_sayisi=tamamlanan_proje_sayisi,
                               devam_eden_proje_sayisi=devam_eden_proje_sayisi,
                               toplam_butce=toplam_butce,
                               harcanan_butce=harcanan_butce,
                               islem_gecmisi=islem_gecmisi,
                               proje_mesajlari=proje_mesajlari,
                               bap_duyurular=bap_duyurular)
