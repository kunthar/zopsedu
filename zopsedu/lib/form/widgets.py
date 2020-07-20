"""Formlar icin ozel widgetlar modulu"""
import datetime

from flask import render_template_string
from flask_babel import format_date, format_datetime
from flask_babel import gettext as _
from wtforms.widgets import HTMLString, html_params, Select


class DatePickerWidget(object):
    """
    Date Time picker
    """
    data_template = """
        {% from 'macros/datepicker.html' import datepicker %}
        {{ datepicker(field=field, disable_older_dates=disable_older_dates,disable_further_dates=disable_further_dates) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('name', field.name)
        kwargs.setdefault('disable_older_dates', field.disable_older_dates)
        kwargs.setdefault('disable_further_dates', field.disable_further_dates)

        if not field.data:
            field.data = ""
        else:
            if isinstance(field.data, str):
                date_obj = datetime.datetime.strptime(field.data, '%Y-%m-%d').date()
                field.data = format_date(date_obj, format="short")
            elif isinstance(field.data, datetime.date):
                field.data = format_date(field.data, format="short")
        return HTMLString(
            render_template_string(self.data_template, field=field, **kwargs)
        )

class TimePickerWidget(object):
    """
    Time picker
    """
    data_template = """
        {% from 'macros/timepicker.html' import timepicker %}
        {{ datepicker(field=field) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('name', field.name)

        if not field.data:
            field.data = ""
        else:
            if isinstance(field.data, str):
                date_obj = datetime.datetime.strptime(field.data, '%H:%M')
                field.data = format_date(date_obj, format="short")
            elif isinstance(field.data, datetime.date):
                field.data = format_date(field.data, format="short")
        return HTMLString(
            render_template_string(self.data_template, field=field, **kwargs)
        )



class DateTimePickerWidget(object):
    """
    Date Time picker
    """
    data_template = """
        {% from 'macros/datetimepicker.html' import datetimepicker %}
        {{ datetimepicker(field=field) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('name', field.name)

        if not field.data:
            field.data = ""
        else:
            #todo: String gelmesi durumunda bunu datetime objesine çevirilmesi eklenecek
            if isinstance(field.data, str):
                date_obj = datetime.datetime.strptime(field.data, '%Y-%m-%d %H:%M')
                field.data = format_datetime(date_obj, format="short")
        return HTMLString(
            render_template_string(self.data_template, field=field, **kwargs)
        )




class FileUploadWidget(object):
    """
    File Upload Widget
    """
    data_template = """
        {% from 'macros/file_upload.html' import modal_file_upload %}
        {{ modal_file_upload(field, button_name, colmd, file_size, file_types, maxNumberOfFiles, id) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('button_name', field.button_name)
        kwargs.setdefault('colmd', field.colmd)
        kwargs.setdefault('file_size', field.file_size)
        kwargs.setdefault('file_types', field.file_types)
        kwargs.setdefault('maxNumberOfFiles', field.max_number_of_files)
        kwargs.setdefault('id', field.id)

        return HTMLString(
            render_template_string(self.data_template, field=field, **kwargs)
        )


class Select2Widget(object):
    """
    Select2 Widget
    """
    data_template = """
        {% from "macros/select2.html" import select2 with context %}
        {{ select2(field=field, url=url, placeholder=placeholder, 
        min_input_len=min_input_len, multiple=multiple, dependent=dependent, choices=choices, 
        birim_tipi=birim_tipi, kurum_ici=kurum_ici, disabled=disabled) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('name', field.name)
        kwargs.setdefault('url', field.url)
        kwargs.setdefault('min_input_len', field.min_input_len)
        kwargs.setdefault('multiple', field.multiple)
        kwargs.setdefault('placeholder', field.placeholder)
        kwargs.setdefault('dependent', field.dependent)
        kwargs.setdefault('choices', field.choices)
        kwargs.setdefault('node_name', field.node_name)
        kwargs.setdefault('disabled', field.disabled)
        kwargs.setdefault('kurum_ici', field.kurum_ici)
        kwargs.setdefault('birim_tipi', field.birim_tipi)

        if not field.data:
            field.data = ""

        return HTMLString(
            render_template_string(
                self.data_template, field=field, **kwargs
            )
        )


class SummerNoteWidget(object):
    """
    WYSIWYG Widget
    """
    data_template = """
        {% from "macros/summernote.html" import render_summernote %}
        {{ render_summernote(field) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        kwargs.setdefault('placeholder', field.placeholder)

        if not field.data:
            field.data = ""

        return HTMLString(
            render_template_string(self.data_template, field=field)
        )


# todo write a select with disabling options field.
class SelectWithSelectedDisabledLabel(Select):
    """Select with disabled label"""

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        html = [
            '<select %s>' % html_params(name=field.name, **kwargs),
            self.render_option('', _('Seçiniz...'), True, disabled=True),
        ]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append('</select>')
        return HTMLString(''.join(html))


class FileInputWidget(object):
    """
    Renders a file input chooser field.
    """

    data_template = """
        {% from 'macros/form_helpers/file_upload_fields.html' import default_file %}
        {{ default_file(field=field) }}
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)

        return HTMLString(render_template_string(self.data_template, field=field, **kwargs))
