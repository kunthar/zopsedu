"""Farabi Form"""
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SelectField, IntegerField, BooleanField

from zopsedu.lib.form.fields import DatePickerField, MultiFileField


class FarabiForm(FlaskForm):
    """ Erasmus form fields """
    ad = StringField(label=_("Ad"),
                     validators=[validators.DataRequired(message=_("Ad boş bırakılamaz."))])
    soyad = StringField(label=_("Soyad"),
                        validators=[validators.DataRequired(message=_("Soyad boş bırakılamaz."))])
    tc = IntegerField(label=_("T.C. Kimlik No"),
                      validators=[
                          validators.DataRequired(message=_("T.C. Kimlik No boş bırakılamaz."))])
    bolum = StringField(label=_("Bölümü"),
                        validators=[validators.DataRequired(message=_("Bölüm boş bırakılamaz."))])
    ogrenci_no = IntegerField(label=_("Öğrenci No"),
                              validators=[validators.DataRequired(
                                  message=_("Öğrenci No boş bırakılamaz."))])
    adres = StringField(label=_("Address"),
                        validators=[validators.DataRequired(message=_("Adres boş bırakılamaz."))])
    photo = MultiFileField(file_types=['jpg', 'jpeg', 'png'], button_name=_('Fotoğraf Yükle'),
                           colmd=4)
    kurum_kordinatoru = StringField(label=_("Kurum Koordinatörü"),
                                    validators=[
                                        validators.DataRequired(
                                            message=_("Kurum Koordinatörü boş bırakılamaz."))])
    phone_number = StringField(label=_("Telefon No"), default=0,
                               validators=[validators.DataRequired(
                                   message=_("Telefon No boş bırakılamaz."))])
    faks = StringField(label=_("Faks"), default=0,
                       validators=[validators.DataRequired(message=_("Faks boş bırakılamaz."))])
    email = StringField(label=_("E-Posta"),
                        validators=[validators.DataRequired(message=_("E-Posta boş bırakılamaz."))])
    bolum_kordinatoru = StringField(label=_("Bölüm Koordinatörü"),
                                    validators=[
                                        validators.DataRequired(
                                            message=_("Bölüm Koordinatörü boş bırakılamaz."))])
    ogrenci_dogum_tarihi = DatePickerField(label=_("Doğum Tarihi"),
                                           validators=[validators.DataRequired(
                                               message=_("Doğum Tarihi boş bırakılamaz."))])
    ogrenci_uyruk = StringField(label=_("Uyruk"),
                                validators=[
                                    validators.DataRequired(message=_("Uyruk boş bırakılamaz."))])
    ogrenci_cinsiyet = SelectField(label=_("Cinsiyet"),
                                   choices=[(0, _("Erkek")), (1, _("Kadın")), (2, _("Diğer"))],
                                   default=2)
    ogrenim_durumu = StringField(label=_("Devam Edilen Diploma Derecesi"),
                                 validators=[validators.DataRequired(
                                     message=_("Devam Edilen Diploma Derecesi boş bırakılamaz."))])
    sinifi = IntegerField(label=_("Sınıfı"),
                          validators=[validators.DataRequired(message=_("Sınıf boş bırakılamaz."))])
    dogum_yeri = StringField(label=_("Doğum Yeri"),
                             validators=[
                                 validators.DataRequired(message=_("Doğum yeri boş bırakılamaz."))])
    bos_input = StringField(render_kw={"class": "form-control"})
    zayif = BooleanField(label=_("Zayıf"), default=False)
    orta = BooleanField(label=_("Orta"), default=False)
    iyi = BooleanField(label=_("İyi"), default=False)
    mukemmel = BooleanField(label=_("Mükemmel"), default=False)
