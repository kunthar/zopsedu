"""Kullanici Profil"""
from _sha512 import sha512

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, abort
from flask import session
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from zopsedu.app import DB
from zopsedu.auth.models.auth import User
from zopsedu.auth.lib import auth
from zopsedu.auth.models.auth import UserRole
from zopsedu.bap.lib.auth import OzgecmisKaydetme
from zopsedu.common.kullanici_profil.models import Ozgecmis
from zopsedu.common.mesaj.models import Mesaj
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.models import File, Person
from zopsedu.personel.models.harici_ogretim_elemani import HariciOgretimElemani
from zopsedu.personel.models.personel import Personel
from .forms import AvatarGuncelleForm, RolForm, OzgecmisKayitFormu, PasswordChangeForm, HariciOgretimElemaniFormu
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class KullaniciProfilView(FlaskView):
    """KullaniciProfilView"""

    @property
    def user_id(self):
        """Current User's id"""
        return current_user.get_id()

    @property
    def qry(self):
        """User objesi dondurur."""
        return User.query.filter(User.id == self.user_id).options(joinedload(User.person))

    @property
    def avatar(self):  # pylint: disable=inconsistent-return-statement
        """User avatar dondurur."""
        user = DB.session.query(User.avatar.label("avatar")).filter(User.id == self.user_id).first()
        if user.avatar:
            return current_app.wsgi_app.url_for(user.avatar.path)

    @property
    def _ozgecmis(self):
        return DB.session.query(
            Ozgecmis
        ).filter(
            Ozgecmis.user_id == self.user_id
        )

    @login_required
    @route('/', methods=["GET"], endpoint='profil_goruntule')
    def profil_goruntule(self):
        """Profil Goruntile"""
        args = request.args.get('args')
        user = self.qry.one()

        personel = DB.session.query(Personel).filter(Personel.person_id == user.person.id). \
            options(
            joinedload(Personel.person).joinedload(Person.odeme_bilgileri)
        ).first()

        # todo: bap memurunu role göre filtereliyor personel tablosuna ilgili birim eklendiğinde değişecek.
        if session['current_user_role'] == 2 or session['current_user_role'] == 5:
            return render_template('profil.html',
                               user=user,
                               bap_memuru=personel,
                               avatar_url=self.avatar)


        elif personel:
            return render_template('profil.html',
                                   user=user,
                                   personel=personel,
                                   avatar_url=self.avatar
                                   )


        else:

            harici_ogretim_elemani = DB.session.query(HariciOgretimElemani). \
                filter(HariciOgretimElemani.person_id == user.person.id). \
                options(joinedload(HariciOgretimElemani.person).joinedload(Person.odeme_bilgileri)
                        ).first()

            form = HariciOgretimElemaniFormu(
                tckn=harici_ogretim_elemani.person.tckn,
                unvan=harici_ogretim_elemani.unvan,

                ad=harici_ogretim_elemani.person.ad,
                soyad=harici_ogretim_elemani.person.soyad,
                birincil_eposta=harici_ogretim_elemani.person.birincil_eposta,
                ikincil_eposta=harici_ogretim_elemani.person.ikincil_eposta,
                ev_tel_no=harici_ogretim_elemani.person.ev_tel_no,
                cep_tel=harici_ogretim_elemani.person.cep_telefonu,
                adres=harici_ogretim_elemani.person.ikametgah_adresi.adres,
                adres2=harici_ogretim_elemani.person.ikincil_adres.adres,
                akademik_yayinlari = harici_ogretim_elemani.yayinlar,
                banka_adi=harici_ogretim_elemani.person.odeme_bilgileri[0].banka_adi,
                sube_adi=harici_ogretim_elemani.person.odeme_bilgileri[0].sube_adi,
                sube_kod=harici_ogretim_elemani.person.odeme_bilgileri[0].sube_kod,
                hesap_no=harici_ogretim_elemani.person.odeme_bilgileri[0].hesap_no,
                iban_no=harici_ogretim_elemani.person.odeme_bilgileri[0].iban_no,
                )
            return render_template('profil.html',
                                   user=user,
                                   harici_ogretim_elemani=harici_ogretim_elemani,
                                   form=form,
                                   args=args,
                                   avatar_url=self.avatar
                                   )


    @login_required
    @route('/', methods=["POST"], endpoint='profil_kaydet')
    def profil_kaydet(self):
        """Profil kaydet"""
        user = self.qry.one()
        harici_ogretim_elemani = DB.session.query(HariciOgretimElemani). \
            filter(HariciOgretimElemani.person_id == user.person.id). \
            options(joinedload(HariciOgretimElemani.person).joinedload(Person.odeme_bilgileri)
                    ).first()

        form = HariciOgretimElemaniFormu(request.form)
        if form.validate():
            try:
                harici_ogretim_elemani.person.tckn = request.form['tckn']
                harici_ogretim_elemani.unvan = request.form['unvan']
                harici_ogretim_elemani.person.ad = request.form['ad']
                harici_ogretim_elemani.person.soyad = request.form['soyad']
                harici_ogretim_elemani.person.birincil_eposta = request.form['birincil_eposta']
                harici_ogretim_elemani.person.ikincil_eposta = request.form['ikincil_eposta']
                harici_ogretim_elemani.person.ev_tel_no = request.form['ev_tel_no']
                harici_ogretim_elemani.person.cep_telefonu = request.form['cep_tel']
                harici_ogretim_elemani.person.ikametgah_adresi.adres = request.form['adres']
                harici_ogretim_elemani.person.ikincil_adres.adres = request.form['adres2']
                harici_ogretim_elemani.yayinlar = request.form['akademik_yayinlari']
                harici_ogretim_elemani.person.odeme_bilgileri[0].banka_adi = request.form['banka_adi']
                harici_ogretim_elemani.person.odeme_bilgileri[0].sube_adi = request.form['sube_adi']
                harici_ogretim_elemani.person.odeme_bilgileri[0].sube_kod = request.form['sube_kod']
                harici_ogretim_elemani.person.odeme_bilgileri[0].hesap_no = request.form['hesap_no']
                harici_ogretim_elemani.person.odeme_bilgileri[0].iban_no = request.form['iban_no']
                DB.session.commit()
            except SQLAlchemyError as error:
                DB.session.rollback()
                CustomErrorHandler.error_handler(
                    hata="Harici hakem eklenmeye ""çalışıldı. Hata: {}".format(error))
                return abort(500)
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("common").get("harici_profil_guncelle").type_index,
                "nesne": 'Harici ogretim elemani',
                "nesne_id": harici_ogretim_elemani.id,
                "ekstra_mesaj": "{} adlı {} idli harici ogretim elemani "
                                "profil bilgilerini değiştirdi"
                                ".".format(current_user.username, current_user.id)
            }
            signal_sender(**signal_payload)
            success_msg = _('Profil bilgilerinizi başarıyla değiştirdiniz.')
            args = {
                'success_msg': success_msg,
            }
            return render_template('profil.html',
                                   user=user,
                                   harici_ogretim_elemani=harici_ogretim_elemani,
                                   form=form,
                                   args=args)
        else:
            args = {'unknown_error': 'Profil bilgilerinizi değiştirirken bir hata oluştu.'}
            return render_template('profil.html',
                                   user=user,
                                   harici_ogretim_elemani=harici_ogretim_elemani,
                                   form=form,
                                   args=args)


    @login_required
    @route('/avatar', methods=["GET"], endpoint='avatar')
    def avatar_guncelle(self):
        """Avatar guncelle get"""
        user = self.qry.one()
        avatar_form = AvatarGuncelleForm(request.form)

        return render_template('avatar_guncelle.html', avatar_form=avatar_form,
                               user=user,
                               avatar_url=self.avatar)

    @login_required
    @route('/avatar', methods=["POST"])
    def post_avatar_guncelle(self):
        """Avatar guncelle post"""
        user = self.qry.one()
        avatar = request.files.get('avatar', None)

        try:
            if avatar:
                user.avatar = avatar
                DB.session.commit()
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("common").get("profil_fotograf_guncelle").type_index,
                    "nesne": 'User',
                    "nesne_id": user.id,
                    "ekstra_mesaj": "{} adlı kullanıcı profil fotoğrafını güncelledi.".format(
                        user.username)
                }
                signal_sender(**signal_payload)
                flash(_("Avatariniz guncellendi."))
            else:
                flash(_("Avatarınızı güncellemek için bir resim seçmelisiniz."))
        except ValueError as vexc:
            flash(str(vexc))

        return redirect(url_for('kullanici_profil.avatar'))

    @login_required
    @route('/okunmamis_mesaj_sayisi', methods=["GET"], endpoint='okunmamis_mesaj_sayisi')
    def okunmamis_mesaj_sayisi(self):
        """Okunmamis mesaj sayisini gosterir"""
        okunmamis_mesaj_sayisi = DB.session.query(
            Mesaj.id
        ).filter(
            Mesaj.alici == self.user_id,
        ).filter(Mesaj.okundu == False).count()  # pylint: disable=singleton-comparison

        return jsonify({
            "okunmamis_mesaj_sayisi": okunmamis_mesaj_sayisi,
            "avatar_url": "{}".format(
                self.avatar)
        })

    @login_required
    @route('/rol', methods=["GET"], endpoint='rol_degistir')
    def rol_degistir(self):
        """Rol degistirme ekrani"""
        user = self.qry.options(joinedload(User.roles)).one()
        roles = [(r.id, r.name) for r in user.roles]

        rol_form = RolForm(request.form)
        rol_form.roles.choices = roles
        rol_form.roles.default = session['current_role']
        rol_form.process()
        return render_template('rol.html', rol_form=rol_form, user=user,
                               avatar_url=self.avatar)

    @login_required
    @route('/parola', methods=["GET"], endpoint='parola_degistir')
    def parola_degistir(self):
        """Parola degistirme ekrani"""
        args = request.args.get('args')
        user = self.qry.options(joinedload(User.roles)).one()
        parola_form = PasswordChangeForm()
        return render_template('parola.html',
                               user=user,
                               parola_form=parola_form,
                               avatar_url=self.avatar,
                               args=args)

    @login_required
    @route('/parola', methods=["POST"])
    def post_parola_degistir(self):
        """Parola degistirme ekrani"""
        user = User.query.filter_by(id=current_user.get_id()).one()
        parola_form = PasswordChangeForm(request.form)

        if parola_form.validate():
            old_password = sha512(parola_form.old_password.data.encode()).hexdigest()
            new_password = sha512(parola_form.new_password.data.encode()).hexdigest()
            if current_user.password == old_password:
                try:
                    user.password = new_password
                    DB.session.commit()
                    flash(_("Parolanız güncellendi"))

                except SQLAlchemyError as error:
                    DB.session.rollback()
                    flash(_("Parolanız güncellenirken bir hata oluştu. Girdiğiniz bilgileri lütfen kontrol ediniz."))
                    CustomErrorHandler.error_handler()

                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("common").get("parola_degisikligi").type_index,
                    "ekstra_mesaj": "{} adlı kullanıcı parolasini degistirdi.".format(
                        current_user.username)
                }
                signal_sender(**signal_payload)

            else:
                flash(_("Parolanız güncellenirken bir hata oluştu. Girdiğiniz bilgileri lütfen kontrol ediniz."))
                signal_payload = {
                    "message_type": USER_ACTIVITY_MESSAGES.get("common").get("hatali_parola").type_index,
                    "ekstra_mesaj": "{} adlı kullanıcı parolasini degistirirken"
                                    "Eski parolasini hatali girdi.".format(
                        current_user.username)
                }
                signal_sender(**signal_payload)
        else:
            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("common").get("parola_degistirirken_hata").type_index,
                "ekstra_mesaj": "{} adlı kullanıcı parolasini degistiremedi.".format(
                    current_user.username)
            }
            signal_sender(**signal_payload)
            flash(_("Parolanız güncellenirken bir hata oluştu. Girdiğiniz bilgileri lütfen kontrol ediniz."))

        return render_template("parola.html",
                               parola_form=parola_form,
                               user=user,
                               avatar_url=self.avatar,
                               )

    @login_required
    @route('/rol', methods=["POST"])
    def post_rol_degistir(self):
        """Rol degistirme ekrani kayit"""
        cache = current_app.extensions['redis']

        rol_form = RolForm(request.form)
        role_id = int(rol_form.roles.data)
        user_role = UserRole.query.filter_by(user_id=self.user_id, role_id=role_id).first()
        session['current_user_role'] = user_role.id
        session['current_role'] = role_id
        cache.set(current_app.config['USER_LAST_LOGIN_ROLE_ID_CACHE_KEY'].
                  format(user_id=self.user_id), session['current_role'])
        role = user_role.role
        session['current_role_name'] = role.name
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("common").get("gecerli_rol_degistir").type_index,
            "ekstra_mesaj": "{} adlı kullanıcı gecerli rolunu {} olarak degistirdi.".format(
                current_user.username, role.name)
        }
        signal_sender(**signal_payload)
        return redirect(url_for('kullanici_profil.rol_degistir'))

    @login_required
    @route('/ozgecmis', methods=["GET"])
    def ozgecmis_goruntule(self):
        """Ozgecmis Goruntuleme Ekrani
        """
        ozgecmis = self._ozgecmis.first()
        profile_photo = current_app.wsgi_app.url_for(
            current_user.profile_photo.path) if current_user.profile_photo else None

        if ozgecmis:
            kayit_formu = OzgecmisKayitFormu(
                tecrube=ozgecmis.tecrube,
                ozgecmis_dosya_id=ozgecmis.file_id
            )
        else:
            kayit_formu = OzgecmisKayitFormu()

        return render_template(
            "ozgecmis.html",
            kayit_formu=kayit_formu,

            profile_photo=profile_photo,
            user=current_user,
            ozgecmis_kaydetme=OzgecmisKaydetme(),
            avatar_url=self.avatar,
        )

    @login_required
    @auth.requires(OzgecmisKaydetme())
    @route('/ozgecmis/kaydet', methods=["POST"])
    def ozgecmis_kaydet(self):
        """Ozgecmis Kaydetme Ekrani
        """
        kayit_formu = OzgecmisKayitFormu(request.form)

        ozgecmis = Ozgecmis.query.filter(Ozgecmis.user_id == current_user.get_id()).one()
        ozgecmis_dosya = request.files.get(kayit_formu.ozgecmis_dosya.name, None)

        if not kayit_formu.validate():
            flash("Lütfen uygun dosya uzantısı olan bir özgeçmiş yükleyiniz.")
            return redirect(url_for('kullanici_profil.KullaniciProfilView:ozgecmis_goruntule'))
        if ozgecmis_dosya:
            _ozgecmis_dosya = File(content=ozgecmis_dosya)
            DB.session.add(_ozgecmis_dosya)
            DB.session.flush()

            ozgecmis.file_id = _ozgecmis_dosya.id
            DB.session.add(ozgecmis)
            DB.session.commit()
        else:
            ozgecmis.tecrube = kayit_formu.tecrube.data
            DB.session.add(ozgecmis)
            DB.session.commit()

        flash("Özgeçmişiniz başarılı bir şekilde kaydedilmiştir.")

        return redirect(url_for('kullanici_profil.KullaniciProfilView:ozgecmis_goruntule'))

    @login_required
    @route('/ozgecmis/indir', methods=["POST"])
    def ozgecmis_indir(self):
        """Ozgecmis Indirme Ekrani
        """
        _ozgecmis = self._ozgecmis.first()
        if _ozgecmis and _ozgecmis.file:
            return send_file(
                _ozgecmis.file.file_object,
                as_attachment=True,
                mimetype=_ozgecmis.file.content.file.content_type,
                attachment_filename=_ozgecmis.file.content.file.filename,
            )
        else:
            flash("Yüklediğiniz herhangi bir özgeçmiş bulunmamaktadır.")
            return redirect(url_for('kullanici_profil.KullaniciProfilView:ozgecmis_goruntule'))
