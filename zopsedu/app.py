"""Zopsedu main app module"""
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_wtf import CSRFProtect

from zopsedu.config import configure_app
from zopsedu.lib.sessions import CustomSessionInterface
from zopsedu.lib.db import DB

# pylint: disable=invalid-name
app = Flask("zopsedu")
app = configure_app(app)

session_opts = {
    'session.cookie_expires': app.config.get('SESSION_COOKIE_EXPIRES', 30),
    'session.timeout': app.config.get('SESSION_TIMEOUT', 30),
    'cache_key_prefix': app.config.get('SESSION_CACHE_KEY_PREFIX', 'Sessions'),
    'token_key_prefix': app.config.get('TOKEN_CACHE_KEY_PREFIX', 'Tokens'),
    'token_header': app.config.get('TOKEN_HEADER', 'X-Auth-Token'),
}

redis_store = FlaskRedis(strict=False)
redis_store.init_app(app)
app.session_interface = CustomSessionInterface(
    session_opts,
    app.extensions['redis'],
)
# pylint: enable=invalid-name

# csrf protection
CSRFProtect(app)

# init db object
DB.init_app(app)
DB.app = app

job_store = SQLAlchemyJobStore(url=app.config.get('SQLALCHEMY_DATABASE_URI'),
                              metadata=DB.metadata,
                              engine=DB.engine)
scheduler = APScheduler()

Migrate(app, DB)
