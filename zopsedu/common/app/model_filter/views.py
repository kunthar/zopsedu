"""Select2 İçin Gerekli Filtleremeleri Yapmak İçin Kullanılır"""
import operator
from datetime import datetime

from flask_allows import Or
from flask_login import login_required
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import load_only, joinedload
from flask import request, jsonify, current_app
from flask_classful import FlaskView, route

from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.detayli_hesap_planlari import DetayliHesapPlanlari
from zopsedu.bap.models.gelir_kasasi import GelirKasasi
from zopsedu.lib.db import DB
from zopsedu.models import Personel, Birim, BAPBelge, Person, HitapUnvan, Ogrenci, OgretimElemani, \
    VergiDairesi
from zopsedu.lib.sessions import SessionHandler
from zopsedu.models.helpers import BirimTipiEnum
from zopsedu.personel.models.hakem import Hakem
from zopsedu.app import app

SELECT2_PAGE_SIZE = 20


# todo: izinlerin tamamı kontrol edilecek.
class FilterView(FlaskView):
    """
    Filter View
    """
    route_base = "/select"

    excluded_methods = [
        "query_data",
        "initial_val",
        "get_paginated_query_data_and_number_of_row",
        "check_request_params",
        "prepare_response",
    ]

    def __init__(self):
        with app.app_context():
            current_app.logger.info("asdfasffasfdsa")

    @property
    def query_data(self):
        """request form query"""
        return request.form.get("q")

    @property
    def initial_val(self):
        """request form initial_val"""
        return request.form.get("initial_val")

    @login_required
    @route('/personel', methods=["POST"], endpoint='select.personel.arama')
    @auth.requires(Permission(*permission_dict["common"]["app"]["modal_filter"]["personel_arama"]))
    def filter_personel(self):
        """
        select2 tarafından query_param olarak gönderilen "q" değişkeni alınıp personel tablosunda
        "ad" ve "soyad" fieldlarında arama yapılır. "q" değişkeni ile başlayan "ad" veya "soyad"
        varsa gerekli degerler return edilir
        Returns:
            {
                "items": [{ "id":1, "text": "Ad1 Soyad1"},...],
                "total_count": number_of_total_row,
            }

        """

        self.check_request_params()

        query = DB.session.query(
            Personel
        ).join(
            Person,
            Personel.person_id == Person.id
        ).join(HitapUnvan, HitapUnvan.id == Personel.unvan).add_columns(
            Personel.id, Person.ad.label("ad"), Person.soyad.label("soyad"),
            HitapUnvan.ad.label("hitap_unvan")
        )

        if self.query_data:
            query = query.filter(or_(Person.ad.ilike(self.query_data + "%"),
                                     Person.soyad.ilike(self.query_data + "%")))
        else:
            query = query.filter(Person.id == self.initial_val)

        return self.prepare_response(query, text_field=["ad", "soyad", "hitap_unvan"],
                                     text_format="{} {} - {}")

    @login_required
    @route('/universite', methods=["POST"], endpoint="select.universite.arama")
    @auth.requires(
        Permission(*permission_dict["common"]["app"]["modal_filter"]["universite_arama"]))
    def filter_universite(self):
        """
         select2 tarafından query_param olarak gönderilen "q" değişkeni alınıp birim tablosunda
        universite isimleri arasinda filtre edilir ve seçilen universitenin birim id si doner
        varsa gerekli degerler return edilir
        :return:
        """

        query = DB.session.query(Birim).filter(Birim.birim_tipi == "Üniversite").options(
            load_only("id", "uzun_ad"))

        if self.query_data:
            filter_param = or_(Birim.ad.ilike("%" + self.query_data + "%"),
                               Birim.uzun_ad.ilike("%" + self.query_data + "%"))
            query = query.filter(filter_param)
        else:
            query = query.filter(Birim.id == self.initial_val)

        return self.prepare_response(query)

    @login_required
    @route('/birim', methods=["POST"], endpoint='select.birim.arama')
    @auth.requires(Permission(*permission_dict["common"]["app"]["modal_filter"]["birim_arama"]))
    def filter_birim(self):
        """

        select2 tarafından query_param olarak gönderilen "q" değişkeni alınıp birim tablosunda
        "ad" ve "uzun_ad" fieldlarında arama yapılır. "q" değişkeni içeren "ad" veya "uzun_ad"
        varsa gerekli degerler return edilir
        Returns:
            {
                "items": [{ "id":1, "text": "İktisat"},...],
                "total_count": number_of_total_row,
            }

        """
        self.check_request_params()
        ust_birim_id = request.form.get("dependant_value")

        kurum_ici = request.form.get("kurum_ici")

        birim_tipi = request.form.get("birim_tipi")

        query = DB.session.query(Birim).options(load_only("id", "uzun_ad"))

        if self.query_data:
            filter_param = or_(Birim.ad.ilike("%" + self.query_data + "%"),
                               Birim.uzun_ad.ilike("%" + self.query_data + "%"))

            if kurum_ici == 'true':
                universite_id = SessionHandler.universite_id()
                if birim_tipi == BirimTipiEnum.fakulte.value:
                    ust_birim_id = universite_id

            if ust_birim_id:
                filter_param = and_(filter_param, Birim.ust_birim_id == ust_birim_id)

            if birim_tipi:
                filter_param = and_(filter_param, Birim.birim_tipi == birim_tipi)

            query = query.filter(filter_param)

        else:
            query = query.filter(Birim.id == self.initial_val)

        return self.prepare_response(query)

    @login_required
    @route('/bap_belge', methods=["POST"], endpoint='select.bap_belge.arama')
    @auth.requires(Permission(*permission_dict["common"]["app"]["modal_filter"]["belge_arama"]))
    def filter_bap_belge(self):
        """

        Returns:

        """
        self.check_request_params()

        query = DB.session.query(BAPBelge).options(load_only("id", "adi", "aciklama"))

        if self.query_data:
            query = query.filter(BAPBelge.adi.ilike(self.query_data + "%"))
        else:
            query = query.filter(BAPBelge.id == self.initial_val)

        return self.prepare_response(query, text_field=["adi", "aciklama"],
                                     text_format="{}\n{}")

    @login_required
    @route('/hakem', methods=["POST"], endpoint='select.hakem.arama')
    @auth.requires(Permission(*permission_dict["common"]["app"]["modal_filter"]["hakem_arama"]))
    def filter_hakem(self):
        """
        Hakem Filtrelemek için kullanılır
        """
        self.check_request_params()

        query = DB.session.query(Hakem).join(
            Hakem.person
        ).options(
            load_only('unvan', 'hakem_turu'),
            joinedload(Hakem.person).load_only('ad', 'soyad'),
            joinedload(Hakem.personel))

        if self.query_data:
            query = query.filter(or_(Person.ad.ilike('%' + self.query_data.strip() + '%'),
                                     Person.soyad.ilike('%' + self.query_data.strip() + '%')))
        else:
            query = query.filter(Person.ad.ilike('%' + self.initial_val.strip() + '%'))

        return self.prepare_response(query,
                                     text_field=["unvan", "person.ad", "person.soyad",
                                                 "universite.ad"])

    @login_required
    @route('/hitap_unvan', methods=["POST"])
    @auth.requires(
        Permission(*permission_dict["common"]["app"]["modal_filter"]["hitap_unvan_arama"]))
    def filter_hitap_unvan(self):
        """
        HitapUnvan Filtrelemek için kullanılır
        """
        self.check_request_params()

        query = DB.session.query(HitapUnvan).options(load_only("id", "ad", "kod"))

        if self.query_data:
            query = query.filter(HitapUnvan.ad.ilike("%" + self.query_data.upper() + "%"))
        else:
            query = query.filter(HitapUnvan.id == self.initial_val)

        return self.prepare_response(query, text_field=["ad", "kod"])

    @login_required
    @route('/ogrenci', methods=["POST"])
    @auth.requires(Permission(*permission_dict["common"]["app"]["modal_filter"]["ogrenci_arama"]))
    def filter_ogrenci(self):
        """
        select2 tarafından query_param olarak gönderilen "q" değişkeni alınıp ogrenci tablosunda
        "ad" ve "soyad" fieldlarında arama yapılır. "q" değişkeni ile başlayan "ad" veya "soyad"
        varsa gerekli degerler return edilir
        Returns:
            {
                "items": [{ "id":1, "text": "Ad1 Soyad1"},...],
                "total_count": number_of_total_row,
            }

        """
        self.check_request_params()

        query = DB.session.query(Ogrenci).join(Person, Ogrenci.person_id == Person.id). \
            add_columns(Ogrenci.id, Person.ad, Person.soyad)

        if self.query_data:
            query = query.filter(or_(Person.ad.ilike("%" + self.query_data + "%"),
                                     Person.soyad.ilike("%" + self.query_data + "%")))
        else:
            query = query.filter(Person.id == self.initial_val)

        return self.prepare_response(query, text_field=["ad", "soyad"], text_format="{} {}")

    @login_required
    @route('/ogretim-uyesi', methods=["POST"])
    @auth.requires(
        Permission(*permission_dict["common"]["app"]["modal_filter"]["ogretim_uyesi_arama"]))
    def filter_ogretim_uyesi(self):
        """
        select2 tarafından query_param olarak gönderilen "q" değişkeni alınıp ogretim elamani
        tablosunda üzerinden person tablosunun
        "ad" ve "soyad" fieldlarında arama yapılır. "q" değişkeni ile başlayan "ad" veya "soyad"
        varsa gerekli degerler return edilir
        Returns:
            {
                "items": [{ "id":1, "text": "Ad1 Soyad1"},...],
                "total_count": number_of_total_row,
            }

        """
        self.check_request_params()

        query = DB.session.query(OgretimElemani).join(
            Personel, OgretimElemani.personel_id == Personel.id).join(
            Person, Personel.person_id == Person.id).add_columns(
            OgretimElemani.id, Person.ad, Person.soyad)

        if self.query_data:
            query = query.filter(or_(Person.ad.ilike("%" + self.query_data + "%"),
                                     Person.soyad.ilike("%" + self.query_data + "%"), ))
        else:
            query = query.filter(Person.id == self.initial_val)

        return self.prepare_response(query, text_field=["ad", "soyad"], text_format="{} {}")

    @route('/vergi-dairesi', methods=["POST"], endpoint='select.vergi_dairesi.arama')
    @auth.requires(
        Or(Permission(*permission_dict["common"]["app"]["modal_filter"]["vergi_dairesi_arama"]),
           Role("anonymous")))
    def filter_vergi_dairesi(self):
        """
        select2 tarafından query_param olarak gönderilen "q" değişkeni alınıp vergi dairesi
        tablosunda "kodu", "adi" ve "il" fieldlarında arama yapılır. "q" değişkeni içeren "adi" ve "kodu"
        varsa gerekli degerler return edilir
        Returns:
            {
                "items": [{ "id":1, "text": "urla vergi dairesi"},...],
                "total_count": number_of_total_row,
            }

        """
        self.check_request_params()

        query = DB.session.query(VergiDairesi)

        if self.query_data:
            query = query.filter(or_(VergiDairesi.kodu.ilike("%" + self.query_data + "%"),
                                     VergiDairesi.adi.ilike("%" + self.query_data + "%"),
                                     VergiDairesi.il.ilike("%" + self.query_data + "%")))
        else:
            query = query.filter(VergiDairesi.id == self.initial_val)

        return self.prepare_response(query, text_field=["adi", "kodu"], text_format="{} - {}")


    @route('/detayli-hesap-kodu', methods=["POST"], endpoint='select.detayli_hesap_plani.arama')
    @auth.requires(
        Permission(*permission_dict["common"]["app"]["modal_filter"]["detayli_hesap_kodu_arama"]))
    def filter_detayli_hesap_plani(self):
        """
        detayli hesap plani modelinde "hesap_kodu" ve "ana_hesap_hesap_grubu_yardimci_hesap_adi"
        alanlarinda arama yapar
        """
        self.check_request_params()

        query = DB.session.query(DetayliHesapPlanlari)

        if self.query_data:
            query = query.filter(
                or_(DetayliHesapPlanlari.hesap_kodu.ilike("%" + self.query_data + "%"),
                    DetayliHesapPlanlari.ana_hesap_hesap_grubu_yardimci_hesap_adi.ilike(
                        "%" + self.query_data + "%")))
        else:
            query = query.filter(DetayliHesapPlanlari.id == self.initial_val)

        return self.prepare_response(query, text_field=["hesap_kodu",
                                                        "ana_hesap_hesap_grubu_yardimci_hesap_adi"],
                                     text_format="{} - {}")

    @login_required
    @route('/gelir-kasasi', methods=["POST"], endpoint='select.gelir_kasasi.arama')
    @auth.requires(
        Permission(*permission_dict["common"]["app"]["modal_filter"]["gelir_kasasi_arama"]))
    def filter_gelir_kasasi(self):
        """
        Güncel gelir kasalari arasinda arama yapar.
        """
        self.check_request_params()

        query = DB.session.query(GelirKasasi)

        if self.query_data:
            query = query.filter(GelirKasasi.adi.ilike("%" + self.query_data + "%"),
                                 GelirKasasi.mali_yil == datetime.now().year)
        else:
            query = query.filter(GelirKasasi.id == self.initial_val)

        return self.prepare_response(query, text_field=["adi"], text_format="{}")

    # pylint: disable=invalid-name
    @staticmethod
    def get_paginated_query_data_and_number_of_row(query):
        """

        Args:
            query: query

        Returns:    query_result(list_model_instance), number_of_row(int)

        """
        page = int(request.form.get("page", 1))
        page_size = int(request.form.get("page_size", SELECT2_PAGE_SIZE))

        count_query = query.statement.with_only_columns([func.count()])
        number_of_row = DB.session.execute(count_query).scalar()

        query_result = query.limit(page_size).offset((page - 1) * page_size).all()
        return query_result, number_of_row
        # pylint: enable=invalid-name

    def check_request_params(self):  # pylint: disable=inconsistent-return-statements
        """
        Check request params and returns empty result if both q and initial_data aren't given.

        Returns:
            Empty result

        """

        if not (self.query_data or self.initial_val):
            return jsonify({"results": []})

    def prepare_response(self, query, id_field="id", text_field=None, text_format=None):
        """

        Args:
            query:
            id_field:
            text_field:
            text_format:

        Returns:

        """

        if not text_field:
            text_field = ["ad"]

        if isinstance(text_field, str):
            text_field = [text_field]

        text = operator.attrgetter(*text_field)
        text_field_number = len(text_field)

        if not text_format:
            text_format = "{} - " * text_field_number

        def format_text(item):
            """

            Args:
                item: query result item

            Returns:
                (str) formatted text

            """

            item_vals = text(item)
            item_vals = list(item_vals) if isinstance(item_vals, tuple) else [item_vals]
            return text_format.format(*item_vals).rstrip('- ')

        items, number_of_row = self.get_paginated_query_data_and_number_of_row(query)
        data = [
            {
                "id": getattr(item, id_field),
                "text": format_text(item)
            } for item in items
        ]

        return jsonify({
            "items": data,
            "total_count": number_of_row
        })
