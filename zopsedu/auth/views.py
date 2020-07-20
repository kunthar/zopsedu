"""AUTH VIEW METOTLARI"""
from hashlib import sha512

from flask import request, render_template, session, redirect, url_for, current_app, Response, \
    make_response, flash
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from sqlalchemy.exc import SQLAlchemyError
from wtforms import StringField, validators, BooleanField, PasswordField
from wtforms.fields.html5 import EmailField

from zopsedu.app import DB
from zopsedu.auth.models.auth import User, Role
from zopsedu.bap.models.firma import BapFirma
from zopsedu.lib.form.forms import LoginForm
from zopsedu.lib.sessions import SessionHandler
from zopsedu.lib.signals.signal_sender import signal_sender
from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES


class UserLoginForm(FlaskForm):
    """Login Form"""
    username = StringField(
        validators=[validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))],
        render_kw={"placeholder": _('Kullanıcı Adı')}
    )
    password = LoginForm.password
    submit = LoginForm.submit


class UserSignupForm(FlaskForm):
    """Signup Form"""
    email = EmailField(
        label=_('E-posta'),
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Email(message=_('Geçersiz e-posta.'))
        ]
    )
    username = StringField(
        label=_('Kullanıcı Adı'),
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Length(3, 16,
                              message=_('Kullanıcı adı en az 3, en fazla 12 karakterden oluşmalı.'))
        ]
    )
    password = PasswordField(
        label=_('Parola'),
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Length(3, 16, message=_('Parola en az 3, en fazla 16 karakterden oluşmalı.'))
        ]
    )
    accept_tos = BooleanField(
        label=_('Şartlar ve Koşulları kabul ediyorum.'),
        validators=[validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))]
    )
    submit = LoginForm.submit2


