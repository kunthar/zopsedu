"""proje hakem form modülü"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from zopsedu.lib.form.fields import Select2Field


class HakemEkleForm(FlaskForm):
    """hakem atama form classi"""
    hakem_id = Select2Field(_("Hakem Ara"), url="/select/hakem")
