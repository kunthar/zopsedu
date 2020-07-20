'''
   This is the Anonymous object for representing an anonymous user.
'''

from flask_login.mixins import AnonymousUserMixin

from zopsedu.auth.models.auth import Role
from zopsedu.lib.sessions import SessionHandler


class Anonymous(AnonymousUserMixin):
    username = 'anonymous'
    _anonymous_user = {}
    _anonymous_role = None

    @property
    def anonymous_user(self):
        if Anonymous._anonymous_user:
            return Anonymous._anonymous_user
        Anonymous._anonymous_user = SessionHandler.anonymous_user_get_cache()
        return Anonymous._anonymous_user

    @property
    def anonymous_role(self):
        if Anonymous._anonymous_role:
            return Anonymous._anonymous_role
        Anonymous._anonymous_role = Role.query.filter_by(
            name=self.anonymous_user['anonymous_role_name']).first()
        return Anonymous._anonymous_role

    def get_role(self, role_id):
        return self.anonymous_role

    def get_id(self):
        return self.anonymous_user['anonymous_user_id']

    @property
    def id(self):
        return self.get_id()
