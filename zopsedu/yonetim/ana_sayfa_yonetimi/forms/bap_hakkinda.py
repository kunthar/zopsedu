from flask_wtf import FlaskForm
from flask_babel import gettext as _
from zopsedu.lib.form.fields import SummerNoteField


class BAPHakkindaForm(FlaskForm):
    bap_hakkinda_metni = SummerNoteField(_("BAP Hakkında Metni"))
