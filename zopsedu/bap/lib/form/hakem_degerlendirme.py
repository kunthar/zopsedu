from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, BooleanField
from wtforms.meta import DefaultMeta
from flask_babel import lazy_gettext as _

from zopsedu.bap.models.helpers import WTFormEnum
from zopsedu.bap.lib.form.common import HAKEM_DEGERLENDIRME


class HakemDegerlendirmeSonuc(str, WTFormEnum):
    desteklenmeli = "Proje Önerilen Haliyle Desteklenmeli"
    duzeltilmeli = "Proje önerisi desteklenecek nitelikte; ancak ekteki önerilere göre düzeltilmeli"
    desteklenmemeli = "Proje önerilen haliyle desteklenecek nitelikte değil."


class HakemDegerlendirmeFormu(FlaskForm):
    """Example form to test migrate_forms command"""

    class Meta(DefaultMeta):
        """Example Form Meta"""
        form_name = "Hakem Degerlendirme Örnek Form 1"
        form_type = HAKEM_DEGERLENDIRME
        form_module = "proje_turu"
        will_explored = True
        will_listed = True

    boolean_field_ornegi = BooleanField(_("Boolean Field Ornegi"))
    select_field_ornegi = SelectField(_("Select Field Ornegi"), choices=[(HakemDegerlendirmeSonuc.desteklenmeli.name, HakemDegerlendirmeSonuc.desteklenmeli.value)])
    text_area_field_ornegi = TextAreaField(_("Text Field Ornegi"))


class HakemDegerlendirmeFormu2(FlaskForm):
    """Example form to test migrate_forms command"""

    class Meta(DefaultMeta):
        """Example Form Meta"""
        form_name = "Hakem Degerlendirme Örnek Form 2"
        form_type = HAKEM_DEGERLENDIRME
        form_module = "proje_turu"
        will_explored = True
        will_listed = True

    boolean_field_ornegi = BooleanField(_("Boolean Field Ornegi"))
    select_field_ornegi = SelectField(_("Select Field Ornegi"), choices=[(HakemDegerlendirmeSonuc.desteklenmeli.name, HakemDegerlendirmeSonuc.desteklenmeli.value)])
    text_area_field_ornegi = TextAreaField(_("Text Field Ornegi"))
