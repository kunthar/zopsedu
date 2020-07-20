from flask import render_template

from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi

from zopsedu.bap.proje.forms.dashboard.islem_formlari import DurumFormlari, IslemFormlari
from zopsedu.lib.db import DB
from zopsedu.models import AppState, AppAction

project_management_methods_get = {}


def proje_bilgisi(proje_id):
    return DB.session.query(Proje).filter(
        Proje.id == proje_id).first()


def proje_durum_aciklmasi(state_code):
    return DB.session.query(AppState.description.label("aciklama"), AppState.state_code.label("kodu")).filter(
        AppState.state_code == state_code).first()


def proje_islem_aciklmasi(action_code):
      return DB.session.query(AppAction.description.label("aciklama"), AppAction.action_code.label("kodu")).filter(
        AppAction.action_code == action_code).first()


class StateChangeGet:
    @staticmethod
    def genel_modal_get(proje_id, form=None, code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.GenelForm()

        proje = proje_bilgisi(proje_id)
        proje_durum_aciklamasi = proje_durum_aciklmasi(code)

        return render_template("dashboard/durum_degisim_modal/genel_modal.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=proje_durum_aciklamasi,
                               form=modal_form)

    @staticmethod
    def p13_get(proje_id, form=None, code=None):
        if form:
            modal_form = form

        else:
            modal_form = DurumFormlari.P13()

        proje = proje_bilgisi(proje_id)
        proje_durum_aciklamasi = proje_durum_aciklmasi(code)

        return render_template("dashboard/durum_degisim_modal/genel_modal.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               proje_yurutucu=proje.proje_yurutucu,
                               app_state_description=proje_durum_aciklamasi,
                               form=modal_form)

    @staticmethod
    def p15_get(proje_id, form=None, code=None):
        if form:
            modal_form = form

        else:
            modal_form = DurumFormlari.P15()

        proje = proje_bilgisi(proje_id)
        proje_durum_aciklamasi = proje_durum_aciklmasi(code)

        return render_template("dashboard/durum_degisim_modal/p15.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               proje_yurutucu=proje.proje_yurutucu,
                               app_state_description=proje_durum_aciklamasi,
                               form=modal_form)

    @staticmethod
    def p18_get(proje_id, form=None, code=None):
        if form:
            modal_form = form

        else:
            modal_form = DurumFormlari.P18()

        proje = proje_bilgisi(proje_id)
        proje_durum_aciklamasi = proje_durum_aciklmasi(code)

        return render_template("dashboard/durum_degisim_modal/genel_modal.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               proje_yurutucu=proje.proje_yurutucu,
                               app_state_description=proje_durum_aciklamasi,
                               form=modal_form)

    @staticmethod
    def p19_get(proje_id, form=None, code=None):
        if form:
            modal_form = form
        else:
            modal_form = DurumFormlari.P19()

        proje = proje_bilgisi(proje_id)
        proje_durum_aciklamasi = proje_durum_aciklmasi(code)

        return render_template("dashboard/durum_degisim_modal/p15.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               proje_yurutucu=proje.proje_yurutucu,
                               app_state_description=proje_durum_aciklamasi,
                               form=modal_form)


class ActionGet:
    @staticmethod
    def pa1_get(proje_id, form=None, code='PA1'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA1()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa1.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa2_get(proje_id, form=None, code='PA2'):
        if form:
            modal_form = form

        else:
            modal_form = IslemFormlari.PA2()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa2.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa3_get(proje_id, form=None, code='PA3'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA3()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa3.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa6_get(proje_id, form=None, code='PA6'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA6()
        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa6.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa7_get(proje_id, form=None, code='PA7'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA7()
        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa7.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa10_get(proje_id, form=None, code='PA10'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA10()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa10.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa11_get(proje_id, form=None, code='PA11'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA11()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template('dashboard/islem_modal/pa11.html',
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    # yönetim kurulu kararı eklendi mail atmak için kullanılır.
    @staticmethod
    def pa12_get(proje_id, form=None, code="PA12"):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA12()
        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa12.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa13_get(proje_id, form=None, code='PA13'):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA13()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa13.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa14_get(proje_id, form=None, code='PA14'):
        if form:
            modal_form = form

        else:
            modal_form = IslemFormlari.PA14()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        modal_form.proje_no.data = proje.proje_no
        modal_form.proje_basligi.data = proje.proje_basligi
        modal_form.project_title.data = proje.project_title

        return render_template("dashboard/islem_modal/pa14.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa16_get(proje_id, form=None, code='PA16'):
        if form:
            modal_form = form

        else:
            modal_form = IslemFormlari.PA16()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa16.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa19_get(proje_id, form=None, code="PA19"):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA19()

        proje = proje_bilgisi(proje_id)
        aciklama = proje_islem_aciklmasi(code)

        return render_template("dashboard/islem_modal/pa19.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)

    @staticmethod
    def pa20_get(proje_id, form=None, code="PA20"):
        if form:
            modal_form = form
        else:
            modal_form = IslemFormlari.PA20()

        proje = proje_bilgisi(proje_id)
        proje_kalemleri = DB.session.query(ProjeKalemi).filter(
            ProjeKalemi.proje_id == proje_id).all()
        aciklama = proje_islem_aciklmasi(code)

        if not form:
            for proje_kalemi in proje_kalemleri:
                modal_form.proje_kalemleri.append_entry({
                    "proje_kalemi_id": proje_kalemi.id,
                    "proje_kalemi_adi": proje_kalemi.ad,
                    "kabul_edilen_miktar": proje_kalemi.onerilen_miktar if not proje_kalemi.toplam_miktar else proje_kalemi.toplam_miktar,
                    "kabul_edilen_yil_1": proje_kalemi.onerilen_yil_1 if not proje_kalemi.kabul_edilen_yil_1 else proje_kalemi.kabul_edilen_yil_1,
                    "kabul_edilen_yil_2": proje_kalemi.onerilen_yil_2 if not proje_kalemi.kabul_edilen_yil_2 else proje_kalemi.kabul_edilen_yil_2,
                    "kabul_edilen_yil_3": proje_kalemi.onerilen_yil_3 if not proje_kalemi.kabul_edilen_yil_3 else proje_kalemi.kabul_edilen_yil_3,
                })

        return render_template("dashboard/islem_modal/pa20.html",
                               proje_numarasi=proje.proje_no,
                               proje_adi=proje.proje_basligi,
                               proje_id=proje_id,
                               app_state_description=aciklama,
                               form=modal_form)


action_methods = {
    'PA1': ActionGet.pa1_get,
    'PA2': ActionGet.pa2_get,
    'PA3': ActionGet.pa3_get,
    # PA4 -> view
    # PA5 -> view
    'PA6': ActionGet.pa6_get,
    'PA7': ActionGet.pa7_get,
    # PA8 -> view
    # PA9 -> view
    'PA10': ActionGet.pa10_get,
    'PA11': ActionGet.pa11_get,
    # todo: kaldirilacakti demo dan dolayi pa19 a yonlendirildi.
    'PA12': ActionGet.pa19_get,

    'PA13': ActionGet.pa13_get,
    'PA14': ActionGet.pa14_get,
    # todo: view da yapilacak
    # PA15 -view,
    'PA16': ActionGet.pa16_get,

    # todo: goruntu icin
    'PA17': ActionGet.pa1_get,
    # todo: goruntu icin
    'PA18': ActionGet.pa1_get,

    'PA19': ActionGet.pa19_get,
    'PA20': ActionGet.pa20_get
}

state_change_methods = {
    'P2': StateChangeGet.genel_modal_get,
    'P3': StateChangeGet.genel_modal_get,
    'P4': StateChangeGet.genel_modal_get,
    'P5': StateChangeGet.genel_modal_get,
    'P6': StateChangeGet.genel_modal_get,
    'P7': StateChangeGet.genel_modal_get,
    'P8': StateChangeGet.genel_modal_get,
    'P9': StateChangeGet.genel_modal_get,
    'P10': StateChangeGet.genel_modal_get,
    'P11': StateChangeGet.genel_modal_get,
    'P12': StateChangeGet.genel_modal_get,
    'P13': StateChangeGet.p13_get,
    'P14': StateChangeGet.genel_modal_get,
    'P15': StateChangeGet.p15_get,
    'P16': StateChangeGet.genel_modal_get,
    'P17': StateChangeGet.genel_modal_get,
    'P18': StateChangeGet.p18_get,
    'P19': StateChangeGet.p19_get,
    'P20': StateChangeGet.genel_modal_get,
    'P21': StateChangeGet.genel_modal_get,
    'P22': StateChangeGet.genel_modal_get,
    'P23': StateChangeGet.genel_modal_get,
    'P24': StateChangeGet.genel_modal_get,
    'P25': StateChangeGet.genel_modal_get,
    'P26': StateChangeGet.genel_modal_get,
    'P27': StateChangeGet.genel_modal_get,
    'P28': StateChangeGet.genel_modal_get,
    'P29': StateChangeGet.genel_modal_get,
    'P30': StateChangeGet.genel_modal_get,
    'P31': StateChangeGet.genel_modal_get,
    'P32': StateChangeGet.genel_modal_get,
    'P33': StateChangeGet.genel_modal_get
}

project_management_methods_get.update(state_change_methods)
project_management_methods_get.update(action_methods)
