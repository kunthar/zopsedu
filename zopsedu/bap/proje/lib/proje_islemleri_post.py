from datetime import datetime, timedelta
from decimal import Decimal

from flask_babel import gettext as _
from flask_login import current_user
from sqlalchemy.orm import  joinedload
from werkzeug.datastructures import ImmutableMultiDict

from zopsedu.bap.models.helpers import NotTipi, ProjeBasvuruDurumu
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_not import ProjeNot
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_detay import ProjeDegerlendirmeleri, ProjeHakemleri, \
    ProjeHakemDavetDurumlari
from zopsedu.bap.models.proje_rapor import ProjeRaporDurumu
from zopsedu.bap.models.proje_rapor import ProjeRapor, ProjeRaporTipi
from zopsedu.bap.models.toplanti import BapGundem
from zopsedu.bap.proje.forms.dashboard.islem_formlari import DurumFormlari, IslemFormlari
from zopsedu.bap.proje.lib.proje_islemleri_get import project_management_methods_get
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.proje_state_dispatcher import ProjeStateDispacther
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.personel.models.hakem import Hakem

from zopsedu.bap.models.helpers import ProjeSuresiBirimi

project_management_methods_post = {}


def proje_bilgisi(proje_id):
    return DB.session.query(Proje).filter(
        Proje.id == proje_id).first()


def form_to_dict(form_list):
    form_dict = {}

    for form in form_list:
        form_dict.update({
            form['name']: form['value']
        })

    return form_dict


def hakem_degerlendirme_notification(rapor_id, hakem_id, person_id):
    """
    Hakeme proje raporu degerlendirmesi eklendigini bildirmek icin notification gonderir
    :param rapor_id: degerlendirmesi eklenen raporun id si
    :param hakem_id: degerlendirme eklenen hakem id
    :param person_id: mesajin gonderilecegi kisinin id si (hakemin id si)
    :return:
    """
    # hakeme degerlendirme notificationi gonderir
    payload = {
        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
            "rapor_hakeme_gonderildi").type_index,
        "ekstra_mesaj": "{} isimli kullanıcı {} id'li raporu {} id'li hakemine gönderdi.".format(
            current_user.username, rapor_id, hakem_id),
        "notification_receiver": person_id,
        "notification_title": _("Yeni Proje Rapor Değerlendirmesi"),
        "notification_message": _(
            "Yeni bir proje değerlendirmesi mevcut. Lütfen atanmış "
            "projeler bölümünden proje değerlendirmelerini kontrol ediniz.")
    }
    signal_sender(notification=True, **payload)


class StateChangePost:

    @staticmethod
    def genel_modal_post(form=None, proje_id=None, code=None):

        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.GenelForm(imd)
        template = None

        if genel_form.validate():
            try:
                ProjeStateDispacther.state_change(
                    params={'proje_id': proje_id},
                    next_app_state_code=code,
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form,
                                                            code=code)

        return template

    @staticmethod
    def p9_post(form=None, proje_id=None, code=None):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.GenelForm(imd)
        template = None

        if genel_form.validate():
            try:
                ProjeStateDispacther.state_change(
                    params={'proje_id': proje_id},
                    next_app_state_code=code,
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )
                proje = DB.session.query(Proje).filter(Proje.id == proje_id).first()
                proje.proje_basvuru_durumu = ProjeBasvuruDurumu.revizyon_bekleniyor
                DB.session.commit()

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form,
                                                            code=code)

        return template

    @staticmethod
    def p13_post(form=None, proje_id=None, code=None):

        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.P13(imd)
        template = None

        if genel_form.validate():
            try:
                ProjeStateDispacther.state_change(
                    params={'proje_id': proje_id},
                    next_app_state_code=code,
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form,
                                                            code=code)

        return template

    @staticmethod
    def p15_post(form=None, proje_id=None, code=None):

        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.P15(imd)
        template = None

        if genel_form.validate():
            rapor_id = genel_form.raporlar.data
            ara_rapor = DB.session.query(ProjeRapor).filter(ProjeRapor.proje_id == proje_id,
                                                            ProjeRapor.id == rapor_id,
                                                            ProjeRapor.rapor_tipi == ProjeRaporTipi.ara_rapor).one()
            ara_rapor.rapor_degerlendirme_durumu = genel_form.degerlendirme_sonucu.data

            try:
                ProjeStateDispacther.state_change(
                    params={'proje_id': proje_id},
                    next_app_state_code=code,
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form,
                                                            code=code)

        return template

    @staticmethod
    def p18_post(form=None, proje_id=None, code=None):

        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.P18(imd)
        template = None

        if genel_form.validate():
            try:
                ProjeStateDispacther.state_change(
                    params={'proje_id': proje_id},
                    next_app_state_code=code,
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form,
                                                            code=code)

        return template

    @staticmethod
    def p19_post(form=None, proje_id=None, code=None):

        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = DurumFormlari.P19(imd)
        template = None

        if genel_form.validate():
            rapor_id = genel_form.raporlar.data
            ara_rapor = DB.session.query(ProjeRapor).filter(ProjeRapor.proje_id == proje_id,
                                                            ProjeRapor.id == rapor_id,
                                                            ProjeRapor.rapor_tipi == ProjeRaporTipi.sonuc_raporu).one()
            ara_rapor.rapor_degerlendirme_durumu = genel_form.degerlendirme_sonucu.data

            try:
                ProjeStateDispacther.state_change(
                    params={'proje_id': proje_id},
                    next_app_state_code=code,
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form,
                                                            code=code)

        return template


