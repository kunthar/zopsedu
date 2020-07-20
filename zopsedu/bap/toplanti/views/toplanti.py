"""BAP Toplanti View Modulu"""

from flask import render_template, request, url_for, redirect, flash, abort, jsonify, render_template_string
from flask_allows import Or
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.orm import joinedload, raiseload, lazyload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError

from zopsedu.auth.models.auth import User
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.helpers import ToplantiDurumu, KararDurumu
from zopsedu.bap.models.toplanti import ToplantiKatilimci
from zopsedu.bap.toplanti.forms import ToplantiOlusturForm, ToplantiKatilimciEkleForm, ToplantiFiltreleForm
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.auth.lib import Permission, auth, Role
from zopsedu.lib.db import DB
from zopsedu.models import BapToplanti, BapGundem, Sablon, Person
from zopsedu.bap.toplanti.forms import ToplantiEkleForm, ToplantiGundem
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.personel.models.idari_personel import BapIdariPersonel
from zopsedu.personel.models.personel import Personel


class ToplantiView(FlaskView):
    """Toplanti ile ilgili islemler Viewi"""

    excluded_methods = [
        "qry",
        "toplanti_ekle_form",
        "user_id"
    ]

    @property
    def qry(self):
        kabul = DB.session.query(
            BapGundem.toplanti_id, func.count('*').label('gundem_kabul')
        ).group_by(
            BapGundem.toplanti_id, BapGundem.karar_durum
        ).having(
            BapGundem.karar_durum == 'kabul'
        ).subquery()

        # Karar durumu "ret" olma sayisi
        ret = DB.session.query(
            BapGundem.toplanti_id, func.count('*').label('gundem_ret')
        ).group_by(
            BapGundem.toplanti_id, BapGundem.karar_durum
        ).having(
            BapGundem.karar_durum == 'ret'
        ).subquery()

        # Karar durumu "degerlendirilmesi" olma sayisi
        degerlendirilmedi = DB.session.query(
            BapGundem.toplanti_id, func.count('*').label('gundem_degerlendirilmedi')
        ).group_by(
            BapGundem.toplanti_id, BapGundem.karar_durum
        ).having(
            BapGundem.karar_durum == KararDurumu.degerlendirilmedi
        ).subquery()

        # Her bir BapToplanti elemeni ve iliskisi bulundugu BapGundem elemaninin kabul ve ret
        #    durumlarinin sayisini dondurur.
        toplanti_listesi = DB.session.query(
            BapToplanti,
            kabul.c.gundem_kabul.label("kabul"),
            ret.c.gundem_ret.label("ret"),
            degerlendirilmedi.c.gundem_degerlendirilmedi.label("degerlendirilmedi"),
        ).outerjoin(
            kabul, BapToplanti.id == kabul.c.toplanti_id
        ).outerjoin(
            ret, BapToplanti.id == ret.c.toplanti_id
        ).outerjoin(
            degerlendirilmedi, BapToplanti.id == degerlendirilmedi.c.toplanti_id
        ).options(
            joinedload(BapToplanti.ekleyen).joinedload(User.person).load_only("ad", "soyad"),
            raiseload("*")
        )

        return toplanti_listesi

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            render_template_string("""
                    {% if toplanti_tarihi %}
                        {{ '{:%d.%m.%Y}'.format(toplanti_tarihi) }}
                    {% else %}
                        -
                    {% endif %}
               """, toplanti_tarihi=r[0].toplanti_tarihi),
            r[0].toplanti_durumu.value,
            render_template_string("""
                {{ item.ekleyen.person.ad + ' ' + item.ekleyen.person.soyad }}
                """, item=r[0]),
            render_template_string("""
                {% if kabul == None %}
                    {% set kabul = 0 %}
                {% endif %}
                {% if ret == None %}
                    {% set ret = 0 %}
                {% endif %}
                {% if degerlendirilmedi == None %}
                    {% set degerlendirilmedi = 0 %}
                {% endif %}
                    {{ degerlendirilmedi | string + " Değerlendirilmedi, " if degerlendirilmedi else ""}} {{ kabul }} Kabul ve {{ ret }} Ret
                """, kabul=r.kabul, ret=r.ret, degerlendirilmedi=r.degerlendirilmedi),
            render_template_string("""
                 <a class="detail_arrow"
                    href="{{ url_for('toplanti.toplanti_gundem_listele', toplanti_id=id) }}">
                    <span class="float-left detail_edit fa ft-edit fa-2x m-l-10"></span>
                </a>
                """, id=r[0].id)

        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record
                        })

    @property
    def user_id(self):
        """Kullanici idsi dondurur"""
        return current_user.id

    @property
    def toplanti_ekle_form(self):
        """Toplanti Ekleme Formu dondurur"""
        toplanti_ekle_form = ToplantiEkleForm(request.form)
        return toplanti_ekle_form

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_listesi_goruntuleme"]),
                   menu_registry={'path': '.bap.yk_toplanti.toplanti_listesi',
                                  'title': _("Toplantı")}
                   )
    @route("/listesi")
    def liste(self):
        """Toplanti Listesi Ekrani"""

        form = ToplantiFiltreleForm()

        return render_template("toplanti_listele.html",
                               toplanti_ekle_form=self.toplanti_ekle_form,
                               form=form)

    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_olusturma"]))
    @route("/listesi", methods=["POST"], endpoint='ekle')
    def ekle(self):
        """Toplanti Ekleme"""
        toplanti_ekle_form = ToplantiEkleForm(request.form)
        toplanti = BapToplanti(toplanti_tarihi=toplanti_ekle_form.toplanti_tarihi.data,
                               toplanti_durumu=toplanti_ekle_form.toplanti_durumu.data,
                               ekleyen_id=self.user_id, )
        DB.session.add(toplanti)
        DB.session.commit()
        flash(_("Toplantı başarıyla eklenmiştir."))
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                "toplanti_olustur").type_index,
            "nesne": 'BAP Toplanti',
            "nesne_id": toplanti.id,
            "ekstra_mesaj": "{} adlı kullanıcı yeni toplanti olusturdu.".format(
                current_user.username),
        }
        signal_sender(**signal_payload)
        return redirect(url_for('toplanti.ToplantiView:liste'))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_silme"]))
    @route("/sil/<int:toplanti_id>", methods=["DELETE"], endpoint='sil')
    def sil(toplanti_id):
        """Toplanti Silme"""
        toplanti = DB.session.query(
            BapToplanti).filter(BapToplanti.id == toplanti_id).one()
        if toplanti:
            DB.session.delete(toplanti)
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                    "toplanti_sil").type_index,
                "nesne": 'BAP Toplanti',
                "nesne_id": toplanti.id,
                "ekstra_mesaj": "{} adlı kullanıcı bap toplantisini sildi.".format(
                    current_user.username),
            }
            signal_sender(**signal_payload)
            return jsonify(status="success")

        return abort(400)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_listesi_goruntuleme"]),
                      Role("BAP Yetkilisi"),
                      Role("BAP Admin")))
    @route('/data', methods=["POST"], endpoint="toplanti_search")
    def toplanti_arama(self):  # pylint: disable=too-many-branches
        """
        Bap toplanti POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response

        """
        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = ToplantiFiltreleForm(**form_data)

        date = search_form.date.toplanti_tarihi.data
        date_option = search_form.date.toplanti_tarihi_option.data
        toplanti_durumu = search_form.toplanti_durumu.data

        if toplanti_durumu != '0' and toplanti_durumu:
            qry = qry.filter(BapToplanti.toplanti_durumu == toplanti_durumu)

        if not search_form.validate():
            result = qry.order_by(desc(BapToplanti.created_at)).offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        if date:
            if date_option == '0':
                qry = qry.filter(BapToplanti.toplanti_tarihi >= date)
            if date_option == '1':
                qry = qry.filter(BapToplanti.toplanti_tarihi == date)
            if date_option == '2':
                qry = qry.filter(BapToplanti.toplanti_tarihi <= date)

        result = qry.order_by(desc(BapToplanti.created_at)).offset(form_data['start']).limit(
            form_data['length']).all()

        return self.process_data(result, form_data, total_record)


