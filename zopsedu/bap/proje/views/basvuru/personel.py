"""Proje Hakem Oneri view classları"""
from flask import request, current_app, jsonify, abort
from flask_classful import FlaskView, route
from flask_allows import And
from flask_babel import gettext as _
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, lazyload, load_only
from sqlalchemy.orm.exc import NoResultFound

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import ProjeCalisanlari, Personel, Ogrenci, Person, Ozgecmis
from zopsedu.auth.lib import auth, Permission
from zopsedu.bap.lib.auth import TamamlanmamisProjeBasvurusu, ProjeYurutucusu
from zopsedu.bap.proje.views.basvuru.common import personel_proje_calisani_mi
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class BasvuruPersonelView(FlaskView):
    """Basvuru Personel Kaydet View Class"""

    excluded_methods = ["ozgecmis_kaydet"]

    @staticmethod
    def ozgecmis_kaydet(ozgecmis_text, ozgecmis_file_id):
        """Proje calisanlarinin ozgecmislerini kaydeder. ozgecmis id doner"""
        calisan_ozgecmis = Ozgecmis(tecrube=ozgecmis_text,
                                    file_id=ozgecmis_file_id,
                                    user_id=current_user.id)
        DB.session.add(calisan_ozgecmis)
        DB.session.flush()
        return calisan_ozgecmis.id

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/arastirmaci-kaydet/', methods=['POST'])
    def arastirmaci_kaydet(self, proje_id):
        """
        Proje çalışanlarına araştırmacı kaydetmek için kullanılır
        """
        arastirmaci_data = request.get_json()
        personel_id = arastirmaci_data.get("personel_id")

        try:
            proje = DB.session.query(Proje).filter(Proje.id == proje_id).one()
            if proje.proje_yurutucu.personel.id == int(personel_id):
                return jsonify(status="error",
                               error_message=_(
                                   "Proje yürütücüsünü personel olarak ekleyemezsiniz")), 400

            try:
                personel = DB.session.query(Personel).options(
                    load_only("id", "person_id"),
                    lazyload(Personel.birimi),
                    lazyload(Personel.user),
                    joinedload(Personel.person).load_only("ad", "soyad")
                ).filter_by(id=personel_id).one()
            except NoResultFound as exc:
                DB.session.rollback()
                CustomErrorHandler.error_handler(
                    hata="Var olmayan bir personel id si ile projeye arastirmaci eklenmeye calışıldı. "
                         "Hata: {}, Proje id: {}".format(exc, proje_id)
                )
                return jsonify(status="error"), 400
            if personel_proje_calisani_mi(proje_id, personel_id):
                return jsonify(status="error",
                               error_message=_(
                                   "Eklemeye çalıştığınız personel zaten proje çalışanı.")), 400
            arastirmaci_ozgecmis_id = self.ozgecmis_kaydet(
                ozgecmis_text=arastirmaci_data.pop("ozgecmis_text", None),
                ozgecmis_file_id=arastirmaci_data.pop("ozgecmis_file_id", None))

            yeni_arastirmaci = ProjeCalisanlari(
                proje_id=proje_id,
                universite_disindan_mi=False,
                ozgecmis_id=arastirmaci_ozgecmis_id,
                **arastirmaci_data)
            personel_ad = personel.person.ad
            personel_soyad = personel.person.soyad
            DB.session.add(yeni_arastirmaci)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "projeye_arastirmaci_eklendi").type_index,
                "nesne": 'Proje Calisanlari',
                "nesne_id": yeni_arastirmaci.id,
                "etkilenen_nesne": "Personel",
                "etkilenen_nesne_id": personel.id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı personeli {} id'li projeye "
                                "araştırmacı olarak ekledi.".format(current_user.username,
                                                                    personel_ad,
                                                                    personel_soyad,
                                                                    proje_id)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success",
                           calisan={
                               "id": yeni_arastirmaci.id,
                               "ad": personel_ad,
                               "soyad": personel_soyad,
                               "gorevi": yeni_arastirmaci.projedeki_gorevi
                           })
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje idsi %s olan projeye arastirmaci atamaya"
                     "çalışılırken bir sorun oluştu. Hata: %s" % (proje_id, exc)
            )

        return jsonify(status="error"), 400

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/bursiyer-kaydet/', methods=['POST'])
    def bursiyer_kaydet(self, proje_id):
        """
        Proje çalışanlarına bursiyer kaydetmek için kullanılır
        """
        bursiyer_data = request.get_json()
        ogrenci_id = bursiyer_data.get("ogrenci_id")

        try:
            try:
                ogrenci = DB.session.query(Ogrenci).options(
                    load_only("id", "person_id"),
                    lazyload(Ogrenci.user),
                    joinedload(Ogrenci.person).load_only("ad", "soyad")
                ).filter_by(id=ogrenci_id).one()
            except NoResultFound as exc:
                CustomErrorHandler.error_handler(
                    hata="Var olmayan bir öğrenci id si ile projeye bursiyer eklenmeye calışıldı. "
                         "Hata: {}, Proje id: {}".format(proje_id, exc)
                )

                return jsonify(status="error"), 400
            bursiyer_calisan = DB.session.query(ProjeCalisanlari.id).filter(
                ProjeCalisanlari.ogrenci_id == ogrenci_id,
                ProjeCalisanlari.proje_id == proje_id).scalar()
            if bursiyer_calisan:
                return jsonify(status="error",
                               error_message=_(
                                   "Eklemeye çalıştığınız öğrenci zaten proje çalışanı.")), 400

            bursiyer_ozgecmis_id = self.ozgecmis_kaydet(
                ozgecmis_text=bursiyer_data.pop("ozgecmis_text", None),
                ozgecmis_file_id=bursiyer_data.pop("ozgecmis_file_id", None))

            yeni_bursiyer = ProjeCalisanlari(
                proje_id=proje_id,
                universite_disindan_mi=False,
                ozgecmis_id=bursiyer_ozgecmis_id,
                **bursiyer_data)
            ogrenci_ad = ogrenci.person.ad
            ogrenci_soyad = ogrenci.person.soyad
            DB.session.add(yeni_bursiyer)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "projeye_bursiyer_eklendi").type_index,
                "nesne": 'Proje Calisanlari',
                "nesne_id": yeni_bursiyer.id,
                "etkilenen_nesne": "Proje",
                "etkilenen_nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı öğrenciyi bursiyer olarak "
                                "ekledi.".format(current_user.username,
                                                 ogrenci_ad,
                                                 ogrenci_soyad)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success",
                           calisan={
                               "id": yeni_bursiyer.id,
                               "ad": ogrenci_ad,
                               "soyad": ogrenci_soyad,
                               "gorevi": yeni_bursiyer.projedeki_gorevi
                           })
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje idsi %s olan projeye bursiyer atamaya"
                     "çalışılırken bir sorun oluştu. Hata: %s" % (proje_id, exc)
            )

        return jsonify(status="error"), 400

    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/harici-arastirmaci-kaydet/', methods=['POST'])
    def harici_arastirmaci_kaydet(self, proje_id):
        """
        Proje çalışanlarına üniversite dışı araştırmacı kaydetmek için kullanılır.
        """
        harici_arastirmaci_data = request.get_json()
        adi = harici_arastirmaci_data.pop("ad")
        soyad = harici_arastirmaci_data.pop("soyad")
        email = harici_arastirmaci_data.pop("email")

        try:

            yeni_person = Person(ad=adi,
                                 soyad=soyad,
                                 birincil_eposta=email)
            DB.session.add(yeni_person)
            DB.session.flush()

            harici_arastirmaci_ozgecmis_id = self.ozgecmis_kaydet(
                ozgecmis_text=harici_arastirmaci_data.pop("ozgecmis_text", None),
                ozgecmis_file_id=harici_arastirmaci_data.pop("ozgecmis_file_id", None))

            yeni_harici_arastirmaci = ProjeCalisanlari(
                proje_id=proje_id,
                ozgecmis_id=harici_arastirmaci_ozgecmis_id,
                person_id=yeni_person.id,
                **harici_arastirmaci_data)
            DB.session.add(yeni_harici_arastirmaci)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "projeye_harici_arastirmaci_eklendi").type_index,
                "nesne": 'Proje Calisanlari',
                "nesne_id": yeni_harici_arastirmaci.id,
                "etkilenen_nesne": "Proje",
                "etkilenen_nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı kisiyi üniversite dışı arastırmacı "
                                "olarak kaydetti.".format(current_user.username,
                                                          adi,
                                                          soyad)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success",
                           calisan={
                               "id": yeni_harici_arastirmaci.id,
                               "ad": adi,
                               "soyad": soyad,
                               "gorevi": yeni_harici_arastirmaci.projedeki_gorevi
                           })
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje idsi %s olan projeye harici araştırmacı atamaya"
                     "çalışılırken bir sorun oluştu. Hata: %s" % (proje_id, exc)
            )

        return jsonify(status="error"), 400

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/calisan-sil/<int:calisan_id>', methods=['DELETE'])
    def proje_calisani_sil(proje_id, calisan_id):
        """
        Daha önce projeye kaydedilmiş çalışanı siler.
        """
        try:
            try:
                silinecek_calisan = DB.session.query(ProjeCalisanlari).filter_by(
                    id=calisan_id, proje_id=proje_id).one()
            except NoResultFound as exc:
                DB.session.rollback()
                CustomErrorHandler.error_handler(
                    hata="Var olmayan bir id ile proje çalışanı silinmeye "
                         "çalışıldı. Proje id: {}, Hata: {}".format(proje_id, exc)
                )
                return jsonify(status="error"), 400

            DB.session.delete(silinecek_calisan)
            if silinecek_calisan.person:
                DB.session.delete(silinecek_calisan.person)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                    "proje_calisani_sil").type_index,
                "nesne": 'Proje Calisanlari',
                "nesne_id": calisan_id,
                "etkilenen_nesne": "Proje",
                "etkilenen_nesne_id": proje_id,
                "ekstra_mesaj": "{} adlı kullanıcı, proje çalışanını projeden sildi.".format(
                    current_user.username)
            }
            signal_sender(**signal_payload)
            return jsonify(status="success")
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje çalışanı silinmeye çalışırken hata ile karşılaşıldı. "
                     "Proje id: {}, Calisan id: {}, Hata: {}".format(proje_id, calisan_id, exc)
            )
        return jsonify(status="error"), 400

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/calisan/<int:calisan_id>', methods=['GET'])
    def get_proje_calisani(proje_id, calisan_id):
        """
        Var olan bir çalışanı almak için kullanılır.
        """
        try:
            try:
                calisan = DB.session.query(ProjeCalisanlari).options(
                    lazyload(ProjeCalisanlari.ogrenci),
                    lazyload(ProjeCalisanlari.personel),
                    joinedload(ProjeCalisanlari.person).load_only("ad", "soyad"),
                    joinedload(ProjeCalisanlari.fakulte).load_only("ad"),
                    joinedload(ProjeCalisanlari.bolum).load_only("ad"),
                    joinedload(ProjeCalisanlari.hitap_unvan).load_only("ad", "kod")
                ).filter_by(id=calisan_id,
                            proje_id=proje_id).one()
            except NoResultFound as exc:
                CustomErrorHandler.error_handler(
                    hata="Var olmayan bir id ile proje çalışanı alınmaya "
                         "çalışıldı. Proje id: {}, Hata: {}".format(proje_id, exc))
                return abort(404)
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje çalışanı silinmeye çalışırken hata ile karşılaşıldı. "
                     "Proje id: {}, Calisan id: {}, Hata: {}".format(proje_id, calisan_id, exc))
            return abort(400)
        data = calisan.to_dict()
        data["projeye_katkisi"] = float(
            calisan.projeye_katkisi) if calisan.projeye_katkisi else float(0)

        data.update({
            "ozgecmis_text": calisan.ozgecmis.tecrube,
            "ozgecmis_file_id": calisan.ozgecmis.file_id
        })
        if calisan.person:
            hitap_unvan_ad = ""
            if calisan.hitap_unvan:
                hitap_unvan_ad = "{} {}".format(
                    calisan.hitap_unvan.kod,
                    calisan.hitap_unvan.ad if calisan.hitap_unvan else ""
                )

            data.update({
                "hitap_unvan_ad": hitap_unvan_ad,
                "fakulte_ad": calisan.fakulte.ad if calisan.fakulte else "",
                "bolum_ad": calisan.bolum.ad if calisan.bolum else "",
                "ad": calisan.person.ad,
                "soyad": calisan.person.soyad,
            })
        return jsonify(status="success", calisan=data)

    @staticmethod
    @login_required
    @auth.requires(
        And(Permission(*permission_dict["bap"]["proje"]["basvuru"]["proje_basvurusu_yapma"]),
            ProjeYurutucusu(), TamamlanmamisProjeBasvurusu()))
    @route('/<int:proje_id>/calisan/<int:calisan_id>', methods=['POST'])
    def calisan_guncelle(proje_id, calisan_id):
        """
        Çalışan güncellemek için kullanılır.
        """
        calisan_data = request.get_json()
        try:
            try:
                calisan = DB.session.query(ProjeCalisanlari).filter_by(
                    id=calisan_id, proje_id=proje_id).one()
            except NoResultFound as exc:
                CustomErrorHandler.error_handler(
                    hata="Var olmayan bir id ile proje çalışanı alınmaya "
                         "çalışıldı. Proje id: {}, Hata: {}".format(proje_id, exc))
                return abort(404)
            if calisan.person_id:
                calisan.person.ad = calisan_data.get("ad")
                calisan.person.soyad = calisan_data.get("soyad")
            # todo: calisan guncellenirken ozgecmisinde bir degisklik var ise guncelle.
            calisan.ozgecmis.tecrube = calisan_data.pop("ozgecmis_text", None)
            calisan.ozgecmis.file_id = calisan_data.pop("ozgecmis_file_id", None)
            calisan.update_obj_data(calisan_data)
            DB.session.commit()
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Proje çalışanı silinmeye çalışırken hata ile karşılaşıldı. "
                     "Proje id: {}, Calisan id: {}, Hata: {}".format(proje_id, calisan_id, exc))
            return abort(400)
        data = {
            "id": calisan.id,
            "gorevi": calisan.projedeki_gorevi
        }
        if calisan.person_id:
            data.update({
                "ad": calisan.person.ad,
                "soyad": calisan.person.soyad
            })
        elif calisan.personel_id:
            data.update({
                "ad": calisan.personel.person.ad,
                "soyad": calisan.personel.person.soyad
            })
        else:
            data.update({
                "ad": calisan.ogrenci.person.ad,
                "soyad": calisan.ogrenci.person.soyad
            })
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("bap").get(
                "proje_calisan_guncelle").type_index,
            "nesne": 'Proje Calisanlari',
            "nesne_id": calisan_id,
            "etkilenen_nesne": "Proje",
            "etkilenen_nesne_id": proje_id,
            "ekstra_mesaj": "{} adlı kullanıcı, {} {} adlı proje çalışanının bilgilerini "
                            "güncelledi.".format(current_user.username,
                                                 data["ad"],
                                                 data["soyad"])
        }
        signal_sender(**signal_payload)
        return jsonify(status="success",
                       calisan=data)
