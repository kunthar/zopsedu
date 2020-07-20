from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField
from wtforms.meta import DefaultMeta
from flask_babel import lazy_gettext as _

from zopsedu.bap.lib.form.common import HAKEM_SONUC_RAPORU


class HakemSonucRaporuFormu1(FlaskForm):
    """Example form to test migrate_forms command"""

    class Meta(DefaultMeta):
        """Example Form Meta"""
        form_name = "Hakem Sonuc Raporu Örnek Form 1"
        form_type = HAKEM_SONUC_RAPORU
        form_module = "proje_turu"
        will_explored = True
        will_listed = True

    boolean_field_ornegi = BooleanField(_("Boolean Field Ornegi"))
    text_area_field_ornegi = TextAreaField(_("Text Field Ornegi"))
