""" Kayıt Geçmisi Modülü """

from flask import render_template, request, flash, redirect, url_for
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required
from sqlalchemy import desc

from zopsedu.auth.models.auth import  User
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.models import Role, AktiviteKaydi, Person
from zopsedu.auth.lib import auth, Permission
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
from zopsedu.sistem_takibi.forms import KayitGecmisiForm


class KayitGecmisiView(FlaskView):
    excluded_methods = ['form', 'qry', 'activity_types']

    @property
    def qry(self):
        """Aktivite kayıtlarını getirir. """
        return DB.session.query(
            AktiviteKaydi.id.label("activity_id"),
            AktiviteKaydi.zaman.label("activity_time"),
            AktiviteKaydi.ekstra_mesaj.label("activity_extra_mesaj"),
            AktiviteKaydi.remote_ip.label("activity_remote_ip"),
            Person.ad.label("person_ad"),
            Person.soyad.label("person_soyad"),
            Role.name.label("role_name"),
            AktiviteKaydi.context.label("activity_context"),
            User.id.label("user_id"),
            User.username.label("user_name")
        ).join(
            User,
            User.id == AktiviteKaydi.user_id
        ).join(
            Person,
            Person.user_id == AktiviteKaydi.user_id,
        ).join(
            Role,
            AktiviteKaydi.role_id == Role.id
        ).order_by(desc(AktiviteKaydi.zaman))

    def form(self):
        kayit_gecmisi_form = KayitGecmisiForm(request.form)
        activity_types = [(0, _("Filtrelemek İçin Bir Değer Seçiniz"))]
        activity_types.extend(self.activity_types())
        kayit_gecmisi_form.activite_tipleri.choices = activity_types
        kayit_gecmisi_form.activite_tipleri.default = 0
        return kayit_gecmisi_form

    @staticmethod
    def activity_types():
        """
        Activite kayıt mesajları listesi döndürür
        :return(list): activity message types
        """
        activity_type_list = []
        for module_values in USER_ACTIVITY_MESSAGES.values():
            for activity_message in module_values.values():
                activity_type_list.append(activity_message)
        return activity_type_list

    @login_required
    @auth.requires(Permission(*permission_dict['sistem_takibi']['aktivite_kaydi']['aktivite_kayitlari_listeleme']),
                   menu_registry={'path': '.sistem_takibi.aktivite_gecmisi',
                                  'title': _("Kullanıcı Aktivitesi")})
    @route('/liste', methods=['GET'])
    def kayit_gecmisi_goruntule(self):
        result = self.qry.all()
        kayit_gecmisi_form = self.form()
        activity_types = [(0, _("Filtrelemek İçin Bir Değer Seçiniz"))]
        activity_types.extend(self.activity_types())
        kayit_gecmisi_form.activite_tipleri.choices = activity_types
        kayit_gecmisi_form.activite_tipleri.default = 0

        return render_template('kayit_gecmisi/kayit_gecmisi.html',
                               form=kayit_gecmisi_form,
                               activities=result)

    @login_required
    @auth.requires(Permission(*permission_dict['sistem_takibi']['aktivite_kaydi']['aktivite_kayitlari_listeleme']))
    @route('/liste', methods=['POST'])
    def kayitlari_filtrele(self):
        """
        AktiviteKayitlarini filtrelemek için kullanılır.

        Başlama tarihi, bitiş tarihi, activity_message_type, username ve AktiviteMesaj extra_mesaj
        degişkeni üzerinde filtre uygulanır
        """
        qry = self.qry
        form = self.form()

        ara_text = form.ara_text.data
        baslama_tarihi = form.tarih_arama.baslama_tarihi.data
        bitis_tarihi = form.tarih_arama.bitis_tarihi.data
        baslama_tarihi_option = form.tarih_arama.baslama_tarihi_option.data
        bitis_tarihi_option = form.tarih_arama.bitis_tarihi_option.data
        activity_message_index = form.activite_tipleri.data
        username = form.username.data

        if not form.validate():
            flash("Filtre alanlarını doğru kullandığınızdan emin olun!")
            return self.kayit_gecmisi_goruntule()

        if request.form.get('temizle') == _('Temizle'):
            return redirect(url_for('.KayitGecmisiView:kayit_gecmisi_goruntule'))

        if ara_text:
            qry = qry.filter(
                AktiviteKaydi.ekstra_mesaj.ilike('%' + form.ara_text.data.strip() + '%'))

        if baslama_tarihi:
            if baslama_tarihi_option == '0':
                qry = qry.filter(AktiviteKaydi.zaman <= baslama_tarihi)
            if baslama_tarihi_option == '1':
                qry = qry.filter(AktiviteKaydi.zaman == baslama_tarihi)
            if baslama_tarihi_option == '2':
                qry = qry.filter(baslama_tarihi <= AktiviteKaydi.zaman)

        if bitis_tarihi:
            if bitis_tarihi_option == '0':
                qry = qry.filter(AktiviteKaydi.zaman <= bitis_tarihi)
            if bitis_tarihi_option == '1':
                qry = qry.filter(AktiviteKaydi.zaman == bitis_tarihi)
            if bitis_tarihi_option == '2':
                qry = qry.filter(bitis_tarihi <= AktiviteKaydi.zaman)

        if activity_message_index:
            qry = qry.filter(AktiviteKaydi.message_type == activity_message_index)

        if username:
            qry = qry.filter(
                User.username.ilike('%' + username + '%'))

        result = qry.all()
        form.activite_tipleri.default = activity_message_index
        return render_template('kayit_gecmisi/kayit_gecmisi.html',
                               activities=result,
                               form=form)

    @login_required
    @auth.requires(Permission(*permission_dict['sistem_takibi']['aktivite_kaydi']['aktivite_kayit_gecmisi_detayi']))
    @route('/liste/<int:activity_id>/detay',
           methods=['GET'],
           endpoint='detay')
    def kayit_detaylari(self, activity_id):
        """AktiviteKaydi detayini döner"""
        aktivite_kaydi = DB.session.query(
            AktiviteKaydi,
            Person.ad.label("person_ad"),
            Person.soyad.label("person_soyad"),
            User.username.label("username"),
            Role.name.label("role_name")
        ).join(
            User, AktiviteKaydi.user_id == User.id
        ).join(
            Person, Person.user_id == User.id
        ).join(
            Role, AktiviteKaydi.role_id == Role.id
        ).filter(AktiviteKaydi.id == activity_id).one()

        return render_template('kayit_gecmisi/kayit_detay.html', result=aktivite_kaydi)
