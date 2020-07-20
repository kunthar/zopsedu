"""BAP Toplanti View Modulu"""
from flask import request, abort, jsonify, render_template, send_file, flash, \
    render_template_string, url_for, redirect
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from flask_babel import gettext as _
from flask_allows import Or
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import lazyload, raiseload, joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_, desc

from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.helpers import GundemTipi, GundemDurumu, ProjeBasvuruDurumu
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.toplanti import GundemSablon, BapToplanti
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.lib.db import DB
from zopsedu.models import BapGundem, AppState, File
from zopsedu.bap.toplanti.forms import ToplantiGundem, DegerlendirilmemisGundemFiltreleForm, \
    GundemOlustur, ProjeFiltreleForm
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.models.helpers import AppStates
from zopsedu.bap.lib.query_helpers import BapQueryHelpers


class GundemView(FlaskView):
    """Toplanti Gundem Viewi"""

    excluded_methods = [
        "qry",
        "qry_proje"
    ]

    @property
    def qry_proje(self):
        return DB.session.query(
            Proje.id.label("proje_id"),
            Proje.kabul_edilen_baslama_tarihi.label("kabul_edilen_baslama_tarihi"),
            Proje.bitis_tarihi.label("bitis_tarihi"),
            Proje.proje_basligi.label("proje_basligi"),
            Proje.proje_no.label("proje_no"),
            AppState.state_code.label("proje_durumu"),
            AppState.description.label("proje_durum_aciklamasi"),
            Proje.bitis_tarihi.label("bitis_tarihi"),
            Proje.kabul_edilen_baslama_tarihi.label("kabul_edilen_baslama_tarihi")
        ).join(AppState, AppState.id == Proje.proje_durumu_id)

    @property
    def qry(self):

        return DB.session.query(BapGundem). \
            outerjoin(Proje, BapGundem.proje_id == Proje.id). \
            outerjoin(File, BapGundem.ek_dosya_id == File.id). \
            outerjoin(BapToplanti, BapGundem.toplanti_id == BapToplanti.id).add_columns(
            BapGundem.id.label("gundem_id"),
            BapGundem.tipi.label("gundem_tipi"),
            BapGundem.aciklama.label("aciklama"),
            BapGundem.karar.label("karar"),
            BapGundem.ek_dosya_id.label("ek_dosya_id"),
            Proje.proje_no.label("proje_no"),
            Proje.proje_basligi.label("proje_basligi"),
            BapToplanti.toplanti_tarihi.label("toplanti_tarihi"),
            BapToplanti.id.label("toplanti_id")
        )

    def process_data_proje(self, result, form_data, total_record):
        gundem_olustur_formu = GundemOlustur()

        for proje in result:
            gundem_olustur_formu.projeler.append_entry({
                "proje_id": proje.proje_id,
                "proje_durum_aciklamasi": "{} ({})".format(proje.proje_durum_aciklamasi, proje.proje_durumu),
                "proje_baslik": proje.proje_basligi,
                "proje_no": proje.proje_no,
                "bitis_tarihi": proje.bitis_tarihi if proje.bitis_tarihi else ' - ',
                "kabul_edilen_baslama_tarihi": proje.kabul_edilen_baslama_tarihi if proje.kabul_edilen_baslama_tarihi else ' - ',
            })

        data = [[
            render_template_string("""
            {{ index }}
            {{ proje_id }}
            """, index=index + 1, proje_id=r.proje_id),
            render_template_string("""
            {{ secili_mi }}
            """, secili_mi=r.secili_mi),
            render_template_string("""
            {{ proje_no.data }}{{ proje_no }}
            """, proje_no=r.proje_no),
            render_template_string("""
            {{ proje_baslik.data }}{{ proje_baslik }}
            """, proje_baslik=r.proje_baslik),
            render_template_string("""
            {{ proje_durum_aciklamasi.data }} {{ proje_durum_aciklamasi }}
            """, proje_durum_aciklamasi=r.proje_durum_aciklamasi),
            render_template_string("""
                            {{ kabul_edilen_baslama_tarihi.data }} {{kabul_edilen_baslama_tarihi }}
                            """, kabul_edilen_baslama_tarihi=r.kabul_edilen_baslama_tarihi),
            render_template_string("""
            {{ bitis_tarihi.data }} {{bitis_tarihi }}
            """, bitis_tarihi=r.bitis_tarihi)

        ] for index, r in enumerate(gundem_olustur_formu['projeler'])]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record
                        })

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.proje_no,
            r.proje_basligi,
            r.gundem_tipi.value,
            render_template_string("""
             {% if toplanti_tarihi %}
                {{ "{:%d.%m.%Y}".format(toplanti_tarihi) }}
            {% else %}
                {{ _('Toplantı eklenmedi') }}
            {% endif %}
            """, toplanti_tarihi=r.toplanti_tarihi),
            render_template_string("""
             {% if aciklama %}
                {{ aciklama | safe }}
                {% else %}
                -
            {% endif %}
            """, aciklama=r.aciklama),
            render_template_string("""
             {% if karar %}
                {{ karar | safe }}
                {% else %}
                -
            {% endif %}
            """, karar=r.karar),
            render_template_string("""
            {% if ek_dosya_id %}
                <div class="document-name attached-document clearfix">
                    <form method="post">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                            <button class="btn btn-info"
                                id="ek_{{ ek_dosya_id }}"
                                name="ek_{{ ek_dosya_id }}"
                                value="{{ ek_dosya_id }}"
                                style="white-space: normal;"
                                formaction="{{ url_for('toplanti.ek_dosya_indir', 
                                                belge_id= ek_dosya_id ) }}">
                                {{ _('Ek Belge İndir') }}
                            </button>
                    </form>
                </div>
            {% else %}
                {{ _('Ek Belge Eklenmedi') }}
            {% endif %}    
            """, ek_dosya_id=r.ek_dosya_id),

            render_template_string("""
                 <a href="#gundem-toplanti-degistir"
                    data-toggle="modal"
                    data-target="#gundem-toplanti-degistir
                    data-toplanti-id="{{ toplanti_id if gundem_id }}"
                    data-gundem-id="{{ gundem_id }}"
                    onclick="gundem_modal_open('{{ gundem_id }}', '{{ toplanti_id }}');">
                    <span class="float-left detail_edit fa ft-edit fa-2x m-l-10"></span>
                </a>
            """, toplanti_tarihi=r.toplanti_tarihi if r.gundem_id else 0, gundem_id=r.gundem_id,
                                   toplanti_id=r.toplanti_id),

            render_template_string(""" <input type="hidden" id="gundem-id" value="{{ id }}"> """, id=r.gundem_id),

        ] for index, r in enumerate(result)]
        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @staticmethod
    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_listeleme"]),
                      Role("BAP Yetkilisi"),
                      Role("BAP Admin")),
                   menu_registry={'path': '.bap.yk_toplanti.degerlendirilmemis_gundem_listele',
                                  'title': _("Gündemler")})
    @route("/degerlendirilmemis-gundemler", methods=['GET'])
    def degerlendirilmemis_gundem_listele():
        """
        Değerlendirilmemis gündemleri listeler

        """
        gundem_form = ToplantiGundem()

        gundem_sablon_list = [(i.id, i.sablon_tipi) for i in DB.session.query(GundemSablon).all()]
        gundem_form.sablon.choices = gundem_sablon_list

        gundem_filtrele_form = DegerlendirilmemisGundemFiltreleForm()

        return render_template('gundem_listele.html',
                               gundem_form=gundem_form,
                               gundem_filtrele_form=gundem_filtrele_form)

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/gundem/<int:gundem_id>', methods=['GET'], endpoint="get_gundem")
    def get_gundem(gundem_id):
        """Belirli bir toplanti gundemini almak icin kullaniriz"""
        user_id = current_user.id
        try:
            gundem = DB.session.query(BapGundem).options(
                joinedload(BapGundem.proje).load_only("proje_basligi", "proje_no", "id").lazyload(
                    "*"),
                raiseload("*")
            ).filter_by(id=gundem_id).one()
        except NoResultFound as exc:
            CustomErrorHandler.error_handler(
                hata="Var olmayan bir gundeme ulasilmalay calisildi. User id: {}, "
                     "Gundem id: {}, Hata: {}".format(user_id,
                                                      gundem_id,
                                                      exc))
            return abort(404)

        gundem_data = {
            "gundemId": gundem_id,
            "sablonId": gundem.sablon_id,
            "ekDosyaId": gundem.ek_dosya_id,
            "karar": gundem.karar,
            "aciklama": gundem.aciklama,
            "tipi": gundem.tipi.name,
            "kararDurumu": gundem.karar_durum.name,
            "gundemSiraNo": gundem.gundem_sira_no,
            "yonetimeBilgiNotu": gundem.yonetime_bilgi_notu,
            "kisiyeOzelNot": gundem.kisiye_ozel_not,
            "projeBasligi": gundem.proje.proje_basligi,
            "projeId": gundem.proje_id,
            "projeNo": gundem.proje.proje_no
        }

        return jsonify(status="success", gundemData=gundem_data)

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/gundem/<int:gundem_id>/guncelle',
           methods=['POST'],
           endpoint="gundem_guncelle")
    def gundem_guncelle(gundem_id):
        """Gundem guncellemek icin kullanilir"""
        user_id = current_user.id
        gundem_data = request.get_json()
        gundem_formu = ToplantiGundem(**gundem_data)
        try:
            gundem = DB.session.query(BapGundem).filter_by(id=gundem_id).one()
        except NoResultFound as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Olmayan bir gündem güncellenmeye çalışıldı."
                     "Gündem id: {}, User id: {}, Hata: {}".format(
                    gundem_id,
                    user_id,
                    exc)
            )

            return jsonify(status="error"), 400
        try:

            gundem_data = gundem_formu.data
            gundem_data.pop("proje_id")
            gundem_data.pop("gundem_id")
            if gundem_data.get("gundem_sira_no") is None:
                gundem_data.pop("gundem_sira_no")
            gundem.update_obj_data(gundem_data)
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Toplanti gündem güncellenmeye calisilirken bir hata olustu."
                     "Gundem id: {}, User id: {}, Hata: {}".format(
                    gundem_id,
                    user_id,
                    exc)
            )

            return jsonify(status="error"), 400

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                "gundem_guncelle").type_index,
            "nesne": 'BAP Gundem',
            "nesne_id": gundem_id,
            "ekstra_mesaj": "{username} adlı kullanıcı toplanti gundemini guncelledi.".format(
                username=current_user.username),
        }
        signal_sender(**signal_payload)
        DB.session.commit()

        toplanti_tarihi = gundem.toplanti.toplanti_tarihi.strftime(
            "%d.%m.%Y") if gundem.toplanti and gundem.toplanti.toplanti_tarihi else "Toplantı tarihi belirtilmedi"
        data = {
            "toplanti_tarihi": toplanti_tarihi,
            "gundem_tipi": gundem.tipi.value,
            "gundem_aciklama": gundem.aciklama,
            "gundem_karar": gundem.karar,
            "toplanti_id": gundem.toplanti_id
        }

        return jsonify(status="success", gundem_data=data)

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/<int:toplanti_id>/gundem/<int:gundem_id>',
           methods=['DELETE'],
           endpoint="toplanti_gundemi_sil")
    def gundem_sil(toplanti_id, gundem_id):
        """
        Gündemi toplanti gundemleri arasindan cikarmak icin kullanılır.
        """
        user_id = current_user.id
        try:
            cikarilacak_gundem = DB.session.query(BapGundem).filter_by(
                toplanti_id=toplanti_id,
                id=gundem_id).one()
            cikarilacak_gundem.toplanti_id = None
            DB.session.commit()
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Gündem silinirken bir hata oluştu.Gundem id: {}, Toplanti id:"
                     " {}, User id: {}, Hata: {}".format(gundem_id,
                                                         toplanti_id,
                                                         user_id,
                                                         exc)
            )

            return jsonify(status="error"), 400
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                "toplanti_gundem_cikar").type_index,
            "nesne": 'BAP Gundem',
            "nesne_id": gundem_id,
            "etkilenen_nesne": "BAP Toplanti",
            "etkilenen_nesne_id": toplanti_id,
            "ekstra_mesaj": "{username} adlı kullanıcı {gundem_id} id'li gundemi toplanti "
                            "gundemleri arasindan cikardi.".format(username=current_user.username,
                                                                   gundem_id=gundem_id),
        }
        signal_sender(**signal_payload)
        return jsonify(status="success")

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/<int:toplanti_id>/gundem_sira_no',
           methods=['POST'],
           endpoint="gundem_sira_no_guncelle")
    def gundem_sira_no_guncelle(toplanti_id):
        """
        Rowreorder datatable da gundem sirasinda bir degisiklik oldugunda ilgili gündemlerin
        sira numarasini degistirmek icin kullanılan view
        """
        gundem_data = request.get_json()
        user_id = current_user.id
        try:
            guncellenecek_gundem = DB.session.query(BapGundem).filter_by(
                id=gundem_data["gundem_id"], toplanti_id=toplanti_id).one()
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Gundem sira no guncellenirken hata olustu. Gundem id: {}, "
                     "User id: {}, Hata: {}".format(gundem_data["gundem_id"],
                                                    user_id,
                                                    exc))
            return abort(400)
        guncellenecek_gundem.gundem_sira_no = int(gundem_data["gundem_sira_no"])
        DB.session.commit()
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                "gundem_sira_degistir").type_index,
            "nesne": 'BAP Gundem',
            "etkilenen_nesne": "BAP Toplanti",
            "etkilenen_nesne_id": toplanti_id,
            "ekstra_mesaj": "{username} adlı kullanıcı toplanti gundem sirasini degistirdi.".format(
                username=current_user.username),
        }
        signal_sender(**signal_payload)

        return jsonify(status="success")

    @staticmethod
    @login_required
    @auth.requires(Or(Role('BAP Yetkilisi'), Role("BAP Admin")))
    @route('/<int:belge_id>', methods=["POST"], endpoint='ek_dosya_indir')
    def ek_dosya_indir(belge_id):

        """Gundem Ek Belgeler"""

        gundem_belge = BapGundem.query.filter(BapGundem.ek_dosya_id == belge_id).one()

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("common").get("gundem_ek_indir").type_index,
            "nesne": 'GundemEkDosya',
            "nesne_id": belge_id,
            "ekstra_mesaj": "{} adlı kullanıcı {} id'li gundem ekini indirdi.".format(
                current_user.username,
                belge_id
            )
        }
        signal_sender(**signal_payload)

        return send_file(
            gundem_belge.ek_dosya_r.file_object,
            as_attachment=True,
            attachment_filename=gundem_belge.ek_dosya_r.content.file.filename,
            mimetype=gundem_belge.ek_dosya_r.content.content_type
        )

    @staticmethod
    @login_required
    @auth.requires(Or(Role('BAP Yetkilisi'), Role("BAP Admin")))
    @route('/render-gundem-sablonu', methods=["POST"])
    def render_gundem_sablonu():
        """
        İki farklı kullanımı mevcut

        Belirli bir gündemin gündem tipini degistirmeye calisildigi durumda Gündem id ve gündem tipi
        verisine(gundem verisinden ilgili projenin id si bulunur) gore ilgili sablonu render
        edip karar ve aciklama verisini döner.
        Belirli bir proje icin gundem olusturmaya calisirken proje id ve gundem tipi verisiyle
        kullanilabilir
        """
        try:
            gundem_id = request.get_json().get("gundem_id", None)
            sablon_tipi = request.get_json().get("sablon_tipi", None)
            proje_id = request.get_json().get("proje_id", None)

            gundem_sablonu = DB.session.query(
                GundemSablon.id.label("sablon_id"),
                GundemSablon.karar.label("karar"),
                GundemSablon.aciklama.label("aciklama"),
            ).filter(
                GundemSablon.sablon_tipi == sablon_tipi
            ).order_by(desc(GundemSablon.updated_at)).first()

            if gundem_id:
                gundem = DB.session.query(
                    BapGundem.aciklama.label("aciklama"),
                    BapGundem.karar.label("karar"),
                    BapGundem.proje_id.label("proje_id")
                ).options(
                    lazyload("*")
                ).filter(BapGundem.id == gundem_id).first()

                proje_id = gundem.proje_id

            if not gundem_sablonu:
                return jsonify(status="error"), 500

            gundem_proje_data_query = BapQueryHelpers.get_gundem_sablon_proje_data_query()
            proje_gundem_sablon_data = gundem_proje_data_query.filter(
                Proje.id == proje_id
            ).first()
            karar_text = render_template_string(gundem_sablonu.karar,
                                                proje=proje_gundem_sablon_data)
            aciklama_text = render_template_string(gundem_sablonu.aciklama,
                                                   proje=proje_gundem_sablon_data)
            data = {
                "karar": karar_text,
                "aciklama": aciklama_text,
                "sablon_id": gundem_sablonu.sablon_id
            }
            return jsonify(status="success", data=data)
        except Exception as exc:
            CustomErrorHandler.error_handler(
                hata="Gündemi tipine göre şablon metni render "
                     "edilirken bir hata meydana geldi. "
                     "Hata: {}".format(exc))
            return jsonify(status="error"), 500

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/olustur',
           methods=['GET'])
    def toplu_gundem_olustur_get():
        """Gundem guncellemek icin kullanilir"""

        projeler = DB.session.query(
            Proje.id.label("proje_id"),
            Proje.proje_no.label("proje_no"),
            Proje.proje_basligi.label("proje_basligi"),
            AppState.description.label("state_description"),
            AppState.state_code.label("state_code"),
            AppState.current_app_state
        ).join(
            AppState, Proje.proje_durumu_id == AppState.id
        ).options(
            lazyload("*")
        ).filter(
            or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.revizyon_bekleniyor,
                Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi),
            AppState.current_app_state != AppStates.son
        ).all()

        gundem_olustur_formu = GundemOlustur()

        proje_filtrele_formu = ProjeFiltreleForm()

        for proje in projeler:
            gundem_olustur_formu.projeler.append_entry({
                "proje_id": proje.proje_id,
                "proje_state": "{} ({})".format(proje.state_description, proje.state_code),
                "proje_baslik": proje.proje_basligi,
                "proje_no": proje.proje_no
            })

        return render_template("gundem_olustur.html", gundem_olusturma_formu=gundem_olustur_formu,
                               proje_filtrele_formu=proje_filtrele_formu)

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/olustur',
           methods=['POST'])
    def toplu_gundem_olustur_post():
        """Gundem guncellemek icin kullanilir"""

        gundem_olustur_formu = GundemOlustur(request.form)

        gundem_olusturulacak_proje_ids = [proje.proje_id.data for proje in
                                          gundem_olustur_formu.projeler if proje.secili_mi.data]

        if not gundem_olusturulacak_proje_ids:
            flash("Gündem oluşturabilmek için proje seçmeniz gerekmektedir")
            return render_template("gundem_olustur.html",
                                   gundem_olusturma_formu=gundem_olustur_formu)

        try:
            gundem_sablonu_obj = DB.session.query(
                GundemSablon.id.label("id"),
                GundemSablon.karar.label("karar"),
                GundemSablon.aciklama.label("aciklama")
            ).filter(
                GundemSablon.sablon_tipi == gundem_olustur_formu.gundem_tipi.data
            ).order_by(
                desc(GundemSablon.updated_at)
            ).first()

            karar_sablonu = gundem_sablonu_obj.karar
            gundem_sablonu = gundem_sablonu_obj.aciklama

            gundem_proje_data_query = BapQueryHelpers.get_gundem_sablon_proje_data_query()
            gundem_olusturulacak_projeler = gundem_proje_data_query.filter(
                Proje.id.in_(gundem_olusturulacak_proje_ids)
            ).all()

            for proje in gundem_olusturulacak_projeler:
                karar_text = render_template_string(karar_sablonu, proje=proje)
                gundem_text = render_template_string(gundem_sablonu, proje=proje)
                yeni_gundem = BapGundem(proje_id=proje.proje_id,
                                        sablon_id=gundem_sablonu_obj.id,
                                        karar=karar_text,
                                        aciklama=gundem_text,
                                        tipi=gundem_olustur_formu.gundem_tipi.data)
                DB.session.add(yeni_gundem)
                # todo: user activity log
                # todo: adminlere mesaj atilabilir !!!

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                    "toplanti_sonuclandirildi").type_index,
                "ekstra_mesaj": "{} adlı kullanıcı {} 'idli proje/projeleri icin {} tipinde toplu gündem oluşturdu.".format(
                    current_user.username,
                    ",".join(str(proje_id) for proje_id in gundem_olusturulacak_proje_ids),
                    gundem_olustur_formu.gundem_tipi.data
                ),
            }
            signal_sender(**signal_payload)
            DB.session.commit()
            flash("Gündemler başarıyla oluşturuldu.")

        except Exception as exc:
            CustomErrorHandler.error_handler(
                hata="Gündem oluşturulurken bir hatayla karşılaşıldı. "
                     "Hata: {}".format(exc))
            DB.session.rollback()
            flash("Gündem oluşturulurken bir hata ile karşılaşıldı. "
                  "Lütfen daha sonra tekrar deneyiniz.")
            return render_template("gundem_olustur.html",
                                   gundem_olusturma_formu=gundem_olustur_formu)

        return redirect(url_for("toplanti.GundemView:degerlendirilmemis_gundem_listele"))

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["proje"]["proje_arama"]["projeleri_arama"])),
                   Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route('/data-proje', methods=["POST"], endpoint="proje_search")
    def proje_arama(self):  # pylint: disable=too-many-branches
        """
        Bap projelerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry_proje
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = ProjeFiltreleForm(**form_data)

        proje_durumu = search_form.proje_durumu.data
        proje_sureci = search_form.proje_sureci.data

        if proje_sureci == "-1":
            qry = qry.filter(or_((AppState.current_app_state == 'basvuru_kabul'),
                                 (AppState.current_app_state == 'devam'),
                                 (AppState.current_app_state == 'son')))
        if proje_sureci == 'AppStates.basvuru_kabul':
            qry = qry.filter(AppState.current_app_state == 'basvuru_kabul')
        if proje_sureci == 'AppStates.devam':
            qry = qry.filter(AppState.current_app_state == 'devam')
        if proje_sureci == 'AppStates.son':
            qry = qry.filter(AppState.current_app_state == 'son')

        if proje_durumu != '0' and proje_durumu != 'None':
            qry = qry.filter(AppState.id == int(proje_durumu))

        if not search_form.validate():
            result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        proje_basligi = search_form.ad.data.strip()
        proje_no = search_form.proje_no.data
        kabul_edilen_baslama_tarihi = search_form.date.baslama_tarihi.data
        bitis_tarihi = search_form.date.bitis_tarihi.data
        baslama_tarihi_option = search_form.date.baslama_tarihi_option.data
        bitis_tarihi_option = search_form.date.bitis_tarihi_option.data

        if proje_basligi:
            qry = qry.filter(Proje.proje_basligi.ilike('%' + proje_basligi + '%'))

        if proje_no:
            qry = qry.filter(Proje.proje_no == proje_no)

        if kabul_edilen_baslama_tarihi:
            if baslama_tarihi_option == '0':
                qry = qry.filter(Proje.kabul_edilen_baslama_tarihi <= kabul_edilen_baslama_tarihi)
            if baslama_tarihi_option == '1':
                qry = qry.filter(Proje.kabul_edilen_baslama_tarihi == kabul_edilen_baslama_tarihi)
            if baslama_tarihi_option == '2':
                qry = qry.filter(kabul_edilen_baslama_tarihi <= Proje.kabul_edilen_baslama_tarihi)

        if bitis_tarihi:
            if bitis_tarihi_option == '0':
                qry = qry.filter(Proje.bitis_tarihi <= bitis_tarihi)
            if bitis_tarihi_option == '1':
                qry = qry.filter(Proje.bitis_tarihi == bitis_tarihi)
            if bitis_tarihi_option == '2':
                qry = qry.filter(bitis_tarihi <= Proje.bitis_tarihi)

        result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data_proje(result, form_data, total_record)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_gundemi_listeleme"]),
                      Role("BAP Yetkilisi"),
                      Role("BAP Admin")))
    @route('/data', methods=["POST"], endpoint="gundem_search")
    def gundem_arama(self):  # pylint: disable=too-many-branches
        """
        Bap gündemlerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = DegerlendirilmemisGundemFiltreleForm(**form_data)

        gundem_durumu = search_form.gundem_durumu.data
        gundem_tipi = search_form.gundem_tipi.data
        date = search_form.date.toplanti_tarihi.data
        date_option = search_form.date.toplanti_tarihi_option.data
        proje_numarasi = search_form.proje_numarasi.data

        """ Gündem henüz degerlendirilmedi """
        if gundem_durumu == "degerlendirilmedi":
            qry = qry.filter(BapGundem.karar_durum == GundemDurumu.degerlendirilmedi)

        """ Gündem bir toplantıya atanmadı """
        if gundem_durumu == "atanmamis":
            qry = qry.filter(BapGundem.toplanti_id.is_(None))

        if gundem_tipi != 'tüm_gündemler' and gundem_tipi != 'None':
            gundem_tipi = getattr(GundemTipi, gundem_tipi)
            qry = qry.filter(BapGundem.tipi == gundem_tipi)

        if not search_form.validate():
            result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        if proje_numarasi:
            qry = qry.filter(Proje.proje_no == proje_numarasi)

        if date:
            if date_option == '0':
                qry = qry.filter(BapToplanti.toplanti_tarihi >= date)
            if date_option == '1':
                qry = qry.filter(BapToplanti.toplanti_tarihi == date)
            if date_option == '2':
                qry = qry.filter(BapToplanti.toplanti_tarihi <= date)

        result = qry.order_by(desc(Proje.id)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)