class ToplantiOlusturView(FlaskView):
    """
    Toplanti olusturmak icin kullanilan view
    """

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/<int:toplanti_id>/gundem', methods=['GET'], endpoint="toplanti_gundem_listele")
    def toplanti_gundem_listele(toplanti_id):
        """Toplanti gundemlerini listeler"""
        user_id = current_user.id
        gundem_form = ToplantiGundem()
        try:
            toplanti = DB.session.query(BapToplanti).options(
                joinedload(BapToplanti.gundemler).joinedload(
                    BapGundem.proje).load_only("id", "proje_no", "proje_basligi").lazyload("*"),
                raiseload("*")
            ).filter_by(id=toplanti_id).one()
        except NoResultFound as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Var olmayan bir toplanti id ile istek gönderildi.User id: {},"
                     " Hata: {}".format(user_id, exc))
            return abort(404)
        gundem_sayisi = len(toplanti.gundemler)
        gundem_form.gundem_sira_no.choices = [(i + 1, str(i + 1)) for i in range(gundem_sayisi)]

        # sablon tipi id '51' Yönetim Kurulu Tutanak Şablonunu temsil etmektedir.
        toplanti_tutanak_sablonu = DB.session.query(Sablon.id.label("sablon_id"),
                                                    Sablon.sablon_tipi_id.label("sablon_tipi_id")).filter(
            Sablon.sablon_tipi_id == 51).order_by(desc(Sablon.updated_at)).first()

        return render_template('toplanti_gundemleri.html',
                               gundemler=toplanti.gundemler,
                               gundem_form=gundem_form,
                               toplanti_id=toplanti_id,
                               toplanti_sonuclandi_mi=toplanti.sonuclandi_mi,
                               toplanti_tutanak_sablon_id=toplanti_tutanak_sablonu.sablon_id,
                               sablon_type_id=toplanti_tutanak_sablonu.sablon_tipi_id)

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_olusturma"]))
    @route('/', methods=['POST'], endpoint='kaydet')
    def toplanti_kaydet():
        """
        Formda kaydedilen gundemler ve tarih/saat ile yeni bir toplantı olusturur.
        Returns:
        """
        form_nesne = ToplantiOlusturForm(request.form)
        toplantiya_alinanlar = list(
            filter(lambda x: x['toplantiya_alinsin'], form_nesne.data['gundem_listesi']))

        if form_nesne.validate() and toplantiya_alinanlar:
            try:
                toplanti = BapToplanti(toplanti_durumu=ToplantiDurumu.gerceklestirilmedi,
                                       ekleyen_id=current_user.id)
                DB.session.add(toplanti)
                DB.session.flush()
                for ind, top_al in enumerate(toplantiya_alinanlar):
                    gundem_id = top_al['id']
                    gundem = BapGundem.query.get(gundem_id)
                    gundem.toplanti_id = toplanti.id
                toplanti.toplanti_tarihi = form_nesne.data['toplanti_tarih_saat']
                DB.session.commit()

                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                        "toplanti_olustur").type_index,
                    "nesne": 'BapToplanti',
                    "nesne_id": toplanti.id,
                    "ekstra_mesaj": "{user} kullanıcısı, {gundemler} idli gündemlerle, {toplanti} "
                                    "idli yeni toplantı "
                                    "oluşturdu.".format(
                        user=current_user.username,
                        gundemler=list(map(lambda x: x['id'], toplantiya_alinanlar)),
                        toplanti=toplanti.id
                    )
                }
                signal_sender(**signal_payload)

                return redirect(url_for('index'))
            except SQLAlchemyError as e:
                DB.session.rollback()
                CustomErrorHandler.error_handler(
                    hata="{} kullanıcısı bir toplantı oluşturmaya çalışırken hata "
                         "meydana geldi. hata: {}".format(current_user.username, e))

                flash(_("Bir hata meydana geldi. İşleminiz kaydedilemedi."))
                return redirect(url_for('.ToplantiOlusturView:toplanti_maddeleri_listele'))

        else:
            flash('Formu doğru doldurduğunuzdan emin olunuz.')
            return redirect(url_for('.ToplantiOlusturView:toplanti_maddeleri_listele'))

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["toplanti"]["toplanti_olusturma"]))
    @route('/listele/sonuclanmamis', methods=['GET'], endpoint='degerlendirilmemis_toplantilar')
    def sonuclanmamis_toplantilar():
        """Sonuclanmamis gundemleri dondurur"""
        sonuclanmamis_toplantilar = DB.session.query(BapToplanti).options(
            joinedload(BapToplanti.ekleyen).load_only("id").joinedload(
                User.person).load_only("ad", "soyad").lazyload("*"),
            raiseload("*")
        ).filter(BapToplanti.sonuclandi_mi == False).all()
        data = []
        for toplanti in sonuclanmamis_toplantilar:
            toplanti_tarihi = toplanti.toplanti_tarihi.strftime(
                "%d.%m.%Y") if toplanti.toplanti_tarihi else "Toplantı tarihi belirtilmedi"
            data.append({
                "id": toplanti.id,
                "ekleyen": "{} {}".format(toplanti.ekleyen.person.ad if toplanti.ekleyen else "",
                                          toplanti.ekleyen.person.soyad if toplanti.ekleyen else ""),
                "toplanti_tarihi": toplanti_tarihi,
                "toplanti_durumu": toplanti.toplanti_durumu.value
            })
        return jsonify(status="success", sonuclanmamis_toplantilar=data)

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('<int:toplanti_id>/katilimci-ekle', methods=['GET', 'POST'])
    def katilimci_ekle(toplanti_id):
        if request.method == 'GET':
            idari_personeller = DB.session.query(BapIdariPersonel.id.label("id"),
                                                 BapIdariPersonel.gorevi.label("gorevi"),
                                                 Person.ad.label("person_ad"),
                                                 Person.soyad.label("person_soyad")). \
                filter(BapIdariPersonel.gorevde_mi == True). \
                join(Personel, BapIdariPersonel.personel_id == Personel.id). \
                join(Person, Personel.person_id == Person.id).all()

            toplanti_katilimcilari = DB.session.query(ToplantiKatilimci.katilimcilar.label("katilimcilar")).filter(
                ToplantiKatilimci.toplanti_id == toplanti_id).first()

            toplanti_katilimci_form = ToplantiKatilimciEkleForm()

            for idari_personel in idari_personeller:
                katildi_mi = False
                if toplanti_katilimcilari:
                    katildi_mi = True if idari_personel.id in [key for key in
                                                               toplanti_katilimcilari.katilimcilar] else False

                toplanti_katilimci_form.katilimcilar.append_entry({
                    'secili_mi': katildi_mi,
                    'idari_personel_id': idari_personel.id,
                    'ad': "{} {}".format(idari_personel.person_ad, idari_personel.person_soyad),
                    'gorevi': idari_personel.gorevi.value
                })

            return render_template("toplanti_katilimcilari.html",
                                   toplanti_id=toplanti_id,
                                   katilimci_form=toplanti_katilimci_form)

        katilimcilar = request.form
        toplanti_katilimci_ekle_form = ToplantiKatilimciEkleForm(**katilimcilar)
        if not toplanti_katilimci_ekle_form.validate():
            flash("Bir hata oluştu lütfen daha sonra tekrar deneyiniz")
            return render_template("toplanti_katilimcilari.html",
                                   toplanti_id=toplanti_id,
                                   katilimci_form=toplanti_katilimci_ekle_form)

        katilimci_list = []
        for katilimci in toplanti_katilimci_ekle_form.katilimcilar:
            if katilimci.secili_mi.data:
                katilimci_list.append(katilimci.idari_personel_id.data)

        toplanti_katilimci_kayit = DB.session.query(ToplantiKatilimci).filter(
            ToplantiKatilimci.toplanti_id == toplanti_id).first()

        if not katilimci_list:
            flash("Toplantıya en az bir adet katılımcı eklemelisiniz")
            return render_template("toplanti_katilimcilari.html",
                                   toplanti_id=toplanti_id,
                                   katilimci_form=toplanti_katilimci_ekle_form)

        try:
            if not toplanti_katilimci_kayit:
                toplanti_katilimci_kayit = ToplantiKatilimci(katilimcilar=katilimci_list,
                                                             toplanti_id=toplanti_id)
                DB.session.add(toplanti_katilimci_kayit)
            else:
                toplanti_katilimci_kayit.katilimcilar = katilimci_list
                toplanti_katilimci_kayit.toplanti_id = toplanti_id
            DB.session.commit()
        except SQLAlchemyError as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Toplanti idsi %s olan toplantıya katılımcılar eklenirken hata oluştu. Hata: %s"
                     % (toplanti_id, exc)
            )
            flash("Bir hata oluştu lütfen daha sonra tekrar deneyiniz")
            return render_template("toplanti_katilimcilari.html",
                                   toplanti_id=toplanti_id,
                                   katilimci_form=toplanti_katilimci_ekle_form)

        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                "toplanti_katilimcilari_duzenlendi").type_index,
            "nesne": 'BAP Toplanti',
            "nesne_id": toplanti_id,
            "ekstra_mesaj": "{} idli toplantiya katılanlar duzenlendi".format(
                toplanti_id),
        }
        signal_sender(**signal_payload)

        flash("Toplantı katılımcılarını başarıyla düzenlendiniz")
        return redirect(url_for('toplanti.toplanti_gundem_listele', toplanti_id=toplanti_id))

    @staticmethod
    @login_required
    @auth.requires(
        Or(Permission(*permission_dict["bap"]["toplanti"]["toplanti_guncelleme"]),
           Role('BAP Yetkilisi'),
           Role("BAP Admin")))
    @route('/<int:toplanti_id>/sonuclandir', methods=['POST'])
    def toplanti_sonuclandir(toplanti_id):
        """YK toplantisini sonuclandir"""
        toplanti_katilimci_kayit = DB.session.query(ToplantiKatilimci).filter(
            ToplantiKatilimci.toplanti_id == toplanti_id).first()

        if not toplanti_katilimci_kayit:
            flash("Lütfen sonuçlandırmadan önce toplantıya katılımcı ekleyiniz")
            return redirect(url_for("toplanti.toplanti_gundem_listele",
                                    toplanti_id=toplanti_id))

        try:
            degerlendirmemis_gundem_sayisi = DB.session.query(
                BapGundem
            ).filter(
                BapGundem.toplanti_id == toplanti_id,
                BapGundem.karar_durum == KararDurumu.degerlendirilmedi
            ).count()

            if degerlendirmemis_gundem_sayisi:
                flash("Toplantıda değerlendirilmemiş gündemler mevcut. "
                      "Lütfen gündemleri değerlendirin veya toplantıdan çıkarınız.")
                return redirect(url_for("toplanti.toplanti_gundem_listele",
                                        toplanti_id=toplanti_id))

            toplanti = DB.session.query(BapToplanti).options(lazyload("*")).filter_by(
                id=toplanti_id).one()
            toplanti.sonuclandi_mi = True
            toplanti.toplanti_durumu = ToplantiDurumu.gerceklestirildi
            flash("Toplantı başarılı bir şekilde sonuçlandırıldı.")
            DB.session.commit()
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("toplanti").get(
                    "toplanti_sonuclandirildi").type_index,
                "nesne": 'BAP Toplanti',
                "nesne_id": toplanti.id,
                "ekstra_mesaj": "{} adlı kullanıcı bap toplantisini sonuçlandırdı.".format(
                    current_user.username),
            }
            signal_sender(**signal_payload)
        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Var olmayan bir toplanti id ile istek gönderildi.User id: {},"
                     " Hata: {}".format(current_user.id, exc))
            return abort(404)

        return redirect(url_for("toplanti.toplanti_gundem_listele",
                                toplanti_id=toplanti_id))
