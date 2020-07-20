"""SESSIONS"""
import json
from uuid import uuid4
from datetime import datetime, timedelta

from flask import session, current_app, render_template
from flask.sessions import SessionInterface, SessionMixin

from werkzeug.datastructures import CallbackDict
from werkzeug.exceptions import BadRequest
from redis.exceptions import RedisError

from zopsedu.auth.models.auth import Role, User, UserRole
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import SiteAyarlari


class DataStoreClientException(Exception):
    """
    CustomSessionInterface sınıfına datastore nesnesi geçilmediği takdirde
    fırlatılacak Exception'dır.
    """
    pass


class CustomSession(CallbackDict, SessionMixin):  # pylint: disable=too-many-ancestors
    """
    Özelleştirilmiş session sınıfı.
    """

    def __init__(self, initial=None, sid=None, new=False, needs_cookie=False):
        def on_update(ins):
            """
            Güncelleme olup olmadığını tespit eden method.
            Args:
                ins:

            """
            ins.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False
        self.destroy = False
        self.needs_cookie = needs_cookie

    def delete(self):
        """
        Session nesnesini silen method.

        """
        self.destroy = True


class CustomSessionInterface(SessionInterface):
    """
    Session ilişkilerini ayakta tutan sınıftır.

    Aşağıda belirtilen proje ve projede belirtilen blog yazısından adapte
    edilmiştir.

    https://github.com/eljrax/flask_token_cookie_sessions
    """
    session_class = CustomSession
    serializer = json

    def __init__(self, session_opts, datastore_client=None):
        """
        Args:
            session_opts (dict): Session özelliklerinin belirtildiği dictionary
                - session.cookie_expires (int):
                - session.timeout: 30,
                - session_cache_prefix (str): default Sessions
                - token_cache_prefix (str): default Tokens
                - token_header: 'X-Auth-Token',
            datastore_client (Redis): Redis client
        """
        self.session_opts = session_opts
        self.token_header = session_opts['token_header']
        self.session_cache_prefix = self.session_opts.get(
            'session_cache_prefix', 'Sessions')
        self.token_cache_prefix = self.session_opts.get(
            'token_cache_prefix', 'Tokens')

        if datastore_client is None:
            raise DataStoreClientException()

        self.datastore_client = datastore_client

    def get_expiration_time(self, app, session):
        """
        Session'ın iptal edileceği zamanın hesaplandığı metoddur.


        Args:
            app : Kalıtıldığı metodun imzasını bozmamak için kullanılmıştır.
            session (CustomSession): CustomSession nesnesi.

        Returns:
            datetime: İptal edilecek zamanı datetime nesnesi olarak döndürür.
        """
        default_expiry = datetime.utcnow() + timedelta(
            seconds=self.session_opts.get('session.cookie_expires', 36000))
        valid_until = session.get('valid_until', None)
        return valid_until or default_expiry

    def get_session_id(self, request, app):
        """
        Session id'sini gönderilmişse çerez üzerinden ya da gönderilen token
        üzerinden elde eden metottur.

        İkisi de mevut ise çerezin önceliği vardır.

        Token geçildiyse, Token, SessionId çiftleri Redis üzerinde
        "Tokens:[token]": [SessionId] şeklinde tutulduğu için
        `token_cache_prefix` ile formatlanarak Redis'ten okunur.

        """

        cookie = request.cookies.get(app.session_cookie_name)
        if cookie:
            return cookie

        try:
            return self.datastore_client.get(
                "{}:{}".format(
                    self.token_cache_prefix,
                    request.headers[self.session_opts['token_header']]
                )
            ).decode()
        except KeyError:
            pass

        try:
            return self.datastore_client.get(
                "{}:{}".format(
                    self.token_cache_prefix,
                    request.get_json()['token']
                )
            ).decode()
        except (TypeError, KeyError, BadRequest):
            pass

        # Session identifier olmadığı için bu yeni bir Session'dır.
        return None

    @staticmethod
    def generate_sid():
        """
        Session id üreten metottur.
        Returns:
            str: Session id döndürür.
        """
        return str(uuid4())

    def needs_cookie(self, request):
        """
        Çerez gönderip göndermemiz gerektiğine karar veren metottur.
        Args:
            request:

        Returns:
            bool: Çerez lazım ya da değil
        """
        needs_cookie = True

        try:
            if self.token_header in request.headers or \
                    'token' in request.get_json():
                needs_cookie = False
        except (json.JSONDecodeError, TypeError):
            pass

        return needs_cookie

    def open_session(self, app, request):
        """
        Her istekte, varsa gelen Session id veya token ile, yoksa yeni Session
        id yaratarak bir Session nesnesi oluşturan metottur.

        Session nesnesi önceden yaratılmış mı diye Redis'e bakılır. Önceden
        var ise Redis'ten okunarak döndürülür, aksi halde yenisi yaratılır ve
        döndürülür.

        Session'lar Redis'e kaydedilirken CustomSessionInterface sınıfının
        serializerı ile serialize edilir. Redis'te sadece str tutabildiğimiz
        için nesne içindeki veri tiplerini kaybetmemek için bu iyi bir yöntem
        olabilir. Serialize edildikten sonra Token'larda olduğu gibi (Tokens),
        bir prefix ve expire time ile Redis'e yazılır.

        Examples:
            Sessions:[SessionId]: {...}

        Args:
            app:
            request:

        Returns:
            CustomSession: Oluşturduğu Session nesnesini döndürür.
        """
        sid = self.get_session_id(request, app)
        needs_cookie = self.needs_cookie(request)

        if not sid:
            # Session daha önce yaratılmamış demektir.
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True,
                                      needs_cookie=needs_cookie)

        #
        key = "{prefix}:{sid}".format(prefix=self.session_cache_prefix, sid=sid)
        val = None
        try:
            val = self.datastore_client.get(key)
        except RedisError as ex:
            print("Redis client get error: %s" % ex)

        if val is not None:
            data = self.serializer.loads(val.decode())
            return self.session_class(data, sid=sid, needs_cookie=needs_cookie)

        return self.session_class(sid=sid, new=True, needs_cookie=needs_cookie)

    def save_session(self, app, session, response):
        """
        Yaratılan ya da güncellenen Session nesnelerinin kaydedildiği metottur.

        Expiration time'ları alarak hem Redis'te hem de gerekliyse çerez
        üzerinde expiration timeları set ederek hem tarayıcıya hem de Redis'e
        kayıt işlemini gerçekleştirir.

        Args:
            app:
            session:
            response:

        """
        domain = self.get_cookie_domain(app)
        key = "{prefix}:{sid}".format(prefix=self.session_cache_prefix,
                                      sid=session.sid)

        if not session or session.destroy:
            try:
                self.datastore_client.delete(key)
            except RedisError as ex:
                print("Redis client delete error: %s" % ex)

            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        expires = self.get_expiration_time(None, session)
        now = datetime.utcnow()
        delta = expires - now
        session_ttl = delta.seconds
        if session_ttl <= 0:
            # Token *just* expired
            return

        val = self.serializer.dumps(dict(session))

        try:
            pipe = self.datastore_client.pipeline()
            pipe.setex(key, val, session_ttl)
            pipe.setex(
                "Tokens:{}".format(session['access_token']),
                session.sid,
                session_ttl
            )
            pipe.execute()

        except RedisError as ex:
            print("Cannot be connected to Redis: %s" % ex)

        if session.needs_cookie:
            response.set_cookie(app.session_cookie_name, session.sid,
                                expires=expires, httponly=True,
                                domain=domain)


