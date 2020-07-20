"""Bap anasayfa formlari"""

from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_babel import gettext as _

from zopsedu.lib.form.fields import DatePickerField


class FirmaKayitFormu(FlaskForm):
    """Firma Kayit Formu"""
    bilgi_notu = _("""Lütfen kayıt işlemi için firma ve yetkili bilgilerinizi doğru girdiğinizden emin olunuz. 
                    Değerlendirme sonucunda firmanızın onay alması halinde, giriş yapmanız için 
                    kullanıcı oluşturulacaktır. 
                    Yetkili bilgileri kısmı, firmanızda yetkili olan kişi şeklinde doldurulmadır.""")

    firma_faaliyet_belgesi_id = FileField(_("Firma Faaliyet Belgesi"))
    adres = StringField(_("Firma Adresi"),
                        validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=500)])

    adi = StringField(_("Firma Adı"), validators=[Length(max=500)])
    telefon = StringField(_("Firma Telefon"),
                          validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=25)])
    email = StringField(_("Firma E-posta"),
                        validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=80),
                                    Email(message=_('Geçersiz e-posta.'))])

    vergi_kimlik_numarasi = StringField(_("Vergi Kimlik Numarası"),
                                        validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=20)])

    faaliyet_belgesi_verilis_tarihi = DatePickerField(_("Faaliyet Belgesi Veriliş Tarihi"),
                                                      validators=[DataRequired(
                                                          message=_("Bu Alan Boş Bırakılamaz"))],
                                                      disable_older_dates=False)
    yetkili_adi = StringField(_("Yetkili Adı"),
                              validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=50)])
    yetkili_soyadi = StringField(_("Yetkili Soyadı"),
                                 validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=50)])
    yetkili_kullanici_adi = StringField(_("Yetkili Kullanıcı Adı"),
                                        validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz"))])
    yetkili_email = StringField(_("Yetkili E-posta"),
                                validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz")), Length(max=25),
                                            Email(message=_('Geçersiz e-posta.'))])