class ActionPost:
    @staticmethod
    def pa1_post(form=None, proje_id=None, code='PA1'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA1(imd)
        template = None

        if genel_form.validate():
            try:
                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    description=genel_form.islem_adi.data,
                    action_code="PA1",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa2_post(form=None, proje_id=None, code='PA2'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA2(imd)
        template = None

        if genel_form.validate():
            try:

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA2",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )
                proje_notu = ProjeNot(
                    not_tipi=NotTipi.proje_notu,
                    notu_ekleyen_yetkili=current_user.id,
                    notu=genel_form.ozel_not.data,
                    proje_id=proje_id
                )

                DB.session.add(proje_notu)
                DB.session.commit()


            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa3_post(form=None, proje_id=None, code='PA3'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA3(imd)
        template = None

        if genel_form.validate():
            try:

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA3",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

                proje_notu = ProjeNot(
                    not_tipi=NotTipi.proje_yurutucu_notu,
                    notu_ekleyen_yetkili=current_user.id,
                    notu=genel_form.ozel_not.data,
                    proje_id=proje_id
                )

                DB.session.add(proje_notu)
                DB.session.commit()

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa6_post(form=None, proje_id=None, code='PA6'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA6(imd)
        template = None

        if genel_form.validate():
            try:
                proje_degerlendirme_rapor = DB.session.query(ProjeRapor).filter(
                    ProjeRapor.proje_id == proje_id,
                    ProjeRapor.rapor_tipi == ProjeRaporTipi.proje_basvuru).first()
                if not proje_degerlendirme_rapor:
                    proje_degerlendirme_rapor = ProjeRapor(rapor_tipi=ProjeRaporTipi.proje_basvuru,
                                                           proje_id=proje_id,
                                                           durumu=ProjeRaporDurumu.tamamlandi)
                    DB.session.add(proje_degerlendirme_rapor)
                    DB.session.flush()
                if genel_form.butun_hakemlere_gonderilsin_mi.data:
                    proje_hakemleri = DB.session.query(ProjeHakemleri).options(
                        joinedload(ProjeHakemleri.hakem).joinedload(Hakem.personel)
                    ).filter(
                        ProjeHakemleri.proje_id == proje_id,
                        ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi).all()
                    for proje_hakemi in proje_hakemleri:
                        # todo: daha once bu rapora iliskin degerlendrme hakeme gonderilmis ise ????
                        yeni_degerlendirme = ProjeDegerlendirmeleri(
                            proje_hakem_id=proje_hakemi.id,
                            rapor_id=proje_degerlendirme_rapor.id,
                            degerlendirme_gonderim_tarihi=datetime.now(),
                        )
                        DB.session.add(yeni_degerlendirme)
                        # ilgili proje hakemine notification gonderir
                        hakem_person_id = proje_hakemi.hakem.person_id if not proje_hakemi.hakem.personel else proje_hakemi.hakem.personel.person_id
                        hakem_degerlendirme_notification(proje_degerlendirme_rapor.id,
                                                         proje_hakemi.hakem_id,
                                                         hakem_person_id)

                else:
                    proje_hakemi = DB.session.query(ProjeHakemleri).options(
                        joinedload(ProjeHakemleri.hakem).joinedload(Hakem.personel)
                    ).filter(
                        ProjeHakemleri.proje_id == proje_id,
                        ProjeHakemleri.id == genel_form.hakemler.data).one()
                    yeni_degerlendirme = ProjeDegerlendirmeleri(
                        proje_hakem_id=genel_form.hakemler.data,
                        rapor_id=proje_degerlendirme_rapor.id,
                        degerlendirme_gonderim_tarihi=datetime.now()
                    )
                    DB.session.add(yeni_degerlendirme)

                    hakem_person_id = proje_hakemi.hakem.person_id if not proje_hakemi.hakem.personel else proje_hakemi.hakem.personel.person_id
                    # ilgili proje hakemine notification gonderir
                    hakem_degerlendirme_notification(proje_degerlendirme_rapor.id,
                                                     proje_hakemi.hakem_id,
                                                     hakem_person_id)
                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA6",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )
                DB.session.commit()
            except Exception as exc:
                DB.session.rollback()
                raise Exception(exc)
        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)
        return template

    @staticmethod
    def pa7_post(form=None, proje_id=None, code='PA7'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA7(imd)
        template = None

        if genel_form.validate():
            try:

                rapor_id = genel_form.raporlar.data
                if genel_form.butun_hakemlere_gonderilsin_mi.data:
                    proje_hakemleri = DB.session.query(ProjeHakemleri).options(
                        joinedload(ProjeHakemleri.hakem).joinedload(Hakem.personel)
                    ).filter(
                        ProjeHakemleri.proje_id == proje_id,
                        ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi).all()
                    for proje_hakemi in proje_hakemleri:
                        # todo: daha once bu rapora iliskin degerlendrme hakeme gonderilmis ise ????
                        yeni_degerlendirme = ProjeDegerlendirmeleri(
                            proje_hakem_id=proje_hakemi.id,
                            rapor_id=rapor_id)
                        DB.session.add(yeni_degerlendirme)
                        # ilgili proje hakemine notification gonderir
                        hakem_person_id = proje_hakemi.hakem.person_id if not proje_hakemi.hakem.personel else proje_hakemi.hakem.personel.person_id
                        hakem_degerlendirme_notification(rapor_id,
                                                         proje_hakemi.hakem_id,
                                                         hakem_person_id)

                else:
                    proje_hakemi = DB.session.query(ProjeHakemleri).options(
                        joinedload(ProjeHakemleri.hakem).joinedload(Hakem.personel)
                    ).filter(
                        ProjeHakemleri.proje_id == proje_id,
                        ProjeHakemleri.id == genel_form.hakemler.data).one()
                    yeni_degerlendirme = ProjeDegerlendirmeleri(
                        proje_hakem_id=genel_form.hakemler.data,
                        rapor_id=genel_form.raporlar.data)
                    DB.session.add(yeni_degerlendirme)

                    # ilgili proje hakemine notification gonderir
                    hakem_person_id = proje_hakemi.hakem.person_id if not proje_hakemi.hakem.personel else proje_hakemi.hakem.personel.person_id
                    hakem_degerlendirme_notification(rapor_id,
                                                     proje_hakemi.hakem_id,
                                                     hakem_person_id)
                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA7",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )
                DB.session.commit()
            except Exception as exc:
                DB.session.rollback()
                raise Exception(exc)
        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)
        return template

    @staticmethod
    def pa10_post(form=None, proje_id=None, code="PA10"):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA10(imd)
        template = None

        if genel_form.validate():
            try:

                proje_degerlendirme = DB.session.query(ProjeDegerlendirmeleri).filter_by(
                    id=genel_form.degerlendirmeler.data).first()

                proje_degerlendirme.degerlendirme_incelendi_mi = True

                DB.session.commit()

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA10",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa11_post(form=None, proje_id=None, code="PA11"):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA11(imd)
        template = None

        if genel_form.validate():
            try:

                proje_degerlendirme = DB.session.query(ProjeDegerlendirmeleri).filter_by(
                    id=genel_form.degerlendirmeler.data).first()

                proje_degerlendirme.degerlendirme_incelendi_mi = True

                DB.session.commit()

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA11",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa12_post(form=None, proje_id=None, code="PA12"):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA12(imd)
        template = None

        if genel_form.validate():
            try:

                bap_karar = BapGundem()
                bap_karar.proje_id = proje_id
                bap_karar.toplanti_id = genel_form.toplanti_tarihi.data
                bap_karar.karar = genel_form.karar.data
                bap_karar.tipi = genel_form.gundem_tipi.data
                bap_karar.karar_durum = genel_form.karar_durum.data
                bap_karar.gundem_sira_no = genel_form.karar_sira_no.data

                DB.session.add(bap_karar)
                DB.session.commit()

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA12",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa13_post(form=None, proje_id=None, code='PA13'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA13(imd)
        template = None

        if genel_form.validate():
            try:

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA13",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

                proje = proje_bilgisi(proje_id=proje_id)
                proje.klasor_sira_no = genel_form.klasor_sira_no.data
                DB.session.commit()

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa14_post(form=None, proje_id=None, code='PA14'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA14(imd)
        template = None

        if genel_form.validate():
            try:

                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA14",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

                proje = DB.session.query(Proje).filter(Proje.id == proje_id).first()
                if genel_form.proje_basligi.data:
                    proje.proje_basligi = genel_form.proje_basligi.data
                if genel_form.project_title.data:
                    proje.project_title = genel_form.project_title.data
                if genel_form.proje_no.data:
                    proje.proje_no = genel_form.proje_no.data

                DB.session.commit()

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa16_post(form=None, proje_id=None, code='PA16'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA16(imd)
        template = None

        if genel_form.validate():
            try:
                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA16",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )

                proje = proje_bilgisi(proje_id=proje_id)
                baslama_tarihi = genel_form.proje_baslangic_tarihi.data
                proje.kabul_edilen_baslama_tarihi = baslama_tarihi
                proje_suresi = genel_form.proje_suresi.data
                proje.proje_suresi = proje_suresi
                proje.proje_suresi_birimi = genel_form.proje_suresi_birimi.data
                bitis_tarihi = None
                if proje.proje_suresi_birimi == ProjeSuresiBirimi.ay:
                    bitis_tarihi = baslama_tarihi + timedelta(30*proje_suresi)
                elif proje.proje_suresi_birimi == ProjeSuresiBirimi.yil:
                    bitis_tarihi = baslama_tarihi + timedelta(365 * proje_suresi)
                elif proje.proje_suresi_birimi == ProjeSuresiBirimi.gun:
                    bitis_tarihi = baslama_tarihi + timedelta(proje_suresi)

                proje.bitis_tarihi = bitis_tarihi
                DB.session.commit()

            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa19_post(form=None, proje_id=None, code='PA19'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA19(imd)
        template = None

        if genel_form.validate():
            try:
                gundem = BapGundem()
                gundem.proje_id = proje_id
                gundem.sablon_id = genel_form.sablon_id.data if genel_form.sablon_id.data else None
                gundem.ek_dosya_id = genel_form.ek_dosya_id.data if genel_form.ek_dosya_id.data else None
                gundem.karar = genel_form.karar.data
                gundem.aciklama = genel_form.aciklama.data
                gundem.tipi = genel_form.tipi.data
                gundem.karar_durum = genel_form.karar_durum.data
                # gundem sira numarasini ayarlamak icin yazilan before_update event listeneri
                # calistirmak icin flush eklendi silinmeyecek
                DB.session.add(gundem)
                DB.session.flush()
                if genel_form.toplanti_tarihi.data:
                    gundem.toplanti_id = genel_form.toplanti_tarihi.data
                DB.session.commit()
                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA19",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )
            except Exception as exc:
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template

    @staticmethod
    def pa20_post(form=None, proje_id=None, code='PA20'):
        imd = ImmutableMultiDict([(element['name'], element['value']) for element in form])
        genel_form = IslemFormlari.PA20(imd)
        template = None
        if genel_form.validate():
            try:

                proje_kalemleri = DB.session.query(ProjeKalemi).filter(
                    ProjeKalemi.proje_id == proje_id).all()
                proje = DB.session.query(Proje).options(joinedload(Proje.gelir_kasasi)).filter(
                    Proje.id == proje_id).first()

                toplam_proje_butcesi = Decimal("0.00")
                for proje_kalemi in proje_kalemleri:
                    for form_proje_kalemi in genel_form.proje_kalemleri:
                        if proje_kalemi.id == form_proje_kalemi.proje_kalemi_id.data:
                            proje_kalemi.toplam_miktar = form_proje_kalemi.kabul_edilen_miktar.data
                            proje_kalemi.kabul_edilen_yil_1 = form_proje_kalemi.kabul_edilen_yil_1.data
                            proje_kalemi.kabul_edilen_yil_2 = form_proje_kalemi.kabul_edilen_yil_2.data
                            proje_kalemi.kabul_edilen_yil_3 = form_proje_kalemi.kabul_edilen_yil_3.data
                            proje_kalemi.toplam_butce = proje_kalemi.kabul_edilen_yil_1 + proje_kalemi.kabul_edilen_yil_2 + proje_kalemi.kabul_edilen_yil_3
                            toplam_proje_butcesi += proje_kalemi.toplam_butce

                toplam_proje_butcesi = toplam_proje_butcesi.quantize(Decimal(".01"))
                gelir_kasasi = proje.gelir_kasasi
                # gelir kasasina proje butcesi rezerv olarak eklenirken kasada kullanilabilir para
                # varmi kontrolu yapilir. (Kullanilabilir paranin proje butcesinden fazla olmasi
                # gerekir)
                gelir_kasasi_kullanilabilir_para = gelir_kasasi.toplam_para - gelir_kasasi.harcanan_para - gelir_kasasi.rezerv_para
                if not proje.kabul_edilen_butce:
                    if toplam_proje_butcesi > gelir_kasasi_kullanilabilir_para:
                        hata_mesaji = _(
                            "Projenin bağlı olduğu kasada ({}) yeterli kullanılabilir bütçe"
                            " bulunmamaktadır. Kullanılabilir bütçe {} Tl. Bu işlemi "
                            "yapabilmek için kasada en az {} Tl bulunmalıdır".format(
                                gelir_kasasi.adi,
                                gelir_kasasi_kullanilabilir_para,
                                toplam_proje_butcesi))

                        DB.session.rollback()
                        template = project_management_methods_get[code](proje_id=proje_id,
                                                                        form=genel_form)
                        return template, hata_mesaji
                    # eger ilk defa proje kabul edilen butcesi ekleniliyorsa toplam butce proje
                    # butcesi olarak yazilir
                    # projenin bagli oldugu gelir kasasindan toplam butce rezerv olarak kaydedilir
                    proje.kabul_edilen_butce = toplam_proje_butcesi
                    gelir_kasasi.rezerv_para += toplam_proje_butcesi
                    signal_payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "kabul_edilen_proje_butcesi_belirlendi").type_index,
                        "nesne": 'Proje',
                        "nesne_id": proje_id,
                        "ekstra_mesaj": "{} adlı kullanıcı {} id'li projenin kabul edilen bütçesini {} TL yaptı.".format(
                            current_user.username,
                            proje_id,
                            toplam_proje_butcesi
                        )
                    }
                    signal_sender(**signal_payload)
                else:
                    # daha once kabul edilen butce girilmis bir projeye kabul edilen butce
                    # degeri giriliyor ise daha once girilen ile şuan girilen arasindaki fark alinir
                    # bu fark (1000 - 900 = 100 yani 1000 lira yerine 900 lira kabul edildi)
                    # projenin bagli oldugu rezerv kasaya eklenir
                    kabul_edilen_butce_farki = toplam_proje_butcesi - proje.kabul_edilen_butce
                    if kabul_edilen_butce_farki > gelir_kasasi_kullanilabilir_para:
                        hata_mesaji = _(
                            "Projenin bağlı olduğu kasada ({}) yeterli kullanılabilir bütçe"
                            " bulunmamaktadır. Kullanılabilir bütçe {} Tl. Bu işlemi "
                            "yapabilmek için kasada en az {} Tl bulunmalıdır".format(
                                gelir_kasasi.adi,
                                gelir_kasasi_kullanilabilir_para,
                                kabul_edilen_butce_farki))

                        DB.session.rollback()
                        template = project_management_methods_get[code](proje_id=proje_id,
                                                                        form=genel_form)
                        return template, hata_mesaji
                    signal_payload = {
                        "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                            "kabul_edilen_proje_butcesi_belirlendi").type_index,
                        "nesne": 'Proje',
                        "nesne_id": proje_id,
                        "ekstra_mesaj": "{} adlı kullanıcı {} id'li projenin {} TL olan kabul edilen bütçesini {} TL olarak değiştirdi.".format(
                            current_user.username,
                            proje_id,
                            proje.kabul_edilen_butce,
                            toplam_proje_butcesi
                        )
                    }
                    signal_sender(**signal_payload)
                    proje.kabul_edilen_butce = toplam_proje_butcesi
                    gelir_kasasi.rezerv_para += kabul_edilen_butce_farki
                ProjeStateDispacther.do_action(
                    params={'proje_id': proje_id},
                    triggered_by=current_user.id,
                    proje_id=proje_id,
                    bap_yetkilisi_notu=genel_form.bap_admin_log.data,
                    action_code="PA20",
                    email_gonderilsin_mi=genel_form.email.data,
                    yurutucu_log=genel_form.yurutucu_log.data
                )
                DB.session.commit()
            except Exception as exc:
                DB.session.rollback()
                raise Exception(exc)

        else:
            template = project_management_methods_get[code](proje_id=proje_id, form=genel_form)

        return template


action_methods = {
    'PA1': ActionPost.pa1_post,
    'PA2': ActionPost.pa2_post,
    'PA3': ActionPost.pa3_post,
    # PA4 -> view
    # PA5 -> view
    'PA6': ActionPost.pa6_post,
    'PA7': ActionPost.pa7_post,
    # PA8 -> view
    # PA9 -> view
    'PA10': ActionPost.pa10_post,
    'PA11': ActionPost.pa11_post,
    # todo: kaldirilacakti demo dan dolayi pa19 a yonlendirildi.
    'PA12': ActionPost.pa19_post,
    'PA13': ActionPost.pa13_post,
    'PA14': ActionPost.pa14_post,
    # todo: view da yapilacak
    # PA15 -view,
    'PA16': ActionPost.pa16_post,
    # todo: goruntu icin
    'PA17': ActionPost.pa1_post,
    # todo: goruntu icin
    'PA18': ActionPost.pa1_post,
    'PA19': ActionPost.pa19_post,
    'PA20': ActionPost.pa20_post

}

state_change_methods = {
    'P2': StateChangePost.genel_modal_post,
    'P3': StateChangePost.genel_modal_post,
    'P4': StateChangePost.genel_modal_post,
    'P5': StateChangePost.genel_modal_post,
    'P6': StateChangePost.genel_modal_post,
    'P7': StateChangePost.genel_modal_post,
    'P8': StateChangePost.genel_modal_post,
    'P9': StateChangePost.p9_post,
    'P10': StateChangePost.genel_modal_post,
    'P11': StateChangePost.genel_modal_post,
    'P12': StateChangePost.genel_modal_post,
    'P13': StateChangePost.p13_post,
    'P14': StateChangePost.genel_modal_post,
    'P15': StateChangePost.p15_post,
    'P16': StateChangePost.genel_modal_post,
    'P17': StateChangePost.genel_modal_post,
    'P18': StateChangePost.p18_post,
    'P19': StateChangePost.p19_post,
    'P20': StateChangePost.genel_modal_post,
    'P21': StateChangePost.genel_modal_post,
    'P22': StateChangePost.genel_modal_post,
    'P23': StateChangePost.genel_modal_post,
    'P24': StateChangePost.genel_modal_post,
    'P25': StateChangePost.genel_modal_post,
    'P26': StateChangePost.genel_modal_post,
    'P27': StateChangePost.genel_modal_post,
    'P28': StateChangePost.genel_modal_post,
    'P29': StateChangePost.genel_modal_post,
    'P30': StateChangePost.genel_modal_post,
    'P31': StateChangePost.genel_modal_post,
    'P32': StateChangePost.genel_modal_post,
    'P33': StateChangePost.genel_modal_post
}

project_management_methods_post.update(state_change_methods)
project_management_methods_post.update(action_methods)
