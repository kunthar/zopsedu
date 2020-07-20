"""Proje Basvuru Diger Formlar"""
from flask_babel import gettext as _
from wtforms import Form, StringField, FormField, FieldList
from wtforms.validators import Optional, Length
from zopsedu.lib.form.fields import Select2Field, HiddenBooleanField
from zopsedu.lib.form.fields import HiddenIntegerField, CustomFileField, HiddenStringField
from zopsedu.lib.form.validators import FileExtensionRestriction
from zopsedu.lib.helpers import SABLON_FILE_EXTENTIONS

file_extention_uyari_mesaji = _("İzin verilen dosya uzantıları: {}".format(
    '%s' % ', '.join(SABLON_FILE_EXTENTIONS.keys())))


class ProjeEkDosyalar(Form):
    """
    Proje EkDosyalarını İçeren Form

    ek_dosya ile baslayan alanlar proje türünde dosya yüklenirken eklenen
    verilerdir(ad, acıklama, zorunlu_mu gibi). Bu alanlar proje basvuran kişiye bilgi vermek
    amacıyla kullanılır

    yeni ile baslayan alanlar proje basvurusunda basvuran kişinin eklediği alanlardır
    """
    form_title = _('Proje Sunum')
    ek_dosya_ad = HiddenStringField(_("Dosya Ad"), validators=[Length(max=100)])
    ek_dosya_aciklama = HiddenStringField(_("Dosya Açıklama"))
    ek_dosya_zorunlu_mu = HiddenBooleanField(_("Zorunlu Mu"), default=False)
    ek_dosya_id = HiddenIntegerField(_("Dosya"))
    proje_turu_ek_dosya_id = HiddenIntegerField(_("Ek Dosya Id"))
    yeni_dosya_aciklama = StringField(_('Açıklama'))
    yeni_dosya = CustomFileField(_('Dosya Yükle'), render_kw={"class": "form-control"},
                                 validators=[
                                     FileExtensionRestriction(
                                         allowed_extentions=SABLON_FILE_EXTENTIONS,
                                         error_message=file_extention_uyari_mesaji)])


class DigerDosyalarForm(Form):
    """
    Diğer dosyalar formu
    """
    proje_belge_id = HiddenIntegerField(validators=[Optional()])
    dosya_id = CustomFileField(_('Dosya Yükle'), render_kw={"class": "form-control"},
                               validators=[
                                   FileExtensionRestriction(
                                       allowed_extentions=SABLON_FILE_EXTENTIONS,
                                       error_message=file_extention_uyari_mesaji)])
    ad = StringField(_("Dosya Ad"), render_kw={"class": "form-control"})
    aciklama = StringField(_("Aciklama"), render_kw={"class": "form-control"})


class ProjeDigerDosyalarForm(Form):
    """
    Proje diğer dosyalar form
    """
    form_title = _('Diğer Dosyalar')
    form_alert = _("""Zorunlu dosyalar kısmında olmayan ve projenin içeriği ve konusuyla ilintili olan
    diğer belgelerin tümü eklenebilir. Örneğin; diğer resmi kamu kurum ve kuruluşlarından alınması 
    zorunlu olan izin, onay ve yazılar vb. """)
    headers = [_('Seç'), _('Dosya Adı'), _('Boyut'), _('Tarih')]

    dosyalar = FieldList(FormField(DigerDosyalarForm), min_entries=1)


class HakemOneri(Form):
    """Hakem Oneri Formu"""
    ad = StringField(_("Ad"), validators=[Length(max=50)])
    soyad = StringField(_("Soyad"), validators=[Length(max=50)])
    email = StringField(_("Email"), validators=[Length(max=80)])
    ogretim_elemani_id = Select2Field(_("Öğretim Üyesi Seç"),
                                      url="/select/ogretim-uyesi",
                                      placeholder=_("Öğretim Üyesi"))


class ProjeHakemOnerForm(Form):
    """
    Hakem öneri formu
    """
    form_title = _('Hakem Önerileri')
    form_alert = _("Projenizin değerlendirmeye alınabilmesi için en az {hakem_sayi} adet hakem "
                   "önerisinde bulunmanız gerekmektedir.")
    headers = [_('Hakem'), _('E-posta')]
    yeni_hakem_mesaj = _('Yeni Hakem Ekle')
    yeni_hakem_db_mesaj = _('Veritabanından Hakem Ekle')
    hakem_oneri = FormField(HakemOneri)


class ProjeDigerFormWizardForm(Form):
    """
    Arastirma Projesi basvurusu Diğer Form Wizard adımı içindeki panelleri barındıran
    form classı

    """
    form_title = _('Diğer')
    ek_dosyalar = FieldList(FormField(ProjeEkDosyalar), min_entries=0)
    proje_diger = FormField(ProjeDigerDosyalarForm)
    proje_hakem = FormField(ProjeHakemOnerForm)
    tabs = {
        "zorunlu-dosyalar": _('Zorunlu Dosyalar'),
        "diger-dosyalar": _('Diğer Dosyalar'),
        "hakem-onerileri": _('Hakem Önerileri'),
    }
