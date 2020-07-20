"""Zopsedu Server Module"""
import json
import time
import logging
from sqlalchemy.orm import load_only
from uuid import uuid4
from datetime import datetime

from babel.numbers import format_currency
from flask import render_template, request, session, current_app, redirect, url_for
from flask_allows import Requirement
from flask_jwt_extended import create_access_token
from flask_login import current_user
from flask_menu import register_menu, current_menu
from flask_babel import lazy_gettext as _
from sqlalchemy.exc import SQLAlchemyError
from num2words import num2words

from zopsedu.app import app
from zopsedu.auth.models.auth import User
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.logs import LogHandler
from zopsedu.lib.mail import init_mail
from zopsedu.lib.sessions import SessionHandler
from zopsedu.models import SiteAyarlari, Permission
from zopsedu.zopsedu_app import zopsedu_app

# pylint: disable=invalid-name

app = zopsedu_app(app)

log_handler = LogHandler()
log_handler.setLevel(level=logging.WARNING)
for logger in (
        app.logger,
        logging.getLogger('sqlalchemy'),
        logging.getLogger('werkzeug'),
):
    logger.addHandler(log_handler)


# pylint: enable=invalid-name


class AktifModulMenu(Requirement):
    """
    Uygulamanın parçası olan modlüllerin enabled olup olmadığını, menude gosterilip
    gosterilmeyecegini belirleyen requirement classı.
    """

    def __init__(self, module_name):
        self.module_name = module_name

    # pylint: disable=redefined-outer-name
    def fulfill(self, user, request=None):
        """Modulun enabled moduller arasında olup olmadigini denetler"""
        return self.module_name in app.config.get('ENABLED_MODULES')
        # pylint: enable=redefined-outer-name

    def has_visible_child(self):
        """Menu iteminin visible childi olup olmadigini denetler"""
        menu = current_menu.submenu(self.module_name)
        return any(map(lambda x: x.visible, menu.children))

    def is_enabled(self):
        """Flask menu registry icin visible_when callbacki"""
        if len(self.module_name.split('.')) > 1:
            # Eger module submodule ise gorunurlugu visible cocugunun olup olmamasina bagli.
            return self.has_visible_child()

        return self.fulfill(None) and self.has_visible_child()


def set_system_user_info():
    """config.py'da tanimli olan SYSTEM_USER'in idsini ve Person idsini redis'e kaydeder."""
    from zopsedu.auth.models.auth import User
    from zopsedu.models import Person

    system_user_name = current_app.config['SYSTEM_USER_NAME']

    system_user_info = DB.session.query(User.id.label("user_id"),
                                        Person.id.label("person_id")).join(Person).filter(
        User.username == system_user_name).first()

    system_user = {
        "user_id": system_user_info.user_id,
        "person_id": system_user_info.person_id
    }

    system_user_json = json.dumps(system_user)

    current_app.extensions['redis'].set(system_user_name, system_user_json)


def user_activity_message_index_controll():
    from zopsedu.lib.user_activity_messages import USER_ACTIVITY_MESSAGES
    message_index_list = []
    number_of_user_activity_messages = 0
    for user_activity_message in USER_ACTIVITY_MESSAGES.values():
        for user_activiyt_tuple in user_activity_message.values():
            message_index_list.append(user_activiyt_tuple.type_index)
            number_of_user_activity_messages += 1

    if len(set(message_index_list)) != number_of_user_activity_messages:
        raise IndexError("USER_ACTIVITY_MESSAGES değişkeninde aynı index 2 defa kullanılmıştır. "
                         "Lütfen dikkat ediniz.")


@app.before_first_request
def before_first_request():
    """
    App'in aldığı İLK istek öncesinde çalışan pre-request hook'udur.
    anonim user için session'da kullanılacak bilgiler redis'e yazılır.

    """
    SessionHandler.anonymous_user_set_cache()
    set_system_user_info()
    SessionHandler.universite_id()
    user_activity_message_index_controll()
    init_mail()


@app.before_request
def before_request():
    """
    Her istek öncesinde çalışan pre-request hook'udur. Eğer session içine bir
    `access_token` yerleştirilmemiş ise jwt ile ürettiği token'ı aynı anahtar
    isim altına yerleştirir.

    """
    if 'access_token' not in session:
        session['access_token'] = create_access_token(identity=session.sid)
    session['activity_context'] = uuid4().hex

    SessionHandler.anonymous_user_set_session()


@app.after_request
def after_request(response):
    """
    Her istek sonrasinda çalışan post-request hook'udur.

    """
    if 'context' in session:
        del session['activity_context']
    return response


