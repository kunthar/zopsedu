"""Ayarlar Form Modulu"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, TextAreaField, FileField, PasswordField
from wtforms.validators import EqualTo, Length

from zopsedu.lib.form.fields import Select2Field


class GenelForm(FlaskForm):
    """Site ayarlari icindeki genel alani formu"""
    site_adi = StringField(_("Site Adı"))
    logo = FileField(label=_('Logo'))
    universite_id = Select2Field(_("Üniversite Adı"), url="/select/universite")
    bap_kisa_adi = StringField(_("BAP Kısa Adı"))
    sehir = StringField(_("Şehir"))
    adres = TextAreaField(_("Adres"))
    telefon = StringField(_("Telefon"))
    faks = StringField(_("Faks"))


class SozlesmeYetkilisiForm(FlaskForm):
    """Site ayarlari icindeki sozlesme yetkilisi alani formu"""
    gorevi = StringField(_("Görevi"))
    adi_soyadi = StringField(_("Adı - Soyadı"))


class DigerForm(FlaskForm):
    """Site ayarlari icindeki diger alani formu"""
    arastirmaci_unvanlari = FieldList(StringField(_("Araştırmacı Unvanları")))
    bilim_dallari = FieldList(StringField(_("Bilim Dalları")))
    proje_ilgili_alanlar = FieldList(StringField(_("Proje İlgili Alanlar")))


class YoksisKullaniciBilgileri(FlaskForm):
    """
    Yoksis kullanici bilgileri formu
    """
    yoksis_kullanici_adi = StringField(_("Yöksis Kullanıcı No"), validators=[Length(max=30)])
    yoksis_password = PasswordField(_("Yöksis Kullanıcı Parolası"), validators=[
        EqualTo('yoksis_password_repeat', message=_('Girdiğiniz parolalar eşleşmelidir.'))
    ])
    yoksis_password_repeat = PasswordField(_("Yöksis Kullanıcı Parolası Tekrar"))


class SiteAyarlariForm(FlaskForm):
    """Site Ayarlari Formu"""
    genel = FormField(GenelForm)
    sozlesme_yetkilisi = FormField(SozlesmeYetkilisiForm)
    yoksis_kullanici_bilgisi = FormField(YoksisKullaniciBilgileri)
    diger = FormField(DigerForm)
