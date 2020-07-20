"""Şablon Ayarlari Modulu"""
from flask import render_template, request, flash, jsonify, render_template_string
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import desc

from zopsedu.auth.lib import auth, Permission
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models import Sablon, File, SablonTipi, QueryHelper
from zopsedu.yonetim.bap_yonetimi.forms.belge_sablonlari import VarsayilanSablonYuklemeForm, SablonSearchForm


class SablonlarView(FlaskView):
    """Sablon ayarları view classi"""
    excluded_methods = ['form', 'bap_sablon_types', 'bap_query_helpers', 'qry']

    @property
    def qry(self):
        """
        Sablon ve ilgili alanlari icin query nesnesi olustur.
        Returns:
        """
        return DB.session.query(Sablon.adi.label("sablon_adi"),
                                Sablon.id.label("sablon_id"),
                                Sablon.updated_at.label("sablon_update_tarihi"),
                                SablonTipi.adi.label("sablon_tipi_adi"),
                                Sablon.ebys_icin_kullanilabilir_mi.label("eby_icin_kullanilabilir_mi"),
                                Sablon.kullanilabilir_mi.label("kullanilabilir_mi")). \
            join(SablonTipi,
                 Sablon.sablon_tipi_id == SablonTipi.id)


    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.sablon_tipi_adi,
            r.sablon_adi,
            'Evet' if r.kullanilabilir_mi else 'Hayır',
            '{:%d.%m.%Y}'.format(r.sablon_update_tarihi),
            render_template_string("""
                <a href="#sablon-onizleme-modal">
                    <button class="btn btn-success" onclick="previewAction({{ sablon_id }});">
                        {{ _('Ön İzle') }}
                    </button>
                </a>
            """, sablon_id=r.sablon_id),
            render_template_string("""
                <a href="#bap-sablon-modal"
                    onclick="getSablonData(this)"
                    data-toggle="modal"
                    data-target="#bap-sablon-modal"
                    data-sablon-id="{{ sablon_id }}">
                    <span class="float-left detail_edit fa ft-edit fa-2x m-l-10"></span>
                </a>
            """, sablon_id=r.sablon_id)

        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @staticmethod
    def bap_sablon_types():
        """
        Bap şablon tiplerini getirir
        """
        bap_sablon_tipleri = DB.session.query(
            SablonTipi.id,
            SablonTipi.adi
        ).filter(SablonTipi.module_name == "BAP").all()
        return bap_sablon_tipleri

    @staticmethod
    def bap_query_helpers():
        """
        Bap query helperlarini getirir.
        bap_query_helpers --> List of set [(id, func_name, arg_list),]
        """
        bap_query_helpers = DB.session.query(
            QueryHelper.id,
            QueryHelper.function_name,
            QueryHelper.function_arg_list
        ).filter(QueryHelper.module_name == "BAP").all()
        return [(helper[0], "{}({})".format(helper[1], ",".join(helper[2]))) for helper in
                bap_query_helpers]

    def form(self):
        """
        Sablon formunu initialize eder.
        """
        bap_sablon_form = VarsayilanSablonYuklemeForm(request.form)
        bap_sablon_types = self.bap_sablon_types()
        bap_sablon_form.sablon_tipi_id.choices = bap_sablon_types
        bap_sablon_form.sablon_tipi_id.default = bap_sablon_types[0]
        bap_query_helpers = self.bap_query_helpers()
        bap_sablon_form.query_helper_id.choices = bap_query_helpers
        bap_sablon_form.query_helper_id.default = bap_query_helpers[0]
        return bap_sablon_form

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["sablon_ayarlari"]))
    @route('/<int:sablon_id>/sablon', methods=['GET'])
    def get_bap_sablon(sablon_id):
        # todo: hata yakalayıp ona gore deger don
        """Belirli bir bap sablon getirir"""
        # tipi duyuru, birim tipi bap olan duyuruyu getirir
        sablon = DB.session.query(Sablon).filter(Sablon.id == sablon_id).one()

        sablon_data = {
            "sablon_adi": sablon.adi,
            "kullanilabilir_mi": sablon.kullanilabilir_mi,
            "sablon_text": sablon.sablon_text,
            "query_id": sablon.query_id
        }

        return jsonify(status="success", sablon_data=sablon_data)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["sablon_ayarlari"]))
    @route('/<int:sablon_id>/guncelle', methods=['POST'])
    def bap_sablon_guncelle(sablon_id):
        """Belirli bir bap sablonu gunceller"""
        sablon_data = request.get_json()
        sablon_formu = VarsayilanSablonYuklemeForm(**sablon_data)

        sablon = DB.session.query(Sablon).filter(Sablon.id == sablon_id).one()

        sablon.adi = sablon_formu.sablon_adi.data
        sablon.query_id = sablon_formu.query_helper_id.data
        sablon.kullanilabilir_mi = sablon_formu.sablon_kullanilabilir_mi.data
        if not sablon.file and sablon_formu.sablon_text.data:
            sablon.sablon_text = sablon_formu.sablon_text.data

        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("ayarlar").get(
                "bap_sablon_guncelle").type_index,
            "nesne": 'Sablon',
            "nesne_id": sablon.id,
            "ekstra_mesaj": "{} adli user, {} id'li bap sablon guncelledi.".format(
                current_user.username,
                sablon.id)
        }
        signal_sender(**signal_payload)

        return jsonify(status="success")

    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["sablon_ayarlari"]),
                   menu_registry={'path': '.yonetim.bap.varsayilan_sablonlar',
                                  'title': _("Şablon Yönetimi"),
                                  "order": 10})
    @route('/varsayilan-sablonlar', methods=['GET'])
    def belge_sablonlari(self):
        """
        Varsayilan belge sablonlari yukleme ekrani

        """
        form = self.form()
        sablon_search_form = SablonSearchForm()

        return render_template("varsayilan_sablonlar.html", sablon_form=form, sablon_search_form=sablon_search_form)

    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["sablon_ayarlari"]))
    @route('/varsayilan-sablonlar', methods=['POST'])
    def post_belge_sablonlari(self):
        """
        Varsayilan belge sablonlari yukleme ekrani

        """
        form = self.form()
        sablon_dosya = request.files.get(form.sablon_dosya.name, None)
        sablon_text = form.sablon_text.data
        if not sablon_text and not sablon_dosya:
            flash(_("Dosya yüklemelisiniz veya şablon metni girmelisiniz"))
        elif sablon_text and sablon_dosya:
            flash(_("Aynı anda dosya yükleyip şablon metni giremezsiniz."))
        else:
            if form.validate():
                sablon_tipi_id = form.sablon_tipi_id.data
                sablon_adi = form.sablon_adi.data
                kullanilabilir_mi = form.sablon_kullanilabilir_mi.data
                query_helper_id = form.query_helper_id.data
                sablon_dosya_id = None
                if sablon_dosya:
                    _sablon = File(content=sablon_dosya)
                    DB.session.add(_sablon)
                    DB.session.flush()
                    sablon_dosya_id = _sablon.id

                sablon = Sablon(
                    file=sablon_dosya_id,
                    sablon_tipi_id=sablon_tipi_id,
                    sablon_text=sablon_text or "",
                    module_name="BAP",
                    adi=sablon_adi,
                    kullanilabilir_mi=kullanilabilir_mi,
                    query_id=query_helper_id
                )

                DB.session.add(sablon)
                DB.session.commit()
                flash("Belge Şablonu başarıyla yüklenmiştir.")
                form = self.form()
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("ayarlar").get(
                        "bap_sablon_kaydet").type_index,
                    "nesne": 'Sablon',
                    "nesne_id": sablon.id,
                    "ekstra_mesaj": "{} adli user, {} id'li bap sablonu kaydetti.".format(
                        current_user.username,
                        sablon.id)
                }
                signal_sender(**signal_payload)
        sablonlar = DB.session.query(Sablon).order_by(Sablon.updated_at).all()

        return render_template("varsayilan_sablonlar.html", sablon_form=form, sablonlar=sablonlar)

    @login_required
    @auth.requires(Permission(*permission_dict["yonetim"]["bap_yonetimi"]["sablon_ayarlari"]))
    @route('/data', methods=["POST"], endpoint="sablon_search")
    def sablon_arama(self):  # pylint: disable=too-many-branches
        """
        Bap şablonlarında POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = SablonSearchForm(**form_data)

        sablon_adi = search_form.sablon_adi.data.strip()
        kullanilabilir_mi = search_form.kullanilabilir_mi.data
        sablon_tipi = search_form.sablon_tipi.data

        if not search_form.validate():
            result = qry.order_by(desc(Sablon.updated_at)).offset(form_data['start']).limit(
            form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        if sablon_adi:
            qry = qry.filter(Sablon.adi.ilike('%' + sablon_adi + '%'))

        if kullanilabilir_mi != 0:
            if kullanilabilir_mi == 1:
                qry = qry.filter(Sablon.kullanilabilir_mi == True)
            else:
                qry = qry.filter(Sablon.kullanilabilir_mi == False)

        if sablon_tipi != 0:
            qry = qry.filter(SablonTipi.id == sablon_tipi)

        result = qry.order_by(desc(Sablon.updated_at)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
