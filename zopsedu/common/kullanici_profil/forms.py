"""Kullanici Profil"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, FileField, PasswordField, validators, StringField, \
    TextAreaField, \
    IntegerField
from flask_babel import gettext as _
from wtforms.validators import DataRequired, Email, Length

from zopsedu.auth.models.auth import RolTipleri

from zopsedu.lib.form.fields import SummerNoteField, Select2Field, HiddenIntegerField
from zopsedu.lib.form.validators import FileExtensionRestriction
from zopsedu.models.helpers import BirimTipiEnum

ROLLER = [(r.name, r.value) for r in RolTipleri]


class AvatarGuncelleForm(FlaskForm):
    """Kullanici Avatar Guncelleme Formu"""

    avatar = FileField(label=_('Avatar'))
    guncelle = SubmitField(label=_('Güncelle'))


class RolForm(FlaskForm):
    """Rol Degistirme Formu"""

    roles = SelectField(label='Rol', render_kw={'class': 'form-control'}, coerce=int)
    degistir = SubmitField(label=_('Rolü Değiştir'))


class PasswordChangeForm(FlaskForm):
    """Login Form"""

    old_password = PasswordField(
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Length(3, 16, message=_('Parola en az 3, en fazla 16 karakterden oluşmalı.'))
        ],
        render_kw={"placeholder": _("Eski Parola")})
    new_password = PasswordField(
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Length(3, 16,
                              message=_('Parola en az 3, en fazla 16 karakterden oluşmalı.')),
            validators.EqualTo('re_password', message=_('Girdiğiniz parolalar eşleşmelidir.'))
        ],
        render_kw={"placeholder": _("Yeni Parola")})
    re_password = PasswordField(
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Length(3, 16,
                              message=_('Parola en az 3, en fazla 16 karakterden oluşmalı.')),
            validators.EqualTo('new_password', message=_('Girdiğiniz parolalar eşleşmelidir.'))
        ],
        render_kw={"placeholder": _("Yeni Parola Onayla")})

    confirm = PasswordField('Repeat Password')
    degistir = SubmitField(label=_('Değiştir'))


class HariciOgretimElemaniFormu(FlaskForm):
    tckn = IntegerField(label=_("TC Kimlik No : "),
                        validators=[validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))])
    unvan = StringField(label=_("Unvan : "), validators=[Length(max=50)])
    ad = StringField(label=_("Ad : "),
                     validators=[validators.DataRequired(message=_('Bu alan boş bırakılamaz.')), Length(max=50)])
    soyad = StringField(label=_("Soyad : "),
                        validators=[validators.DataRequired(message=_('Bu alan boş bırakılamaz.')), Length(max=50)])
    birincil_eposta = StringField(label=_("Eposta : "),
                                  validators=[validators.DataRequired(
                                      message=_('Bu alan boş bırakılamaz.')), Length(max=50),
                                              Email(message='Bir email adresi girmelisiniz')])

    ikincil_eposta = StringField(label=_("İkinci Eposta : "),
                                 validators=[
                                     validators.DataRequired(message=_('Bu alan boş bırakılamaz.')), Length(max=50),
                                     Email(message='Bir email adresi girmelisiniz')])
    ev_tel_no = IntegerField(label=_("Ev Telefonu : "))
    cep_tel = IntegerField(label=_("Cep Tel. : "))
    adres = TextAreaField(label=_("Adres :"))
    adres2 = TextAreaField(label=_("Adres2 :"))
    akademik_yayinlari = TextAreaField(label=_('Akademik Yayınları :'))
    banka_adi = StringField(label=_('Banka Adı : '), validators=[Length(max=100)])
    sube_adi = StringField(label=_('Şube Adı : '), validators=[Length(max=100)] )
    sube_kod = IntegerField(label=_('Şube Kodu : '))
    hesap_no = IntegerField(label=_('Hesap No : '))
    iban_no = StringField(label=_('Iban No : '), validators=[Length(max=100)])
    submit = SubmitField(label=_('Kaydet'))

    universite = Select2Field(_('Üniversite Seç'),
                              url="/select/birim",
                              validators=[
                                  DataRequired(message=_("Üniversite alanı boş bırakılamaz"))
                              ],
                              placeholder=_("Üniversite"),
                              node_name="fakulte_parent",
                              birim_tipi=BirimTipiEnum.universite.value,
                              kurum_ici=True)

    fakulte = Select2Field(_('Fakülte Seç'), url="/select/birim",
                           validators=[DataRequired(message=_("Bölüm alanı boş bırakılamaz"))],
                           placeholder=_("Fakülte"),
                           dependent="fakulte_parent",
                           node_name="bolum_parent",
                           birim_tipi=BirimTipiEnum.fakulte.value,
                           kurum_ici=True)

    bolum = Select2Field(_('Bölüm Seç'),
                         url="/select/birim",
                         validators=[
                             DataRequired(
                                 message=_("Bölüm alanı boş bırakılamaz"))
                         ],
                         placeholder=_("Bölüm"),
                         dependent="bolum_parent",
                         birim_tipi=BirimTipiEnum.bolum.value,
                         kurum_ici=True)

    unvan = Select2Field(label=_('Ünvan'),
                         validators=[
                             DataRequired(
                                 message=_("Ünvan boş bırakılamaz"))
                         ],
                         url='/select/hitap_unvan')


class OzgecmisKayitFormu(FlaskForm):
    """Ozgecmis kayit Formu
       Kullanici dosya ile ozgecmis yukler,
         aksi takdirde gerekli alanlari doldurur.
    """
    ad = StringField(label=_("Ad: "), validators=[Length(max=50)])
    soyad = StringField(label=_("Soyad: "), validators=[Length(max=50)])
    dogum_tarihi = StringField(label=_("Doğum Tarihi: "))
    tecrube = SummerNoteField(label=_("Tecrübe: "))
    ozgecmis_dosya = FileField(
        label=_("Dosya seçerseniz varolan özgeçmiş dosyanız güncellenecektir!"),
        validators=[FileExtensionRestriction(error_message=_("Lütfen uzantısı geçerli bir dosya yükleyiniz."))])
    ozgecmis_dosya_id = HiddenIntegerField(_("Dosya"))
    kaydet = SubmitField(label=_("Kaydet"))
