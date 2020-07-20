"""Mevlana Views"""
from flask import render_template, request, url_for, redirect
from flask_classful import route

from zopsedu.mevlana.forms import ogrenci_basvuru


@route('/ogrenci-basvuru', methods=["GET", "POST"])
# @login_required
def bilgi_formu():
    """Mevlana form"""
    form = ogrenci_basvuru.StudentInformationForm(request.form)
    if request.method == 'POST':
        return redirect(url_for('ping'))
    return render_template(
        'mevlana/mevlana.html', form=form)


@route('/kaydet', methods=["POST"])
def kaydet():
    """Farabi form"""
    return render_template('mevlana/thanks.html')
