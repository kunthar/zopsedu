from importlib import import_module

from flask import render_template
from flask_classful import FlaskView, route

from zopsedu.lib.db import DB
from zopsedu.models import Form


class FormPreview(FlaskView):
    route_base = "/form"

    @staticmethod
    @route('/<string:form_name>/onizle')
    def form_preview(form_name):
        """
        Form önizlemek için kullanılır
        Args:
            form_name: formun ismi

        Returns: rendered template

        """
        form = DB.session.query(Form).filter_by(form_name=form_name).first()
        if not form:
            return "Form Bulunamadı"
        form_class = getattr(import_module(form.form_import_path), form.form_class_name)
        form_instance = form_class()
        return render_template('form_preview.html', form=form_instance)
