"""proje degerlendirme form modülü"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from zopsedu.lib.form.fields import SummerNoteField


class DegerlendirmeGuncelleForm(FlaskForm):
    """Degerlendirme guncelleme formu"""
    degerlendirme_metni = SummerNoteField(_("Degerlendirme Güncelle"))