@app.babel_instance.localeselector
def get_locale():
    """how to get the locale is defined by you.
    Match by the Accept Language header::
        match = app.config.get('BABEL_SUPPORTED_LOCALES', ['en', 'zh'])
        default = app.config.get('BABEL_DEFAULT_LOCALES', 'en')
        return request.accept_languages.best_match(match, default)
    """
    # this is a demo case, we use url to get locale
    code = request.args.get('lang', 'tr')
    return code


# makrolar dahil her yerde erisilebilir sekilde
# kullanilabilecek template fonksiyonlari bu sekilde
# kaydediyoruz. template icinde fonksiyon adi ile
# cagrilarak kullanilabiliyor.
@app.template_global()
def uuid():
    """Generates unique identifiers"""
    return uuid4().hex


@app.template_global()
def jenumerate(iterable):
    """Enumerate"""
    return enumerate(iterable)


@app.template_global()
def jinja_zip(*args):
    """
    Jinja zip template function.

    Args:
        *args:

    Returns:
        list of tuples

    """
    return zip(*args)


@app.template_global()
def jlist(iterable):
    """
    Jinja list template function.

    Args:
        iterable:

    Returns:

    """
    return list(iterable)


@app.template_global()
def timestamp_to_strftime(float_time):
    """Timestamp olarak kaydedilen degeri ilgili formatta string olarak formatlar"""
    return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(float_time))


@app.template_global()
def get_datetime_now():
    return datetime.now()


@app.template_global()
def date_to_string(date):
    """Date objesini belirli formatta date stringine cevirir"""
    return date.strftime(app.config["DATE_FORMAT"])


@app.template_global()
def datetime_to_string(date):
    """Date objesini belirli formatta datetime stringine  cevirir"""
    return date.strftime(app.config["DATETIME_FORMAT"])


@app.template_global()
def num_to_words(number):
    """number to words"""
    return num2words(float(number), lang="tr", to="currency").upper()


# ozel template fonksiyonlari kaydediyoruz. fonsiyonlar
# tanimlanir veya import edilir, dekore edilmis fonsiyon
# ornekteki gibi bir dict donmelidir. her key template icinde
# kullanilacak fonsiyon adina denk gelir.
# makro importlari icinde kullanilacaksa with context ifadeleri
# ile import yapilmalidir.
@app.context_processor
def custom_template_functions():
    """Custom template functions"""
    return dict()


@app.route('/index', endpoint='index')
@app.route('/')
@register_menu(app, '.', 'Home')
def index():
    """Index Page"""
    return redirect(url_for('anasayfa.BapAnasayfaView:bap_anasayfa'))


@app.route('/')
@register_menu(app, '.anasayfa', 'BAP Anasayfa', order=5)
def anasayfa():
    """BAP anasayfa menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap', 'BAP', visible_when=AktifModulMenu('bap').is_enabled)
def bap():
    """Bap menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap.proje', 'Proje', order=1,
               visible_when=AktifModulMenu('bap.proje').is_enabled)
def bap_proje():
    """ Bap Proje İslemleri menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap.yk_toplanti', 'YK Toplantı', order=4,
               visible_when=AktifModulMenu('bap.yk_toplanti').is_enabled)
def bap_yk_toplanti():
    """YK Toplanti menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap.butce', 'Bütçe', order=5,
               visible_when=AktifModulMenu('bap.butce').is_enabled)
def bap_butce():
    """Butçe menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap.satinalma', 'Satınalma', order=6,
               visible_when=AktifModulMenu('bap.satinalma').is_enabled)
def bap_satinalma():
    """Satınalma menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap.yolluk', 'Yolluk', order=7,
               visible_when=AktifModulMenu('bap.yolluk').is_enabled)
def bap_yolluk():
    """Yolluk menu item"""
    pass


@app.route('/')
@register_menu(app, '.bap.demirbas', 'Demirbaş', order=8,
               visible_when=AktifModulMenu('bap.demirbas').is_enabled)
def bap_demirbas():
    """Demirbas menu item"""
    pass


@app.route('/')
@register_menu(app, '.ebys', 'EBYS', order=3, visible_when=AktifModulMenu('ebys').is_enabled)
def ebsy():
    """
    Uygulama Ebsy menu item
    """
    pass


@app.route('/')
@register_menu(app, '.yonetim', 'Yönetim', order=2, visible_when=AktifModulMenu('yonetim').is_enabled)
def yonetim():
    """Ayarlar menu item"""
    pass


@app.route('/')
@register_menu(app, '.yonetim.bap', 'BAP Yönetimi', order=0, visible_when=AktifModulMenu('yonetim.bap').is_enabled)
def yonetim_bap_ayarlari():
    """Ayarlar menu item"""
    pass


