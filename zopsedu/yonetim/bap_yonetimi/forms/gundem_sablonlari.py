"""GundemSablon Formlari"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import SubmitField, SelectField, FormField

from zopsedu.bap.models.helpers import GundemTipi, SablonKategori
from zopsedu.lib.form.fields import SummerNoteField


class GundemSablonEkleForm(FlaskForm):
    """GundemSablon Ekleme Formu"""
    sablon_tipi = SelectField(label=_('Şablon Tipi '),
                              choices=GundemTipi.choices(),
                              coerce=GundemTipi.coerce)

    kategori = SelectField(label=_('Kategori '),
                           choices=SablonKategori.choices(),
                           coerce=SablonKategori.coerce)
    aciklama = SummerNoteField(label=_('Açıklama '))
    karar = SummerNoteField(label=_('Karar '))
    ekle = SubmitField(label=_('Ekle'))


class GundemSablonDuzenleForm(FlaskForm):
    """GundemSablon Duzenleme Formu"""
    duzenle = FormField(GundemSablonEkleForm)
    duzenle_btn = SubmitField(label=_('Düzenle'))
