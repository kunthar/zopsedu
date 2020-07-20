"""App config module"""
import os

BASE_DIR = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))
if os.path.islink(BASE_DIR):
    BASE_DIR = os.readlink(BASE_DIR)


class BaseConfig(object):
    """Base Configuration Object"""
    VERSION = '0.4.1.4'
    DEBUG = False
    TESTING = False
    SECRET_KEY = "Zr4t7w!asasdBgW32RgUkXp2s5v8x/A?D(G+KbPeShVmYq3t6w9z$B&E)H@McQfT" #random olarak uretin. openssl rand -base64 64
    SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:5000')
    SECRET_SALT_KEY = "aPdSgVkYp3s6v9y$B78u3yHH!z%C*F)J@NcRfUjXn2r5u8x/A?D("   # random olarak uretin. openssl rand -base64 64

    # sqlite :memory: identifier is the default if no filepath is present
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DEPOT_STORAGE_PATH = "{}/{}".format(BASE_DIR, 'uploads')

    # cache
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_URL = "redis://{}:6379/0".format(os.getenv('REDIS_HOST', 'localhost'))
    CACHE_FORM_PREFIX = "ZOPSEDU:FORMS:{form_name}"

    # session
    SESSION_CACHE_KEY_PREFIX = "Sessions"
    TOKEN_CACHE_KEY_PREFIX = "Tokens"
    TOKEN_HEADER = 'X-Auth-Token'
    SESSION_COOKIE_EXPIRES = 500
    SESSION_TIMEOUT = 500

    # localization
    WTF_I18N_ENABLED = True
    BABEL_DEFAULT_LOCALE = 'tr'
    BABEL_TRANSLATION_DIRECTORIES = 'locale'
    # SERVER_NAME = "localhost"

    # app specific

    MODULE_NAMES = [
        'bap',
        'personel',
        'farabi',
        'erasmus',
        'mevlana',
        'samples',
        'yonetim',
        'bap_yonetimi',
        'icerik',
        'sistem_takibi',
        'akademik_performans'
    ]

    SUB_MODULE_NAMES = [
        'bap_proje',
        'bap_satın_alma'
    ]

    ENABLED_MODULES = [
        'bap',
        'personel',
        'farabi',
        'erasmus',
        'mevlana',
        'samples',
        'yonetim',
        'bap_yonetimi',
        'sistem_takibi',
        'icerik',
        'akademik_performans',
    ]


    # EBYS modulu hazirdir ancak sozlesme yapilamadigi icin acik hale getirilememistir.
    EBYS_PASSWORD_ENC = os.getenv('EBYS_PASSWORD_ENC', 'getyourownpass')
    EBYS_USERNAME_ENC = os.getenv('EBYS_USERNAME_ENC', 'getyourownuser')
    EBYS = "EBYS"

    # authhorization
    ALL_PERMISSIONS_CACHE_KEY = "Permissions"
    PERMISSIONS_OF_ENDPOINT_CACHE_KEY = "Permissions:{endpoint}"
    ALL_IMPORT_PATH_OF_ENDPOINTS_CACHE_KEY = "ImportPathsOfEndpoints"
    ROLES_PERMISSIONS_CACHE_KEY = "Roles:{role_id}:Permissions"
    USER_LAST_LOGIN_ROLE_ID_CACHE_KEY = "User:{user_id}:LastLoginRoleId"
    USER_LAST_LOGIN_ROLE_NAME_CACHE_KEY = "User:{user_id}:LastLoginRoleName"

    UNIVERSITE_ID = "UniversiteId"
    UNIVERSITE_CONFIG_ID = 0

    DATETIME_FORMAT = "%d.%m.%Y %H:%M"
    DATE_FORMAT = "%d.%m.%Y"

    CRUD_LOG = os.getenv('CRUD_LOG', False)
    SYSTEM_USER_NAME = "system_user"
    SYSTEM_USER_EMAIL = "system_user@yourname.com"



    MAIL_SERVER = os.getenv('MAIL_SERVER', 'mail.server.x')
    MAIL_PORT = os.getenv('MAIL_PORT', '587')
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', 0))
    MAIL_USE_TLS = int(os.getenv('MAIL_USE_TLS', 0))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'mail@username.x')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'mail@username.x')
    MAIL_MAX_EMAILS = os.getenv('MAIL_MAX_EMAILS', None)

    # Works different than expected behaviour. 1 Means don't suppress 0 Means suppress...
    MAIL_SUPPRESS_SEND = int(os.getenv('MAIL_SUPPRESS_SEND', 1))


class DevelopmentConfig(BaseConfig):
    """Development Configuration Object"""
    DEBUG = True
    SECRET_KEY = "development"
    SECRET_SALT_KEY = "development"

    SQLALCHEMY_DATABASE_URI = 'postgresql://zopsedu:zopsedu@localhost:5432/zopsedu'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SESSION_COOKIE_EXPIRES = 60 * 60 * 50
    SESSION_TIMEOUT = 60 * 60 * 50
    CRUD_LOG = False


class TestingConfig(DevelopmentConfig):
    """Test Configuration Object based on Development"""
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production Configuration Object"""
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
        os.getenv('POSTGRES_USER', 'username'),
        os.getenv('POSTGRES_PASSWORD', 'password'),
        os.getenv('POSTGRES_HOST', 'localhost'),
        os.getenv('POSTGRES_DB', 'database')
    )

    SESSION_COOKIE_EXPIRES = 8 * 60 * 60
    SESSION_TIMEOUT = 8 * 60 * 60
    CRUD_LOG = False if os.getenv('CRUD_LOG', True) == 'False' else True


CONFIG = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "production": ProductionConfig()
}


def configure_app(app):
    """
    Configure and return app object
    Args:
        app (app): flask app object

    Returns:
        (app): configured app

    """
    config_name = os.getenv('FLASK_CONFIGURATION', 'development')
    app.config.from_object(CONFIG[config_name])
    return app
