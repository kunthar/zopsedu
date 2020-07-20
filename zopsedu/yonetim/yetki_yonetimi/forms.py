"""Yonetim Form Modulu"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

from zopsedu.lib.form.fields import MultiCheckboxField


class KisiSearchForm(FlaskForm):
    kisi_ad = StringField("Kullanıcı Adı")
    kisi_soyad = StringField("Kullanıcı Soyadı")


class RolEkleForm(FlaskForm):
    """Rol Ekleme Formu"""
    rol_adi = StringField(_("Rol Adı"))

    iptal = SubmitField(_("Vazgeç"))
    kaydet = SubmitField(_("Kaydet"))


class RolAtamaForm(FlaskForm):
    roller = MultiCheckboxField(label='Rol Listesi', coerce=int)
    ata = SubmitField('Ata')




