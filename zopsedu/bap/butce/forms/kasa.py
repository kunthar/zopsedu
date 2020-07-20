"""Kasa ve baglantili formlarindan olusur"""
from flask_babel import gettext as _
from wtforms import Form, StringField
from wtforms.meta import DefaultMeta
from wtforms.validators import Length

from zopsedu.lib.form.fields import ZopseduDecimalField
from zopsedu.lib.form.validators import DecimalLength


class Kasa(Form):
    """
    Bap kasa formu
    """
    adi = StringField(_("Kasa Adı"), validators=[Length(max=100)])


class KasaGirdiFormu(Form):
    """
    Bap ana kasalarina yapilan butce girdilerini temsil eden form
    """

    class Meta(DefaultMeta):
        locales = ["tr"]

    aciklama = StringField(_('Açıklama'), render_kw={"class": "form-control"})
    tutar = ZopseduDecimalField(_('Tutar'),
                                validators=[
                                    DecimalLength(max_length=12,
                                                  error_message="Tutar için en fazla 12 "
                                                                "haneli bir değer girebilirsiniz")
                                ])
