"""Bap butce kodlari formu ve iliskili formlarindan olusur"""
from flask_wtf import FlaskForm, Form
from wtforms import StringField, FormField, FieldList
from wtforms.validators import ValidationError, Length
from flask_babel import lazy_gettext as _

from zopsedu.lib.form.fields import Select2Field


class FonksiyonelKod(Form):
    kod = StringField(_("Kod"), render_kw={"class": "form-control"})
    aciklama = StringField(_("Açıklama"), render_kw={"class": "form-control"})


class FonksiyonelKodlar(FlaskForm):
    fonksiyonel_kodlar = FieldList(FormField(FonksiyonelKod), min_entries=1)


class KDVKodlari(Form):
    kdv_tevkifat_kodu = StringField(_("KDV Tevkifat Kodu"))
    kdv_tevkifat_adi = StringField(_("KDV Tevkifat Adı"))

    kdv_tevkifat_orani = StringField(_("KDV Tevkifat Oranı"),
                                     render_kw={"class": "form-control percent"})


class KurumBankaBilgisi(Form):
    hesap_adi = StringField(_("Hesap Adı"))
    iban = StringField(_("IBAN No"), validators=[Length(max=100)])
    banka_adi = StringField(_("Banka Adı"), validators=[Length(max=100)])
    banka_subesi = StringField(_("Banka Şubesi"), validators=[Length(max=100)])

    vergi_no = StringField(_("Vergi No"))
    vergi_dairesi_id = Select2Field(_('Vergi Dairesi'),
                                    url="/select/vergi-dairesi",
                                    placeholder=_("Vergi Dairesi Adı"))


class ButceKodlari(FlaskForm):
    kurum_adi = StringField(_("Kurum Adı"), validators=[Length(max=255)])
    kurum_kodu = StringField(_("Kurum Kodu"), validators=[Length(max=20)])

    birim_adi = StringField(_("Birim Adı"), validators=[Length(max=255)])
    birim_kodu = StringField(_("Birim Kodu"), validators=[Length(max=20)])

    muhasebe_birimi_adi = StringField(_("Muhasebe Birimi Adı"), validators=[Length(max=255)])
    muhasebe_birimi_kodu = StringField(_("Muhasebe Birimi Kodu"), validators=[Length(max=20)])

    kurum_banka_bilgisi = FormField(KurumBankaBilgisi)
    kdv_kodlari = FormField(KDVKodlari)

    def validate_kurum_kodu(self, _):
        if self.kurum_kodu.data:
            yok_kurum_kodu = self.kurum_kodu.data.split(".")[0]
            if yok_kurum_kodu != "38" and yok_kurum_kodu != "39":
                raise ValidationError(
                    message="Kurum kodu 38 veya 39 ile başlamalıdır ve "
                            "kod düzeyleri nokta ile ayrılmalıdır. (Örn: 39.01.00.00) ")


class HesapKodlariSearch(FlaskForm):
    kod = StringField(_("Hesap Kodu"))
    aciklama = StringField(_("Hesap Kodu Açıklaması"))
