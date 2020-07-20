"""Ogrenci Basvuru Form"""
from flask_babel import lazy_gettext as _
from wtforms import Form, SubmitField, StringField, validators, SelectField, IntegerField, \
    FloatField
from zopsedu.lib.form import fields


class StudentInformationForm(Form):
    """Example ogrenci formu"""
    name = StringField(
        label=_("Name"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Name"}
    )
    surname = StringField(
        label=_("Surname"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Surname"}
    )
    identification_no = IntegerField(
        label=_("Identification Number"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Identification Number"}
    )

    registration_no = IntegerField(
        label=_("Registration Number"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Registration Number"}
    )

    date_of_birth = fields.DatePickerField(
        label=_("Student Birth Day"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Student Birth Day"}
    )

    gender = SelectField(label=_("Gender"), choices=[(0, _("Male")), (1, _("Female"))], default=1)

    nationality = StringField(
        label=_("Student Nationality"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Student Nationality"}
    )

    home_institution = StringField(
        label=_("Student Institution"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Student Institution"}
    )

    field_code = IntegerField(
        label=_("Field Code"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Field Code"}
    )

    preceding_education = IntegerField(
        label=_("Period of Preceding Education (years)"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Period of Preceding Education (years)"}
    )
    total_national_credits = IntegerField(
        label=_("Total National Credits"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Total National Credits"}
    )
    total_ects = IntegerField(
        label=_("Total ECTS Credits (if applied)"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Total ECTS Credits"}
    )
    instruction_language = StringField(
        label=_("Instruction Language of Host Institution"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Instruction Language of Host Institution"}
    )
    gpa = FloatField(
        label=_("GPA"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Student Grade Point Average (GPA)"}
    )
    language_level = SelectField(
        label=_("Language Level"),
        choices=[
            ('elementary', 'Elementary'), ('pre-intermediate', 'Pre-Intermediate'),
            ('intermediate', 'Intermediate'), ('upper-intermediate', 'Upper-Intermediate')
        ],
        render_kw={"placeholder": "Language Level"}
    )
    host_institution = StringField(
        label=_("Host Institution"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Host Institution"}
    )

    contact = StringField(
        label=_("Student Contact Information"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Contact"}
    )
    contact_host_institution = IntegerField(
        label=_("Contact Information of Host Institution"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Contact Information of Host Institution"}
    )
    scholarship_sum = IntegerField(
        label=_("Total Amount of Scholarship"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Total Amount of Scholarship"}
    )
    advance_payment = IntegerField(
        label=_("Payment in Advance"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Payment in Advance"}
    )
    final_payment = IntegerField(
        label=_("Final Payment"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Final Payment"}
    )
    start_date_of_study = fields.DatePickerField(
        label=_("Start Date of Study"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))],
        render_kw={"placeholder": "Start Date of Study"}
    )

    finish_date_of_study = fields.DatePickerField(
        label=_("Final Date of Study"),
        validators=[validators.DataRequired(message=_("This field can not be left blank."))])

    level_of_degree = SelectField(
        label=_("Level of Degree (Associate Degree, Bachelor Degree, MA, PhD)"),
        choices=[
            ('associate', 'Associate Degree'), ('bachelor', 'Bachelor Degree'), ('ma', 'MA'),
            ('phd', 'PhD')
        ],
        render_kw={"placeholder": "Final Date of Study"}
    )
    has_the_student_ever_attended_mep = fields.RadioButtonField(
        _('Has the Student Ever Attended Mevlana Exchange Programme?'),
        choices=[(1, _('Evet')), (2, _('Hayır'))],
        render_kw={"placeholder": "Has the Student Ever Attended Mevlana Exchange Programme?"}
    )
    has_the_student_ever_attended_eep = fields.RadioButtonField(
        _('Has the Student Ever Attended Erasmus Exchange Programme?'),
        choices=[(1, _('Evet')), (2, _('Hayır'))],
        render_kw={"placeholder": "Has the Student Ever Attended Erasmus Exchange Programme?"}
    )
    notes = StringField(
        label=_("Notes"),
        validators=[validators.DataRequired(message=("This field can not be left blank."))],
        render_kw={"placeholder": "Notes"}
    )

    submit = SubmitField(label=_('Save'))
