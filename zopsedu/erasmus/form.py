"""Erasmus form"""
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SelectField, IntegerField, BooleanField

from zopsedu.lib.form.fields import DatePickerField


class ErasmusForm(FlaskForm):
    """ Erasmus form fields """
    ad = StringField(label=_("First Name"),
                     validators=[validators.DataRequired(message=_("First Name cannot be empty."))])
    name_only = StringField(label=_("Name"),
                            validators=[
                                validators.DataRequired(message=_("Name cannot be empty."))])
    soyad = StringField(label=_("Last Name"),
                        validators=[
                            validators.DataRequired(message=_("Last Name cannot be empty."))])
    ogrenci_dogum_tarihi = DatePickerField(label=_("Date of Birth"),
                                           validators=[validators.DataRequired(
                                               message=_("Date of birth cannot be empty."))])
    ogrenci_uyruk = StringField(label=_("Nationality"),
                                validators=[validators.DataRequired(
                                    message=_("Nationality cannot be empty."))])
    ogrenci_cinsiyet = SelectField(label=_("Sex"),
                                   choices=[(0, _("Male")), (1, _("Female")), (2, _("Other"))],
                                   default=2)
    akademik_yil = IntegerField(_("Academic Year"), default=2018)
    ogrenim_durumu = SelectField(label=_("Study Cycle"),
                                 choices=[(1, _("Bachelor or equivalent")),
                                          (2, _("Master or equivalent")),
                                          (3, _("Doctoral level"))],
                                 default=1)
    calisma_alani_kodu = StringField(label=_("Subject Area, Code"),
                                     validators=[validators.DataRequired(
                                         message=_("Subject Area, Code cannot be empty."))])
    fakulte = StringField(label=_("Faculty"),
                          validators=[
                              validators.DataRequired(message=_("Faculty cannot be empty."))])
    erasmus_kodu = StringField(label=_("Erasmus Code  (if applicable)"))
    bolum = StringField(label=_("Department"),
                        validators=[
                            validators.DataRequired(message=_("Department cannot be empty."))])
    adres = StringField(label=_("Address"),
                        validators=[validators.DataRequired(message=_("Address cannot be empty."))])

    ulke = StringField(label=_("Country, Country code"), validators=[
        validators.DataRequired(message=_("Country, Country code cannot be emoty."))
    ])

    contact_person_ad = StringField(label=_("Contact person name"),
                                    validators=[validators.DataRequired(
                                        message=_("Contact person name cannot be empty."))])

    constact_person_email_or_phone = StringField(
        label=_("Contact person e-posta/telefon"),
        validators=[
            validators.DataRequired(message=_("Contact person e-posta/telefon cannot be empty."))
        ])
    planed_period_of_the_mobility_from = StringField(
        label=_("Planned period of the mobility: from [month/year]"),
        validators=[
            validators.DataRequired(message=_("month/year cannot be empty."))
        ])
    planed_period_of_the_mobility_to = StringField(
        label=_("to [month/year]"),
        validators=[
            validators.DataRequired(message=_("month/year cannot be empty."))
        ])
    bos_input = StringField(render_kw={"class": "form-control"})
    empty_number_input = IntegerField(render_kw={"class": "form-control", "type": "number"})
    a1 = BooleanField(label=_("A1"), default=False)
    a2 = BooleanField(label=_("A2"), default=False)
    b1 = BooleanField(label=_("B1"), default=False)
    b2 = BooleanField(label=_("B2"), default=False)
    c1 = BooleanField(label=_("C1"), default=False)
    c2 = BooleanField(label=_("C2"), default=False)
    native = BooleanField(label=_("Native speaker"), default=False)
    function = StringField(label=_("Function"),
                           validators=[
                               validators.DataRequired(message=_("Function cannot be empty."))])
    phone_number = StringField(label=_("Phone Number"), default=5300000000,
                               validators=[validators.DataRequired(
                                   message=_("Phone number cannot be empty."))])
    email = StringField(label=_("Email"),
                        validators=[validators.DataRequired(message=_("Email cannot be empty."))])
    date = DatePickerField(label=_("Date"),
                           validators=[validators.DataRequired(message=_("Date cannot be empty."))])
