"""Bap firma satinalma teklif formlari"""

from flask_wtf import FlaskForm
from wtforms import Form, SelectField
from wtforms.meta import DefaultMeta
from wtforms import StringField, FileField, FormField, IntegerField, FieldList, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from flask_babel import gettext as _

from zopsedu.bap.models.firma_teklif import DosyaKategori
from zopsedu.lib.form.validators import FileExtensionRestriction
from zopsedu.lib.form.fields import DatePickerField, Select2Field, HiddenIntegerField, \
    HiddenStringField, ZopseduDecimalField
from zopsedu.lib.form.validators import CustomFileFieldRequired, DecimalLength


class TalepKalemi(Form):
    talep_kalemi_id = HiddenIntegerField(_("STKI"))
    kalem_adi = StringField(_("Kalem Adı"), validators=[Length(max=255)])
    sayi = IntegerField(_("Talep Sayısı"))
    birim = StringField(_("Talep Birimi"))
    teknik_sartname_id = IntegerField(_("Teknik Şartname"))


class FirmaUrunTeklif(Form):
    class Meta(DefaultMeta):
        locales = ["tr"]

    talep_kalemi = FormField(TalepKalemi)
    marka_model = StringField(_("Marka Model"), validators=[Length(max=255)])
    birim_fiyati = ZopseduDecimalField(
        _('Birim Fiyatı(TL)'),
        validators=[
            Optional(),
            DecimalLength(max_length=10,
                          error_message="Birim Fiyatı için en fazla 10 "
                                        "haneli bir değer girebilirsiniz")])
    kdv_orani = ZopseduDecimalField(
        _('KDV Oranı'),
        validators=[
            Optional(),
            DecimalLength(max_length=3,
                          error_message="KDV oranı için en fazla 3 "
                                        "haneli bir değer girebilirsiniz")])
    teslimat_suresi = IntegerField(_("Teslimat Süresi(Gün)"))


class TeklifFormu(FlaskForm):
    """Firma satinalma teklif formu"""
    uyarilar = [
        _("Lütfen tekliflerinizi KDV hariç veriniz."),
        _("Teklifinizde herhangi bir ürünü boş bırakabilirsiniz"),
        _("Birim fiyatı girmediğiniz ürün dikkate alınmayacaktır."),
        _("Teklif vereceginiz ürünün bütün alanlarını doldurmak zorundasınız.")
    ]
    urunler = FieldList(FormField(FirmaUrunTeklif), min_entries=0)
    aciklama = TextAreaField(_("Açıklama"),
                             validators=[DataRequired(_("Açıklama alanı boş bırakılamaz"))])


class TeklifDosyasi(Form):
    dosya = FileField(_("Dosya"), validators=[
        CustomFileFieldRequired(error_message=_("Dosya Yüklemek Zorundasınız.")),
        FileExtensionRestriction(error_message=_("Lütfen uzantısı geçerli bir dosya yükleyiniz."))],
                      render_kw={"class": "form-control"})
    kategori = SelectField("Dosya Tipi",
                           choices=DosyaKategori.choices(),
                           default=DosyaKategori.teklif_mektubu,
                           coerce=DosyaKategori.coerce,
                           render_kw={"class": "form-control"})
    aciklama = StringField(_("Açıklama"), validators=[
        DataRequired(message=_("Açıklama alanını doldurmak zorundasınız"))],
                           render_kw={"class": "form-control"})


class TeklifDosyalari(FlaskForm):
    uyarilar = [
        _("Teklik mektubunun çıktısı alınıp ıslak imza atılarak mühürlenmesi gerekmektedir."),
        _("Gerekli işlemleri yaptığınız dosyanın taratılarak sisteme yüklenmesi gerekmektedir"),
        _("Teklif Mektubu eklemeden başvurunuzu tamamlayamazsınız"),
        _("Eklemek istediğiniz diğer dosyaları ekleyebilirsiniz")
    ]
    dosyalar = FieldList(FormField(TeklifDosyasi), min_entries=1)
