"""Proje Basvuru Formu"""
from flask_wtf import FlaskForm
from wtforms import FormField
from wtforms.meta import DefaultMeta

from zopsedu.lib.form.fields import DatePickerField, HiddenIntegerField
from zopsedu.bap.lib.form.common import ONERI
from zopsedu.bap.proje.forms.basvuru.genel_bilgiler import GenelBilgilerFormWizardForm
from zopsedu.bap.proje.forms.basvuru.diger import ProjeDigerFormWizardForm
from zopsedu.bap.proje.forms.basvuru.proje_elemanlari import ProjePersoneliFormWizardForm
from zopsedu.bap.proje.forms.basvuru.butce import ProjeButceFormWizardForm


# Arastirma Projesi Formu
class BAPProjeBasvuruFormu(FlaskForm):
    """Yeni başvuru formu"""

    class Meta(DefaultMeta):
        """BapProjeBasvuru Form Meta"""
        form_name = "BAP Proje Basvuru Formu"
        form_type = ONERI
        form_module = "arastirma_projesi"
        will_explored = True
        will_listed = True

    kayit_tarihi = DatePickerField(label='Kayit Tarihi')

    genel_bilgiler = FormField(GenelBilgilerFormWizardForm)
    proje_personeli = FormField(ProjePersoneliFormWizardForm)
    diger = FormField(ProjeDigerFormWizardForm)
    butce = FormField(ProjeButceFormWizardForm)
    proje_turu = HiddenIntegerField()

    # pylint: disable=too-many-arguments
    def __init__(self, formdata=None, obj=None, prefix='', data=None, meta=None, **kwargs):
        super().__init__(formdata=formdata, obj=obj, prefix=prefix, data=data, meta=meta, **kwargs)
        # pylint: enable=too-many-arguments
