"""Proje Turu formu ek_dosya ayarlari kismi"""

from wtforms import Form, StringField, BooleanField, FormField
from wtforms import validators
from flask_babel import lazy_gettext as _

from zopsedu.lib.form.fields import HiddenIntegerField, CustomFileField
from zopsedu.lib.form.validators import FileExtensionRestriction


class Dosya(Form):
    """
    Proje türü dosya formu
    """
    adi = StringField(_("Dosya Adı", render_kw={"class": "form-control"}),
                      render_kw={"class": "form-control"})
    aciklama = StringField(_("Açıklama"),
                           render_kw={"class": "form-control"})
    # todo: dosya türleri arasından coklu secim yapılarak oluşturulacak
    # turler = SelectMultipleField("Türler",
    #                              choices=[(element, element) for element in PROJE_BELGE_TURLERI])
    file_id = CustomFileField(_("Dosya"), render_kw={"class": "form-control"},
                              validators=[FileExtensionRestriction(
                                  error_message=_(
                                      "Lütfen uzantısı geçerli bir dosya yükleyiniz."))])


class EkDosya(Form):
    """
    Proje türü ekdosya formu
    """
    ek_dosya_id = HiddenIntegerField(validators=[validators.optional()])
    zorunlu_mu = BooleanField(_("Zorunlu Mu ?", render_kw={"class": "form-control"}),
                              default=False)
    proje_icerik_dosyasi_mi = BooleanField(_("Proje içerik dosyası mı ?"),
                                           default=False)
    belgenin_ciktisi_alinacak_mi = BooleanField(_("Belge çıktısı alınacak mı ?"),
                                                default=False)
    belge = FormField(Dosya)
