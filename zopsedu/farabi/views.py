"""Farabi Views"""
from flask import render_template

from zopsedu.farabi.form import FarabiForm
from flask_classful import route


@route('/ogrenci-basvuru', methods=["GET"])
# @login_required
def ogrenci_basvuru():
    """Farabi form"""
    farabi_form = FarabiForm()
    return render_template('farabi_form/farabi_form.html', farabi_form=farabi_form)


@route('/kaydet', methods=["POST"])
def kaydet():
    """Farabi form"""
    farabi_form = FarabiForm()
    return render_template('farabi_form/thanks.html', farabi_form=farabi_form)
