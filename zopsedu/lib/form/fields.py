"""Ozel widgetlara sahip form fieldlari"""
from uuid import uuid4
from decimal import Decimal

from flask_babel import gettext as _

from wtforms import DateField, SelectField, widgets, IntegerField, Field, StringField, BooleanField, \
    DateTimeField, SelectMultipleField, DecimalField
from zopsedu.lib.form.widgets import DatePickerWidget, FileUploadWidget, Select2Widget, \
    SummerNoteWidget, FileInputWidget, SelectWithSelectedDisabledLabel, DateTimePickerWidget


class DatePickerField(DateField):
    """Date picker field"""
    widget = DatePickerWidget()

    def __init__(self,
                 label='',
                 validators=None,
                 disable_older_dates=True,
                 disable_further_dates=False,
                 format='%d.%m.%Y',  # pylint: disable=redefined-builtin
                 **kwargs):
        super(DatePickerField, self).__init__(label, validators, format=format, **kwargs)

        self.disable_older_dates = disable_older_dates
        self.disable_further_dates = disable_further_dates
        self.format = format


class TimePickerField(DateField):
    """Date picker field"""
    widget = DatePickerWidget()

    def __init__(self,
                 label='',
                 validators=None,
                 format='%H:%M',  # pylint: disable=redefined-builtin
                 **kwargs):
        super(TimePickerField, self).__init__(label, validators, format=format, **kwargs)
        self.format = format


class DateTimePickerField(DateTimeField):
    """Date picker field"""
    widget = DateTimePickerWidget()

    def __init__(self,
                 label='',
                 validators=None,
                 format='%d.%m.%Y %H:%M',  # pylint: disable=redefined-builtin
                 **kwargs):
        super(DateTimePickerField, self).__init__(label, validators, format=format, **kwargs)


class RadioButtonField(SelectField):
    """Radio button field"""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()


class MultiCheckboxField(SelectMultipleField):
    """Multi Checkbox field"""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiFileField(IntegerField):
    """Multiple file upload field"""
    widget = FileUploadWidget()

    def __init__(self,
                 label='',
                 validators=None,
                 button_name=_('Dosya Yükle'),
                 colmd=3,
                 file_size=5,
                 file_types=None,
                 max_number_of_files=1,
                 ids=uuid4().hex,
                 **kwargs):  # pylint: disable=too-many-arguments
        super(MultiFileField, self).__init__(label, validators, **kwargs)
        if not file_types:
            file_types = ['jpg', 'jpeg', 'png', 'odt', 'doc', 'pdf']
        self.button_name = button_name
        self.colmd = colmd
        self.file_size = file_size
        self.file_types = file_types
        self.max_number_of_files = max_number_of_files
        self.id = ids


class HiddenIntegerField(IntegerField):
    """Hidden integer field"""
    widget = widgets.HiddenInput()


class HiddenStringField(StringField):
    """Hidden String field"""
    widget = widgets.HiddenInput()


class HiddenBooleanField(BooleanField):
    """Hidden Boolean field"""
    widget = widgets.HiddenInput()


class CustomFileField(Field):
    """Custom File field"""
    widget = FileInputWidget()

    def __init__(self,
                 label='',
                 validators=None,
                 **kwargs):
        super(CustomFileField, self).__init__(label, validators, **kwargs)


class Select2Field(Field):
    """Custom select2 field"""
    widget = Select2Widget()

    def __init__(self,
                 label='',
                 validators=None,
                 url=None,
                 placeholder=_('Ara'),
                 min_input_len=3,
                 multiple=False,
                 dependent=None,
                 choices=None,
                 node_name=None,
                 disabled=False,
                 kurum_ici=True,
                 birim_tipi=None,
                 **kwargs):  # pylint: disable=too-many-arguments
        super(Select2Field, self).__init__(label, validators, **kwargs)

        self.url = url
        self.placeholder = placeholder
        self.min_input_len = min_input_len
        self.multiple = multiple
        self.dependent = dependent
        self.choices = choices
        self.node_name = node_name
        self.disabled = disabled
        self.kurum_ici = kurum_ici
        self.birim_tipi = birim_tipi


class SummerNoteField(Field):
    """Custom select2 field"""
    widget = SummerNoteWidget()

    def __init__(self, label='', validators=None, placeholder=_('Mesaj Ekleyiniz'), **kwargs):
        super(SummerNoteField, self).__init__(label, validators, **kwargs)

        self.placeholder = placeholder


class SelectWithDisableField(SelectField):
    """Select field with disable option"""
    widget = SelectWithSelectedDisabledLabel()


class ZopseduDecimalField(DecimalField):
    def __init__(self,
                 label=None,
                 default=Decimal("0.00"),
                 use_locale=True,
                 number_format="0.00",
                 render_kw={"class": "form-control money"},
                 **kwargs):
        super(DecimalField, self).__init__(label,
                                           use_locale=use_locale,
                                           number_format=number_format,
                                           render_kw=render_kw,
                                           default=default,
                                           **kwargs)
