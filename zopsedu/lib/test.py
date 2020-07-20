"""Test utils"""
from copy import deepcopy

from flask import session, request, redirect, url_for, render_template
from flask_jwt_extended import create_access_token
from flask_login import login_required
from flask_testing import TestCase

from zopsedu.app import app
from zopsedu.lib.form import forms


def before_request_proxy():
    """
    app nesnesine kayıt edilmiş before_request metodunun test amacıyla
    yaratılmış kopyasıdır.
    """
    if 'access_token' not in session:
        session['access_token'] = create_access_token(identity=session.sid)


def ping_proxy():
    """
    app nesnesine kayıt edilmiş ping metodunun test amacıyla
    yaratılmış kopyasıdır.

    """
    return "pong"


@login_required
def date_proxy():
    """
    app nesnesine kayıt edilmiş date metodunun test amacıyla
    yaratılmış kopyasıdır.

    """
    form = forms.SexAndALanguageForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('ping'))
    return render_template("dev/samples/form_with_date_picker.html", form=form)


def create_app_proxy():
    """
    Testlerde kullanılacak app nesnesini yaratıp, blueprintlerde bulunmayıp app
    içinde kaydedilmiş view ve request hooklarını test app nesnesine kaydederek
    test app nesnesini döndüren metottur.
    """
    app_proxy = deepcopy(app)
    app_proxy.before_request_funcs.setdefault(None, []).append(
        before_request_proxy)
    app_proxy.add_url_rule(
        '/ping',
        endpoint='ping',
        view_func=ping_proxy,
        methods=['GET'],
    )
    app_proxy.add_url_rule(
        '/dev/sample/form/date',
        endpoint='date',
        view_func=date_proxy,
        methods=['GET', 'POST'],
    )
    return app_proxy


class ZopseduTestCase(TestCase):
    """Temel test sınıfı"""
    def create_app(self):
        """Testlerde kullanılacak app nesnesini döndüren sınıf"""
        return create_app_proxy()
