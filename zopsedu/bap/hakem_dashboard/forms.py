"""Proje Değerlendirme Form"""
from uuid import uuid4

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, TextAreaField, validators, SelectField, Form
from zopsedu.lib.form import fields
from zopsedu.bap.models.helpers import ProjeDegerlendirmeSecenekleri
from zopsedu.bap.models.helpers import ProjeDegerlendirmeSonuc
from zopsedu.lib.form.fields import MultiFileField, SummerNoteField

# pylint: disable=invalid-name
proje_degerlendirme_secenekleri = [
    (choice.name, choice.value) for choice in ProjeDegerlendirmeSecenekleri
]


# pylint: enable=invalid-name


class ProjeDegerlendirmeForm(FlaskForm):
    """Example hakem proje degerlendirme formu"""

    proje_konusu = fields.RadioButtonField(
        _('Proje konusu özgün mü?'), choices=proje_degerlendirme_secenekleri)
    proje_amaci = fields.RadioButtonField(
        _('Proje amacı açık bir şekilde belirtilmiş mi?'),
        choices=proje_degerlendirme_secenekleri)
    proje_bilimsel = fields.RadioButtonField(
        _('Proje amacı bilimsel bakımdan anlamlı mı?'), choices=proje_degerlendirme_secenekleri)
    proje_katki = fields.RadioButtonField(
        _('Tamamlandığında sonuçları ile alanında bilime evrensel ve ulusal ölçülerde katkı '
          'yapması ve ülkenin teknolojik, ekonomik ve sosyo-kültürel kalkınmasına yönelik '
          'katkıları var mı ve gerçekçi mi?'),
        choices=proje_degerlendirme_secenekleri)
    proje_temeli = fields.RadioButtonField(
        _('Projenin kuramsal temeli yeterli düzeyde literatür '
          'araştırılması yapılarak verilmiş mi?'),
        choices=proje_degerlendirme_secenekleri)
    proje_metot = fields.RadioButtonField(
        _('Projede uygulanacak metotlar açık bir şekilde verilmiş mi?'),
        choices=proje_degerlendirme_secenekleri)
    proje_arastirma = fields.RadioButtonField(
        _('Proje araştırma yöntemi amacı ile tutarlı mı?'),
        choices=proje_degerlendirme_secenekleri)
    proje_takvimi = fields.RadioButtonField(
        _('Proje takviminde yer alan işler ve iş süreleri proje araştırma yönetimi ile uyumlu mu?'),
        choices=proje_degerlendirme_secenekleri)
    sarf_techizat = fields.RadioButtonField(
        _('Talep edilen sarf ve teçhizat, araştırmanın amacı ve var olan alt yapı ile uyumlu mu?'),
        choices=proje_degerlendirme_secenekleri)
    sanayi = fields.RadioButtonField(
        _('Proje sanayide uygulanabilir mi?'), choices=proje_degerlendirme_secenekleri)
    etik_kurul = fields.RadioButtonField(
        _('Etik Kurul Kararı gerekli mi?'), choices=proje_degerlendirme_secenekleri)
    gorus_oneri_degisiklik = TextAreaField(
        label=("Lütfen varsa görüş ve önerilerinizi belirtiniz."),
        render_kw={"placeholder": "Görüş / Öneri / Değişiklik"}
    )
    dosya = BooleanField(label=_("Değerlendirmeye ek olarak, "
                                 "bilgisayarımdan dosya seçerek yüklemek istiyorum"),
                         default=False)
    dosya_id = MultiFileField(label=_("Dosya Ekle"),
                              validators=[validators.optional()], ids=uuid4().hex)

    degerlendirme_sonucu = fields.RadioButtonField(
        _('Lütfen inceleme sonucunuzu işaretleyiniz?'),
        choices=[(choice.name, choice.value) for choice in ProjeDegerlendirmeSonuc])

    degerlendirme_tamamlandi = BooleanField(label=_("Proje değerlendirmesi tamamlandı."),
                                            default=False)


class RaporDegerlendirmeForm(Form):
    ara_form = SummerNoteField()
    sonuc_form = SummerNoteField()


class ProjeDegerlendirmeFormu(FlaskForm):
    information = [
        _(
            "Değerlendirmeyi tamamlayabilmek için tamamlandı seçeneğini işaretleyip kaydetmeniz gerekir"),
        _(
            "Tamamladığınız değerlendirmeyi güncellemeniz mümkun değildir.(Yetkili ile iletişime geçmeniz gerekir) "),
    ]
    degerlendirme_metni = SummerNoteField()
    degerlendirme_sonucu = SelectField(_("Değerlendirme Sonucu"),
                                       choices=ProjeDegerlendirmeSonuc.choices(),
                                       coerce=ProjeDegerlendirmeSonuc.coerce)
    degerlendirme_tamamlandi_mi = BooleanField(label=_("Değerlendirme Tamamlandı Mı?"),
                                               default=False)


class HakemProjeDegerlendirmeForm(FlaskForm):
    degerlendirme_metni = SummerNoteField("Degerlendirme Metni")
    degerlendirme_sonucu = fields.RadioButtonField(
        _('Lütfen inceleme sonucunuzu işaretleyiniz?'),
        choices=[(choice.name, choice.value) for choice in ProjeDegerlendirmeSonuc])

    degerlendirme_tamamlandi = BooleanField(label=_("Proje değerlendirmesi tamamlandı."),
                                            default=False)
