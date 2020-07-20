from flask_wtf import FlaskForm, Form
from wtforms import StringField, FormField, FieldList
from flask_babel import lazy_gettext as _

from zopsedu.lib.form.fields import CustomFileField
from zopsedu.lib.form.validators import FileExtensionRestriction


class AnaSayfaDosyaAyarlari(FlaskForm):
    file_id = CustomFileField(_("Dosya"),
                              render_kw={"class": "form-control"},
                              validators=[FileExtensionRestriction(
                                  error_message=_("Lütfen uzantısı geçerli bir dosya yükleyiniz."))])
