"""Erasmus Views"""
from flask import render_template
from flask_classful import route

from zopsedu.erasmus.form import ErasmusForm




@route('/ogrenci-basvuru', methods=["GET"])
# @login_required
def ogrenci_basvuru():
    """erasmus form"""
    erasmus_form = ErasmusForm()
    return render_template('erasmus_form/form.html', erasmus_form=erasmus_form)


@route('/kaydet', methods=["POST"])
def tesekkur():
    """after success erasmus form"""
    return render_template('erasmus_form/thanks.html')
