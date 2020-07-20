"""Ornek ve Genel Amacli Formlar Modulu"""
from uuid import uuid4

from flask_babel import lazy_gettext as _
from wtforms import Form, SubmitField, StringField, validators, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField
from wtforms.meta import DefaultMeta
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from zopsedu.lib.form import fields
from zopsedu.lib.form.fields import MultiFileField, SummerNoteField, Select2Field

# pylint: disable=invalid-name
il_ilce_mah = [
    {
        "id": "a",
        "text": "Ankara",
        "sub": [
            {
                "id": "x",
                "text": "Sincan",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "y",
                "text": "Bahçelievler",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "z",
                "text": "Dikmen",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
        ]
    },
    {
        "id": "b",
        "text": "Balıkesir",
        "sub": [
            {
                "id": "x",
                "text": "Bandırma",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "y",
                "text": "Erdemit",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "z",
                "text": "Ayvalık",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
        ]
    },
    {
        "id": "d",
        "text": "Denizli",
        "sub": [
            {
                "id": "x",
                "text": "Acıpayam",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "y",
                "text": "Baklan",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "z",
                "text": "Çal",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
        ]
    },
    {
        "id": "k",
        "text": "Konya",
        "sub": [
            {
                "id": "x",
                "text": "Karatay",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "y",
                "text": "Cihanbeyli",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "z",
                "text": "Merum",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
        ]
    },
    {
        "id": "B",
        "text": "Bursa",
        "sub": [
            {
                "id": "x",
                "text": "Osmangazi",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "y",
                "text": "Gemlik",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "z",
                "text": "İnegöl",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
        ]
    },
    {
        "id": "i",
        "text": "İzmir",
        "sub": [
            {
                "id": "x",
                "text": "Alsancak",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "y",
                "text": "Urla",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
            {
                "id": "z",
                "text": "Çeşme",
                "sub": [
                    {
                        "id": "e",
                        "text": "orta"
                    },
                    {
                        "id": "f",
                        "text": "alt"
                    },
                    {
                        "id": "g",
                        "text": "üst"
                    },
                ]
            },
        ]
    },
]


# pylint: enable=invalid-name


class DatePickerForm(FlaskForm):
    """Example form for Date Picker"""
    start = fields.DatePickerField(_('Başlangıç günü'))
    finish = fields.DatePickerField(_('Bitiş günü'))
    submit = SubmitField(label=_('Gönder'))


class BagimliBirimSecimi(FlaskForm):
    """
    3 adimlik birbirine bağımlı birim seçimi formu.
    Ornek formdur. FormField olarak olusturdugunuz forma eklenip kullanilamaz.
    Proje Basvuru formunun genel_bilgiler bölümünde FakulteForm'u icerisinde kullanilmistir.Oradan
    yararlanilabilir
    """

    select_node_one = Select2Field(_('Fakülte'),
                                   url="/select/birim",
                                   validators=[
                                       DataRequired(message=_("Fakülte Alanı Boş Bırakılamaz"))
                                   ],
                                   placeholder=_("Fakülte"),
                                   node_name="first_node_name")
    select_node_two = Select2Field(_('Bölüm'), url="/select/birim",
                                   validators=[DataRequired(message=_("Bu Alan Boş Bırakılamaz"))],
                                   placeholder=_("Bölüm"),
                                   dependent="first_node_name",
                                   node_name="second_node_name")
    select_node_three = Select2Field(_('Ana Bilim Dali'),
                                     url="/select/birim",
                                     validators=[
                                         DataRequired(
                                             message=_("Bu Alan Boş Bırakılamaz"))
                                     ],
                                     placeholder=_("Ana Bilim Dali"),
                                     dependent="second_node_name")


class GenderAndALanguageForm(BagimliBirimSecimi):
    """Example form for Checkbox, RadioButton and TextField with validation"""

    class Meta(DefaultMeta):
        """Ekstra form meta"""
        form_name = "zopsedu_gender_and_language_form"
        form_type = "generic"
        will_explored = False
        will_listed = False

    gender = fields.MultiCheckboxField(_('Cinsiyet'),
                                       choices=[(1, _('Erkek')), (2, _('Kadın'))])
    language = fields.RadioButtonField(_('Dil'), choices=[(1, _('İngilizce')),
                                                          (2, _('Türkçe'))])
    required_field = StringField(_('Gerekli alan'), [
        validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))])
    submit = SubmitField(label=_('Gönder'))
    # Birden fazla MultiFileField veya Select2Field varsa
    file = MultiFileField()
    file2 = MultiFileField(ids=uuid4().hex)
    # url = '/form_samples/select-random'
    d2 = fields.Select2Field(url='/form_samples/select-random')
    d22 = fields.Select2Field(url='/form_samples/select-random', dependent='d2')
    d222 = fields.Select2Field(url='/form_samples/select-random', dependent='d22')
    s2 = fields.Select2Field(choices=il_ilce_mah)
    s22 = fields.Select2Field(dependent='s2', choices=il_ilce_mah)
    s222 = fields.Select2Field(dependent='s22', choices=il_ilce_mah)
    birim = fields.Select2Field(url='/select/birim')
    hakem = fields.Select2Field(url='/select/hakem')
    personel = fields.Select2Field(url='/select/personel')


class ExampleFormToIndexAndImportDynamically(DatePickerForm):
    """Example form to test migrate_forms command"""

    class Meta(DefaultMeta):
        """Example Form Meta"""
        form_name = "zopsedu_example_form"
        form_type = "generic"
        form_module = "general"
        will_explored = True
        will_listed = True


class SubmitForm(Form):
    """Submit Form"""
    submit = SubmitField(label=_('Save'))


class LoginForm(Form):
    """Example login form for EmailInput, PasswordInput and Checkbox with validation"""
    email = EmailField(
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Email(message=_('Geçersiz e-posta.'))
        ],
        render_kw={"placeholder": _("E-posta")}
    )
    password = PasswordField(
        validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            validators.Length(3, 16, message=_('Parola en az 3, en fazla 16 karakterden oluşmalı.'))
        ],
        render_kw={"placeholder": _("Parola")}
    )
    submit = SubmitField(label=_('Giriş Yap'))
    submit2 = SubmitField(label=_('Kayıt Ol'))


class SelectBoxForm(Form):
    """Example selectbox form"""

    locations = SelectField(u'Selections', choices=[
        ('a', 'Ankara'), ('b', 'Balıkesir'), ('d', 'Denizli'), ('k', 'Kapadokya'),
        ('k', 'Konya'), ('B', 'Bursa'), ('i', 'Izmir')
    ])


class SummerNoteForm(Form):
    """Example wysiwyg form"""

    note = SummerNoteField(u'Write Something')
    save = SubmitField(label=_('Kaydet'))
