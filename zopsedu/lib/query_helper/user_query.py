from sqlalchemy import or_

from zopsedu.auth.models.auth import UserRole, User,Role
from zopsedu.lib.db import DB
from zopsedu.models import Person


def bap_admin_ids():
    bap_admin_ids = DB.session.query(Person.id.label("person_id")). \
        join(Role, Role.name == "BAP Admin").join(UserRole, UserRole.role_id == Role.id). \
        join(User, UserRole.user_id == User.id). \
        filter(Person.user_id == User.id). \
        all()

    return bap_admin_ids


def bap_yetkili_ids():
    bap_yetkili_ids = DB.session.query(Person.id.label("person_id")). \
        join(Role, Role.name == "BAP Yetkilisi").join(UserRole, UserRole.role_id == Role.id). \
        join(User, UserRole.user_id == User.id). \
        filter(Person.user_id == User.id). \
        all()

    return bap_yetkili_ids


def bap_yetkili_and_admin_ids():
    bap_yetkili_and_admin_ids = DB.session.query(Person.id.label("person_id")). \
        join(Role, or_(Role.name == "BAP Yetkilisi",Role.name == "BAP Admin")).\
        join(UserRole, UserRole.role_id == Role.id). \
        join(User, UserRole.user_id == User.id). \
        filter(Person.user_id == User.id). \
        all()

    return bap_yetkili_and_admin_ids
