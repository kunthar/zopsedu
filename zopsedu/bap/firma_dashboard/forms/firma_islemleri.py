"""Bap firma formlari"""

from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField, FileField, FormField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_babel import gettext as _

from zopsedu.lib.form.fields import DatePickerField, Select2Field
from zopsedu.lib.form.validators import CustomFileFieldRequired, FileExtensionRestriction


class UserBilgileri(Form):
    yetkili_kullanici_adi = StringField(_("Bap Kullanıcı Adı"),
                                        validators=[
                                            DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=80)])
    yetkili_email = StringField(_("Yetkili E-posta"),
                                validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")),
                                            Email(message=_('Geçersiz e-posta.')), Length(max=255)])
    password = StringField(_("Parola"),
                           validators=[
                               DataRequired(message=_('Bu alan boş bırakılamaz.')),
                               Length(3, 16, message=_(
                                   'Parola en az 3, en fazla 16 karakterden oluşmalı.')),
                               EqualTo('re_password',
                                       message=_('Girdiğiniz parolalar eşleşmelidir.'))
                           ],
                           )
    re_password = StringField(_("Parola Tekrar"),
                              validators=[
                                  DataRequired(message=_('Bu alan boş bırakılamaz.')),
                                  Length(3, 16, message=_(
                                      'Parola en az 3, en fazla 16 karakterden oluşmalı.')),
                                  EqualTo('password',
                                          message=_('Girdiğiniz parolalar eşleşmelidir.'))
                              ],
                              )


class FirmaKayitFormu(FlaskForm):
    """Firma Kayit Formu"""
    bilgi_notu = _("""Lütfen kayıt işlemi için firma ve yetkili bilgilerinizi doğru girdiğinizden emin olunuz. 
                    Değerlendirme sonucunda firmanızın onay alması halinde, giriş yapmanız için 
                    kullanıcı oluşturulacaktır. 
                    Yetkili bilgileri kısmı, firmanızda yetkili olan kişi şeklinde doldurulmadır.""")

    firma_faaliyet_belgesi_id = FileField(_("Firma Faaliyet Belgesi"), validators=[
        CustomFileFieldRequired(error_message=_("Firma faaliyet belgesi yüklemek zorundasınız")),
        FileExtensionRestriction(
            error_message=_(
                "Lütfen uzantısı geçerli bir dosya yükleyiniz."))])
    adres = StringField(_("Firma Adresi"),
                        validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=500)])

    adi = StringField(_("Firma Adı"), validators=[Length(max=500)])
    telefon = StringField(_("Firma Telefon"),
                          validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=25)])
    email = StringField(_("Firma E-posta"),
                        validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=80),
                                    Email(message=_('Geçersiz e-posta.'))])

    vergi_kimlik_numarasi = StringField(_("Vergi Kimlik Numarası"),
                                        validators=[
                                            DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=20)])

    faaliyet_belgesi_verilis_tarihi = DatePickerField(_("Faaliyet Belgesi Veriliş Tarihi"),
                                                      validators=[DataRequired(
                                                          message=_("Bu Alan Boş Bırakılamaz"))],
                                                      disable_older_dates=False)
    yetkili_adi = StringField(_("Yetkili Adı"),
                              validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=50)])
    yetkili_soyadi = StringField(_("Yetkili Soyadı"),
                                 validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=50)])
    vergi_dairesi_id = Select2Field(_('Vergi Dairesi'),
                                    url="/select/vergi-dairesi",
                                    placeholder=_("Vergi Dairesi Adı"))

    iban = StringField(_("IBAN No"),
                       validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=30)])
    banka_sube_adi = StringField(_("Banka/Şube Adı"),
                                 validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=255)])

    yetkili_user_bilgileri = FormField(UserBilgileri)
