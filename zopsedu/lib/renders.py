"""Template Renderer"""
import os
from secretary import Renderer, SecretaryError
from flask import current_app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TRenderer(object):
    """Döküman renderer"""

    def __init__(self, template=None, context=None):
        """
        Şablon ve şablon içinde kullanılacak değişkenler

        Usage:
            t = TRenderer(template=f, context={"name": "Cem",})
            rendered_doc = t.render_document

        Args:
            template (file): file or file like object
            context (dict): context variables
        """
        self.template = template
        self.context = context
        self.engine = Renderer()

    def render_document(self):
        """
        Sablonu verilen degiskenler ile isleyip dondurur.

        Returns:
            (file): islenmis file like object

        """
        try:
            return self.engine.render(self.template, **self.context)
        except SecretaryError as exception:
            current_app.logger.error(str(exception))
