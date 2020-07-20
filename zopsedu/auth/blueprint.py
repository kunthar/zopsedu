"""AUTH MODULÜ"""
from flask import Blueprint
from zopsedu.auth.views import AuthView

# pylint: disable=invalid-name
# auth url prefix flask-classful view adından geliyor.
# '/auth/login', '/auth/logout' gibi
auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder='templates/'
)

AuthView.register(auth_bp, route_base="/auth")

# pylint: enable=invalid-name