@app.route('/')
@register_menu(app, '.yonetim.ana_sayfa', 'Ana Sayfa Yönetimi',
               visible_when=AktifModulMenu('yonetim.ana_sayfa').is_enabled)
def yonetim_ana_sayfa_ayarlari():
    """Ayarlar menu item"""
    pass


@app.route('/')
@register_menu(app, '.yonetim.yetki_yonetimi',
               'Yetki Yönetimi', order=1, visible_when=AktifModulMenu('yonetim.yetki_yonetimi').is_enabled)
def yonetim_yetki_yonetimi():
    """Sistem Ayarlari rol yonetimi menu item"""
    pass


@app.route('/')
@register_menu(app, '.yonetim.personel_yonetimi', 'Personel Yönetimi', order=2,
               visible_when=AktifModulMenu('.yonetim.personel_yonetimi').is_enabled)
def yonetim_personel_yonetimi():
    """Personel menu item"""
    pass


@app.route('/')
@register_menu(app, '.yonetim.firma_yonetimi', 'Firma Yönetimi',
               visible_when=AktifModulMenu('yonetim.firma_yonetimi').is_enabled)
def bap_firma_menu():
    """Firma menu item"""
    pass


@app.route('/')
@register_menu(app, '.sistem_takibi', 'Sistem Takibi', visible_when=AktifModulMenu('sistem_takibi').is_enabled, order=3)
def sistem_takibi():
    """
    Uygulama Genele Ayarlar menu item
    """
    pass


@app.template_filter('currency')
def tr_currency_filter(number):
    """
    Turk Lirasi template filter

    Args:
        number (float): formatlanacak sayi

    Returns:
        (str): formatlanmis string

    """
    return format_currency(number, 'TL', '#,##0.00 ¤¤¤', locale='tr_TR')


app.jinja_env.filters['tr_currency'] = tr_currency_filter
app.jinja_env.add_extension('jinja2.ext.do')


@app.template_global()
def is_visible(menu_path, item=current_menu):
    """Verilen pathin gorunur olup olmamasina gore True veya False doner"""
    menu_path = menu_path.split('.')
    head, *tail = menu_path
    if item:
        try:
            item = item._child_entries.get(head)  # pylint: disable=protected-access
            if head and not tail and item.visible:
                return True
            if tail:
                return is_visible('.'.join(tail), item=item)
        except AttributeError:
            raise AttributeError('Boyle bir menu pathi bulunmamaktadir.')
    return False


@app.template_global()
def is_ebys_enable():
    if 'ebys' in app.config.get('ENABLED_MODULES'):
        return True
    return False


@app.template_global()
def has_perm(endpoint_name):
    """
    Yetki var mi diye kontrol eder.
    İlgili endpoint keyi rediste varmı kontrolunu yapar. Eğer yoksa db den permission name i alip
    redise kaydeder.
    """
    cache = current_app.extensions['redis']
    permission_cache_key = app.config['PERMISSIONS_OF_ENDPOINT_CACHE_KEY'].format(
        endpoint=endpoint_name)
    if not cache.smembers(permission_cache_key):
        permission = DB.session.query(Permission).filter(
            Permission.endpoint_name == endpoint_name).first()
        if permission:
            cache.sadd(permission_cache_key, permission.name)
    perms = cache.sinter(
        permission_cache_key,
        current_app.config['ROLES_PERMISSIONS_CACHE_KEY'].format(role_id=session['current_role'])
    )

    return perms


@app.template_global()
def menu_icon():
    icon_dict = [{
        "Gelen Kutusu": "icons8-gmail",
        "BAP": "icons8-flow-chart",
        "BAP Projeleri": "icons8-add-property",
        "Proje": "icons8-add-property",
        "YK Toplantı": "icons8-crowd-of-people-2",
        "Firma": "icons8-management-2",
        "Yönetim": "icons8-administrative-tools",
        "BAP Yönetimi": "icons8-classroom",
        "Firma Yönetimi": "icons8-new-job",
        "Yetki Yönetimi": "icons8-computer-support",
        "Ana Sayfa Yönetimi": "icons8-classroom",
        "Personel Yönetimi": "icons8-batch-assign",
        "Sistem Takibi": "icons8-accounting",
        "BAP Anasayfa": "icons8-globe",
        "Bütçe": "icons8-accounting",
        "Yolluk": "icons8-fast-browsing",
        "Demirbaş": "icons8-e-learning",
        "Satınalma": "icons8-create-2",
        "EBYS": "icons8-agreement",
        "Kontrol Paneli": "icons8-combo-chart"
    }, {"Gelen Kutusu": "menu-title",
        "BAP": "menu-title",
        "Yönetim": "menu-title",
        "Sistem Takibi": "menu-title",
        "BAP Anasayfa": "menu-title",
        "EBYS": "menu-title",
        "Kontrol Paneli": "menu-title",
        "BAP Projeleri": "menu-title",
        }]
    return icon_dict


