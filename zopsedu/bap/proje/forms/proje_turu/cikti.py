"""Proje Turu formu Cikti kismi"""
from wtforms import Form, StringField, SelectField, BooleanField
from wtforms import validators
from flask_babel import lazy_gettext as _

from zopsedu.lib.db import DB
from zopsedu.models import Sablon
from zopsedu.lib.form.fields import HiddenIntegerField
from zopsedu.bap.models.helpers import GorunurlukSecenekleri


class Cikti(Form):
    """
    Proje türü cıktı formu
    """
    cikti_id = HiddenIntegerField(validators=[validators.optional()])
    adi = StringField("Çıktı Adı", render_kw={"class": "form-control"})
    gorunurluk = SelectField("Görünürlük",
                             choices=GorunurlukSecenekleri.choices(),
                             default=GorunurlukSecenekleri.sadece_yonetici,
                             coerce=GorunurlukSecenekleri.coerce,
                             render_kw={"class": "form-control"})
    belge_ciktisi_alinacak_mi = BooleanField("Belgenin Çıktısı Alınacak Mı?",
                                             default=False)
    # sablon_id = CustomFileField(_("Şablon Ekle"), render_kw={"class": "form-control"})
    cikti_sablonu_id = SelectField(_("Çıktı Şablonu"),
                                   choices=[],
                                   coerce=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bap_sablon_tipleri = DB.session.query(
            Sablon.id,
            Sablon.adi).filter(Sablon.module_name == "BAP").all()
        if bap_sablon_tipleri:
            self.cikti_sablonu_id.choices = bap_sablon_tipleri
            self.cikti_sablonu_id.default = bap_sablon_tipleri[0]
            self.cikti_sablonu_id.coerce = int
