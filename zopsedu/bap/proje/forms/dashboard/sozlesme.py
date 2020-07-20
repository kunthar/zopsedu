"""Proje Sozlesme Form Modülü"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import FileField

from zopsedu.lib.form.validators import FileExtensionRestriction


class SozlesmeYukleForm(FlaskForm):
    """SozlesmeYukleForm Form Classi"""
    sozlesme_file = FileField(_("Sözleşmeyi Yükleyiniz"),
                              validators=[FileExtensionRestriction(error_message="Dosya uzantısı kabul edilmemektedir.")])