class SessionHandler:
    """
    session kullanımını için set,pop,update methodlarını içerir.

    anonim user'ın bilgilerini redis'e yazmak ve okumak için methodlar içerir.

    """

    @staticmethod
    def session_set(**kwargs):
        """
        parametre olarak verilen dict'i session'a
        eğer key daha önce yaratılmamışsa ekler,
        yaratılmışsa güncellemez.

        :param kwargs:
        :return:
        """
        for key, value in kwargs.items():
            if key not in session:
                session[key] = value

    @staticmethod
    def session_update(**kwargs):
        """
        paramtre olarak verilen dict'i session'a
        ekler  eğer key daha önce yaratılmışsa
        günceller.

        :param kwargs:
        :return:
        """
        for key, value in kwargs.items():
            session[key] = value

    @staticmethod
    def session_pop(*args):
        """
        parametre olarak verilen key'leri
        sessiondan çıkartır.

        :param args:
        :return:
        """
        for arg in args:
            if arg in session:
                session.pop(arg)

    @staticmethod
    def session_logout_flush(last_role=None,
                             is_authenticated=False):

        """
        logout olunduğunda session'dan kullanıcı bilgilerini kaldırır.


        :param last_role:
        :param is_authenticated:
        :return:
        """

        SessionHandler.session_update(is_authenticated=is_authenticated,
                                      **last_role)

        SessionHandler.session_pop('current_role_name',
                                   'current_role',
                                   'user_ad_soyad',
                                   'current_user_role')

        session.pop('_flashes', None)

    @staticmethod
    def session_login_set(user=None,
                          user_ad=None,
                          is_authenticated=True):

        """

        login olunduğunda session'a kullanıcı bilgilerini ekler.

        :param user:
        :param user_ad:
        :param is_authenticated:
        :return:
        """

        last_login_role = current_app.extensions['redis'].get(
            current_app.config['USER_LAST_LOGIN_ROLE_ID_CACHE_KEY'].format(user_id=user.id)
        )
        if last_login_role:
            SessionHandler.session_update(current_role=int(last_login_role.decode()))
        else:
            if user.roles:
                SessionHandler.session_update(current_role=user.roles[0].id)
            else:
                anonymous_role = DB.session.query(Role).filter_by(name='anonymous').first()
                user.roles.append(anonymous_role)
                DB.session.commit()
                SessionHandler.session_update(current_role=anonymous_role.id)

        login_user_role = DB.session.query(UserRole). \
            filter_by(user_id=user.id, role_id=session['current_role']).first()
        login_role = login_user_role.role
        perms = [perm.name for perm in login_role.permissions]

        if perms:
            current_app.extensions['redis'].sadd(
                current_app.config['ROLES_PERMISSIONS_CACHE_KEY'].format(
                    role_id=session['current_role']), *perms)

        SessionHandler.session_update(is_authenticated=is_authenticated,
                                      user_ad_soyad=user_ad,
                                      current_role_name=login_role.name,
                                      current_user_role=login_user_role.id)

    @staticmethod
    def anonymous_user_set_cache():

        """
        anonim user bilgilerini redis'e ekler.

        :return:
        """

        role = DB.session.query(Role).filter_by(name='anonymous').first()
        user = User.query.filter(User.username == 'anonymous').first()

        anonymous_user = {'anonymous_role': role.id,
                          'anonymous_role_name': role.name,
                          'anonymous_user_id': user.id,
                          'anonymous_user_name': user.username}
        anonymous_user_json = json.dumps(anonymous_user)

        current_app.extensions['redis'].set('anonymous_user_dict', anonymous_user_json)

    @staticmethod
    def anonymous_user_set_session():

        """

        anonim user bilgilerini redis'den alarak session'a ekler.

        :return:
        """

        if 'current_role' in session:
            return

        anonymous_user = SessionHandler.anonymous_user_get_cache()
        SessionHandler.session_update(
            current_role=anonymous_user['anonymous_role'],
            current_role_name=anonymous_user['anonymous_role_name']
        )

    @staticmethod
    def anonymous_user_get_cache():

        """
        anonim user bilgilerini redis'den almaya yarar.

        :return: anonymous_user
        """
        anonymous_user = current_app.extensions['redis'].get('anonymous_user_dict')
        if anonymous_user:
            return json.loads(anonymous_user)

        SessionHandler.anonymous_user_set_cache()
        return SessionHandler.anonymous_user_get_cache()

    @staticmethod
    def ebys_ayarlari(update=None):
        """
        Ebys Ayarlarını döndürür.

        Eğer ebys ayarları redis'e ekli değilse db'den alır ve redis'e ekler

        """
        ebys_ayarlari = current_app.extensions['redis'].get(current_app.config['EBYS'])
        if ebys_ayarlari and not update:
            return json.loads(ebys_ayarlari)
        try:
            site_ayarlari = DB.session.query(SiteAyarlari).first()
            if site_ayarlari:
                ebys_ayarlari_dict = site_ayarlari.params['ebys_ayarlari']
                password_enc = current_app.config.get('EBYS_PASSWORD_ENC')
                username_enc = current_app.config.get('EBYS_USERNAME_ENC')
                ebys_ayarlari_dict.update({'password_enc': password_enc})
                ebys_ayarlari_dict.update({'username_enc': username_enc})
                ebys_ayarlari = json.dumps(ebys_ayarlari_dict)

                current_app.extensions['redis'].set(current_app.config['EBYS'], ebys_ayarlari)
                return ebys_ayarlari_dict
        except Exception as exc:
            CustomErrorHandler.error_handler(
                hata="Ebys Ayarları DB den okunmaya calisilirken hatayla "
                     "karşılaşıldı.Hata: ".format(exc))

    @staticmethod
    def universite_id():
        """

        Universite Id yi redis e ekler.

        :return:
        """

        universite_id = current_app.extensions['redis'].get(current_app.config['UNIVERSITE_ID'])
        if universite_id:
            universite_id = json.loads(universite_id)
            return universite_id

        try:
            site_ayarlari = DB.session.query(
                SiteAyarlari.universite_id.label("universite_id")).first()
            if site_ayarlari:
                current_app.extensions['redis'].set(current_app.config['UNIVERSITE_ID'],
                                                    site_ayarlari.universite_id)
            universite_id = site_ayarlari.universite_id if site_ayarlari and site_ayarlari.universite_id else current_app.config.get(
                'UNIVERSITE_CONFIG_ID')
        except Exception as exc:
            CustomErrorHandler.error_handler(
                hata="Universite id DB den okunmaya calisilirken hatayla "
                     "karşılaşıldı.Hata: ".format(exc))

        return universite_id

    @staticmethod
    def system_user():
        """
        System user bilgilerini redis'den alır
        System userı eğer redis'de ekli değilse redis'e ekler
        """
        """config.py'da tanimli olan SYSTEM_USER'in idsini ve Person idsini redis'e kaydeder."""

        system_user_name = current_app.config['SYSTEM_USER_NAME']

        system_user_infos = current_app.extensions['redis'].get(system_user_name)
        if system_user_infos:
            return json.loads(system_user_infos)

        from zopsedu.models import Person

        system_user_info = DB.session.query(User.id.label("user_id"),
                                            Person.id.label("person_id")).join(Person).filter(
            User.username == system_user_name).first()


        system_user = {
            "user_id": system_user_info.user_id,
            "person_id": system_user_info.person_id
        }

        system_user_json = json.dumps(system_user)

        current_app.extensions['redis'].set(system_user_name, system_user_json)

        return system_user


    @staticmethod
    def menu_set_session():
        """
        #todo user için rol atama eklendiğinde eklenecek
        menu = session.get("current_role_menu")

        if menu:
            return
        """
        current_role_menu = ' '.join(render_template("menu.html").replace("\n", "").split())
        session['current_role_menu'] = current_role_menu

    @staticmethod
    def menu_delete_session():
        SessionHandler.session_pop('current_role_menu')