@app.template_global()
def rektor_menu_icon():
    icon_dict = [{
        "Bilimsel Yayınlar": "icons8-gmail",
        "Bilimsel Projeler": "icons8-flow-chart",
        "Atıflar ve Tanınırlık": "icons8-crowd-of-people-2",
        "Patent": "icons8-management-2",
        "Ödüller": "icons8-administrative-tools",
        "Bilimsel Faaliyetler": "icons8-classroom",
        "Bilimsel Etkinlikler": "icons8-new-job",
        "Personel": "icons8-computer-support",
    }, {"Gelen Kutusu": "menu-title",
        "BAP": "menu-title",
        "Yönetim": "menu-title",
        "Sistem Takibi": "menu-title",
        "BAP Anasayfa": "menu-title",
        "EBYS": "menu-title",
        "Kontrol Paneli": "menu-title"
        }]
    return icon_dict


@app.template_global()
def is_role(role_name):
    """Rol Kontrolu Yapar."""
    current_role_name = session['current_role_name']
    if current_role_name == role_name:
        return True
    return False


@app.template_global()
def fullfills(custom_requirement):
    """Ozel kosullara gore yetki kontrolu Yapar."""
    return custom_requirement.fulfill(user=current_user)


@app.template_global()
def get_logo_url():
    """Universite ID'sini kullanarak site logosunun url ini return eder."""
    universite_id = SessionHandler.universite_id()
    result = DB.session.query(SiteAyarlari).options(load_only('logo')).filter_by(
        universite_id=universite_id).first()
    logo_url = None
    if result and result.logo:
        logo_url = current_app.wsgi_app.url_for(result.logo.path)
    return logo_url


@app.template_global()
def get_avatar_url():
    """Universite ID'sini kullanarak site logosunun url ini return eder."""
    result = DB.session.query(User).options(load_only('avatar')).filter_by(
        id=current_user.id).first()
    avatar_url = None
    if result and result.avatar:
        avatar_url = current_app.wsgi_app.url_for('{{ request.url_root }}' + result.avatar.path)
    return avatar_url


@app.template_global()
def get_app_version():
    """config version bilgisini return eder."""
    version = current_app.config.get('VERSION')
    return version


@app.template_global()
def get_sablon_logo_url():
    universite_id = SessionHandler.universite_id()
    result = DB.session.query(SiteAyarlari).options(load_only('logo')).filter_by(
        universite_id=universite_id).first()
    logo_url = '/static/assets/img/brand-logo2.png'
    if result and result.logo:
        logo_url = current_app.wsgi_app.url_for(result.logo.path)
    sablon_logo_url = "{}{}".format(request.url_root.strip('/'), logo_url)
    return sablon_logo_url


# pylint: disable=unused-argument
@app.errorhandler(Exception)
@app.errorhandler(SQLAlchemyError)
@app.errorhandler(500)
def custom_error_handler(exc):
    """
    Flask abort methodu ile raise edilen "return abort(500)", SQLAlchemyError(Sqlalchemy genel
    exception classi) ve Exception(Genel exception classi) hatalarini yakalayip loglar.
    Kullaniciyi error_title, error_message ve error_description parametreleriyle ozel hata
    sayfasina yonlendirir.
    """
    return render_error_page(title="500")


@app.errorhandler(404)
def custom_error_404(exc):
    """
    Flask abort methodu ile raise edilen "return abort(404)" hatasini yakalayip loglar.
    Kullaniciyi error_title, error_message ve error_description parametreleriyle ozel hata
    sayfasina yonlendirir.
    """
    error_title = _("404")
    error_message = _("Aradığınız Sayfa Bulunamadı")
    error_description = _("Ulaşmaya çalıştığınız sayfa bulunamadı. Lütfen kontrol edip tekrar "
                          "deneyiniz.")
    return render_error_page(title=error_title,
                             message=error_message,
                             description=error_description)


def render_error_page(title=_("Hata"),
                      message=_("Sistemde Bir Hata Oluştu"),
                      description=_("Oluşan hata bildirildi. Lütfen daha sonra tekrar deneyiniz.")):
    """
    İlgili request session i rollback yapip hatayi loglar ve ozel hata sayfasini gerekli
    parametreler ile render eder.
    Args:
        title: error title
        message: error message
        description: error description

    Returns: rendered template

    """
    CustomErrorHandler.error_handler()

    return render_template('ozel_hata_sayfasi.html',
                           error_title=title,
                           error_message=message,
                           error_description=description)

# pylint: enable=unused-argument