class AuthView(FlaskView):
    """Auth View"""

    @staticmethod
    @route('/login', endpoint='login', methods=['GET'])
    def get_login_view():
        """
        Login formunu dündürür.
        """
        # already logged in
        if session.get('is_authenticated'):
            return redirect(url_for('ping'))

        success_msg = None
        if request.args.get('new_user'):
            success_msg = _('Başarıyla kayıt oldunuz. Lütfen giriş yapınız.')
        args = {
            'success_msg': success_msg,
            'title': _('Giriş Yap'),
            'footer': _('Bütün hakları saklıdır')
        }
        form = UserLoginForm(request.form)

        # todo: after refresh the page, old errors came fix it
        return render_template('login.html', form=form, args=args)

    @staticmethod
    @route('/login', methods=['POST'])
    def post_login_view():
        """
        Kullanıcıyı kullanıcı adı ve parolası ile doğrular.
        Returns:

        """
        default_url = url_for('index')
        form = UserLoginForm(request.form)
        password = sha512(form.password.data.encode()).hexdigest()

        user = DB.session.query(User).filter_by(
            username=form.username.data,
            password=password
        ).first()

        if form.validate() and user:
            # success
            firma = DB.session.query(BapFirma).filter(
                BapFirma.user_id == user.id).first()

            if firma and not firma.onaylandi and not firma.faaliyet_durumu:
                # firma girisi basarisiz
                flash(_("Firmanız, Bap tarafından henüz onaylanmadığı için "
                        "veya kabul edilmediği için giriş yapamıyorsunuz."))
                return redirect(url_for('auth.login'))

            if not user.durumu:
                flash("Giriş başarısızdır. Lütfen ilgili birimle irtibat kurunuz.")
                return redirect(url_for('.login'))

            try:
                user_ad = "{} {}".format(user.person.ad, user.person.soyad)
            except AttributeError:
                user_ad = user.username

            if not login_user(user):
                return Response(_('Kullanıcı aktif değil'), 401)

            SessionHandler.session_login_set(user=user,
                                             user_ad=user_ad)

            current_app.logger.debug('Logged in user %s', user.username)
            user_role = DB.session.query(Role).filter(
                Role.id == session.get('current_role')
            ).first()

            ekstra_mesaj = ""
            if firma and firma.onaylandi and firma.faaliyet_durumu:
                # firma girisi basarili
                default_url = url_for('firma.BapFirmaIslemleriView:firma_dashboard')
                ekstra_mesaj = "{} {}, {} rolu ile firma girişi yapıldı".format(
                    firma.yetkili_adi,
                    firma.yetkili_soyadi,
                    user_role.name)

            signal_payload = {
                "message_type": USER_ACTIVITY_MESSAGES.get("auth").get("login").type_index,
                "nesne": 'User',
                "nesne_id": user.id,
                "ekstra_mesaj": ekstra_mesaj if ekstra_mesaj else "{} {}, {} rolü ile giriş yaptı.".format(
                    user.person.ad,
                    user.person.soyad,
                    user_role.name
                ),
            }
            signal_sender(**signal_payload)

            if request.headers.environ.get('HTTP_X_REQUESTED_WITH'):
                # response for ajax call
                return Response('', 302)

            # to delete flask_login message
            session.pop('_flashes', None)

            # Useri logout etmek icin gereklidir.
            user.session_id = session.sid
            DB.session.commit()

            role_dashboard = {
                2: url_for('bap_yetkilisi_dashboard.BapYetkilisiDashboardView:index'),
                3: url_for('proje.ProjeYurutucuDashboard:genel'),
                4: url_for('hakem_dashboard.HakemDashboard:hakem_proje_degerlendirme_istekleri'),
                5: url_for('bap_yetkilisi_dashboard.BapYetkilisiDashboardView:index'),
                8: url_for('bap_yetkilisi_dashboard.BapYetkilisiDashboardView:rektor_kokpiti')
            }
            role_id = None
            if user.roles:
                role_id = user.roles[0].id

            if role_dashboard.get(role_id, None):
                default_url = role_dashboard.get(role_id)

            # response for /auth/login page
            next_url = request.args.get('next', default_url)
            resp = make_response(redirect(next_url))
            if not request.cookies.get("introSeen", None):
                resp.set_cookie("introSeen", "false")
            return resp

        else:
            success_msg = None
            if request.args.get('new_user'):
                success_msg = _('Başarıyla kayıt oldunuz. Lütfen giriş yapınız.')
            args = {
                'success_msg': success_msg,
                'title': _('Giriş Yap'),
                'footer': _('Bütün hakları saklıdır')
            }

            if not form.errors:
                args['unknown_error'] = _('Kullanıcı adı veya Parola yanlış.')

        return render_template('login.html', form=form, args=args)

    @staticmethod
    @login_required
    @route('/logout', methods=['GET'])
    def logout():
        """
        Kullanıcı oturumunu kapatır.

        """
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("auth").get("logout").type_index,
            "nesne": 'User',
            "nesne_id": current_user.id,
            "ekstra_mesaj": "{} adlı kullanıcı çıkış yaptı.".format(current_user.username),
        }
        signal_sender(**signal_payload)

        last_login_role = {
            current_app.config['USER_LAST_LOGIN_ROLE_ID_CACHE_KEY'].format(user_id=current_user.id):
                session.get('current_role'),
            current_app.config['USER_LAST_LOGIN_ROLE_NAME_CACHE_KEY'].
                format(user_id=current_user.id):
                session.get('current_role_name')}

        SessionHandler.session_logout_flush(is_authenticated=False,
                                            last_role=last_login_role)

        logout_user()

        return redirect(url_for('anasayfa.BapAnasayfaView:bap_anasayfa'))

    @staticmethod
    @route('/signup', methods=['GET'])
    def get_signup_view():
        """
        Kayıt formunu getirir.
        Returns:

        """
        args = {
            'title': _('Kayıt Ol'),
            'footer': _('Bütün hakları saklıdır')
        }
        form = UserSignupForm(request.form)
        # todo: after refresh the page, old errors came fix it
        return render_template('signup.html', form=form, args=args)

    @staticmethod
    @route('/signup', methods=['POST'])
    def post_signup_view():
        """
        Doldurulan form ile kullanıcıyı kaydeder.

        """
        form = UserSignupForm(request.form)
        new_user = User()
        new_user.username = form.username.data
        new_user.email = form.email.data
        new_user.password = sha512(form.password.data.encode()).hexdigest()

        args = {
            'title': _('Kayıt Ol'),
            'footer': _('Bütün hakları saklıdır')
        }

        try:
            if form.validate():
                sess = DB.session()
                sess.add(new_user)
                sess.commit()
            else:
                return render_template('signup.html', form=form, args=args)
        except SQLAlchemyError as exception:
            current_app.logger.info((str(exception)))
            if 'users_email_key' in exception.args[0]:
                form.email.errors.append(_('Email zaten kayıtlı.'))
            elif 'users_username_key' in exception.args[0]:
                form.username.errors.append(_('Kullanıcı adı zaten var.'))
            else:
                form.username.errors.append(_('Bilinmeyen bir hata oluştu.'))
            return render_template('signup.html', form=form, args=args)
        signal_payload = {
            "message_type": USER_ACTIVITY_MESSAGES.get("auth").get("signup").type_index,
            "ekstra_mesaj": "{} adı ile bir kullanıcı kaydı yapıldı.".format(new_user.username),
        }
        signal_sender(**signal_payload)
        return redirect(url_for('auth.login', new_user=1))
