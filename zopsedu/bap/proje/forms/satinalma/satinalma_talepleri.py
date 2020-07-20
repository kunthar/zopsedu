"""Proje satinalmaya ikiskin formalari icerir"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, FieldList, FormField, StringField, Form
from flask_babel import lazy_gettext as _
from wtforms.validators import ValidationError
from zopsedu.lib.form.fields import CustomFileField, HiddenStringField
from wtforms.validators import Optional, DataRequired

from zopsedu.lib.form.fields import Select2Field, HiddenIntegerField, SummerNoteField
from zopsedu.lib.form.validators import FileExtensionRestriction, FileRequired


class TalepForm(FlaskForm):
    secili_mi = BooleanField(_("Seçiniz"), default=False)
    proje_kalemi_id = HiddenIntegerField(_("PKI"))
    talep_edilen_miktar = IntegerField(default=0)
    teknik_sartname_belge = CustomFileField(_("Dosya Yükle"),
                                            validators=[FileExtensionRestriction(
                                                error_message=_(
                                                    "Lütfen uzantısı geçerli bir dosya yükleyiniz."))])

    proje_kalemi_adi = HiddenStringField(_("Proje Kalemi"))
    toplam_miktar = HiddenIntegerField(_("TM"))
    birim = HiddenStringField(_("Birim"))
    kullanilan_miktar = HiddenIntegerField(_("KulMik"))
    rezerv_edilen_miktar = HiddenIntegerField(_("REM"))
    kullanilabilir_miktar = HiddenIntegerField(_("KulbilM"))

    # toplam_butce = HiddenStringField(_("TB"))
    # kullanilan_butce = HiddenStringField(_("KB"))
    # rezerv_edilen_butce = HiddenStringField(_("REB"))
    # kullanilabilir_butce = HiddenStringField(_("KBB"))

    def validate_talep_edilen_miktar(self, _):
        if self.secili_mi.data:
            if self.talep_edilen_miktar.data <= 0:
                raise ValidationError(
                    message="Seçili kalemlerin talep edilen miktar değeri boş bırakılamaz")
            if self.talep_edilen_miktar.data > self.kullanilabilir_miktar.data:
                raise ValidationError(
                    message="Talep edilen miktar kullanılabilir miktardan büyük olamaz")


class ProjeSatinAlmaTalepleri(FlaskForm):
    urun_secimi_information = [
        _(
            "Ürünleriniz için teknik şartnamenizi 'Teknik Şartname Ekle' butonu ile ekleyebilirsiniz."),
        _("Genel teknik şartname ekle butonu teknik şartname yüklenmeyen "
          "kalemler için ortak şartname eklemek için kullanılır."),
        _("TEKNİK ŞARTNAME DOSYALARINIZI İMZA ETMENİZ ZORUNLUDUR"),
        _("Seçili kalemler için talep edilen miktar değeri yazmak zorundasınız."),
        _("Talep edilen miktar kullanılabilir miktardan büyük olamaz"),
        _("Muayene komisyon üyelerini belirtmek zorundasınız"),
        _('Muayene kabul komisyonu başkanı aksi bir durum oluşmadığı takdirde proje yürütücüsü olmalıdır')
    ]

    talepler = FieldList(FormField(TalepForm), min_entries=0)

    genel_teknik_sartname_belge = CustomFileField(
        _("Genel Teknik Şartname"),
        validators=[FileExtensionRestriction(
            error_message=_("Lütfen uzantısı geçerli bir dosya yükleyiniz."))])

    baskan = Select2Field(label=_('Adı Soyadı'), validators=[
        DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    yedek_baskan = Select2Field(label=_('Adı Soyadı'), validators=[
        DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    uye = Select2Field(label=_('Adı Soyadı'), validators=[
        DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    uye2 = Select2Field(label=_('Adı Soyadı'), validators=[
        DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    yedek_uye = Select2Field(label=_('Adı Soyadı'), validators=[
        DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    yedek_uye2 = Select2Field(label=_('Adı Soyadı'), validators=[
        DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')


class DuyuruForm(FlaskForm):
    duyuru_id = HiddenIntegerField(validators=[DataRequired(message=_("Bu alan boş bırakılamaz"))])
    duyuru_basligi = StringField(label=_('Duyuru Başlığı'),
                                 validators=[DataRequired(message=_("Bu alan boş bırakılamaz"))])
    duyuru_metni = SummerNoteField(_("Duyuru Metni"),
                                   validators=[DataRequired(message=_("Bu alan boş bırakılamaz"))])


class TeknikSartnameDuzenle(Form):
    talep_kalemi_id = HiddenIntegerField(_("KDI"))
    eski_teknik_sartname_id = HiddenIntegerField(_("Eski Teknik Şartname"))
    yeni_teknik_sartname = CustomFileField(_("Dosya Yükle"),
                                           validators=[FileRequired(), FileExtensionRestriction(
                                               error_message=_(
                                                   "Lütfen uzantısı geçerli bir dosya yükleyiniz."))])
    proje_kalemi_adi = HiddenStringField(_("Proje Kalemi"))
    talep_edilen_miktar = HiddenIntegerField()
    birim = HiddenStringField(_("Birim"))


class TeknikSartnameDuzenlemeFormu(FlaskForm):
    uyari_mesajlari = [
        _("Teknik şartnamesi düzenlenmesi gereken talep kalemleri listelenmiştir."),
        _("Listelenen kalemlerin hepsine yeni teknik şartneme yüklemeniz gerekmektedir."),
        _("Yüklediğiniz teknik şartnamenin eski teknik şartname ile aynı olmadığına lütfen dikkat ediniz")
    ]
    talep_kalemleri = FieldList(FormField(TeknikSartnameDuzenle), min_entries=0)
