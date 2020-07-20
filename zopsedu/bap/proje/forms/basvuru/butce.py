"""Proje Basvuru Butce Formlari"""
from flask_babel import gettext as _
from wtforms import Form, StringField, FormField, FieldList, IntegerField
from wtforms.meta import DefaultMeta
from wtforms.validators import Optional

from zopsedu.lib.form.fields import SelectWithDisableField, HiddenIntegerField, ZopseduDecimalField
from zopsedu.bap.models.helpers import OlcuBirimi
from zopsedu.lib.form.validators import DecimalLength


class AlimForm(Form):
    """
    Arastirma Projesi basvurusu Bütçe Form Wizard adımının içindeki projenin hizmet, tüketime
    yönelik mal ve malzeme, menkul mal, gayrimaddi hak alım, bakım onarım ve giderleri, vs.
    bilgilerin tutulacağı form classı

    """

    class Meta(DefaultMeta):
        locales = ["tr"]

    ad = StringField(_('Ad'), render_kw={"class": "form-control"})
    gerekce = StringField(_('Açıklama/Gerekçe'), render_kw={"class": "form-control"})
    onerilen_miktar = IntegerField(_('Miktar'), default=0,
                                   render_kw={"class": "form-control", "type": "number"})
    birim = SelectWithDisableField(_('Birim'),
                                   choices=OlcuBirimi.choices(),
                                   default=OlcuBirimi.adet,
                                   coerce=OlcuBirimi.coerce,
                                   render_kw={"class": "form-control"})
    onerilen_yil_1 = ZopseduDecimalField(_('1. Yıl'),
                                         validators=[
                                             Optional(),
                                             DecimalLength(max_length=10,
                                                           error_message="Bütçe 1. yıl için en fazla 10 "
                                                                         "haneli bir değer girebilirsiniz")
                                         ])
    onerilen_yil_2 = ZopseduDecimalField(_('2. Yıl'),
                                         validators=[
                                             Optional(),
                                             DecimalLength(max_length=10,
                                                           error_message="Bütçe 2. yıl için en fazla 10 "
                                                                         "haneli bir değer girebilirsiniz")
                                         ])
    onerilen_yil_3 = ZopseduDecimalField(_('3. Yıl'),
                                         validators=[
                                             Optional(),
                                             DecimalLength(max_length=10,
                                                           error_message="Bütçe 3. yıl için en fazla 10 "
                                                                         "haneli bir değer girebilirsiniz")
                                         ])


class ButceKalemiFormu(Form):
    """
    Butce Kalemleri Formu
    """

    class Meta(DefaultMeta):
        locales = ["tr"]

    butce_kalemi_id = HiddenIntegerField("Butce Kalemi id")
    gider_siniflandirma_id = HiddenIntegerField("SBKİ")
    butce_kalemi_adi = StringField("BKA")
    butce_alt_limiti = ZopseduDecimalField("BAL")
    butce_ust_limiti = ZopseduDecimalField("BUS")
    alimlar = FieldList(FormField(AlimForm), min_entries=1)
    yolluklar = FieldList(FormField(AlimForm), min_entries=2)


class ProjeButceFormWizardForm(Form):
    """
    Arastirma Projesi basvurusu Bütçe Form Wizard adımı içindeki panelleri barındıran
    form classı
    """
    form_title = _('Bütçe')
    form_description_list = [
        _('Bütçe bölümüne yazılacak tüm kalemlerin değerleri TL cinsinden olmalıdır.'),
    ]

    labels = {
        "yil_1": _('1. Yıl'),
        "yil_2": _('2. Yıl'),
        "yil_3": _('3. Yıl'),
        "toplamlar": _('Toplamlar'),
        "yillara_gore_toplamlar": _('Yıllara Göre Toplamlar'),
        "genel_toplam": _('Genel Toplam'),
        "onerilen_toplam_kdv": _('Önerilen Toplam (KDV dahil)'),
        "ek_malzeme_toplam_kdv": _('Ek Malzeme Toplam (KDV dahil)'),
    }
