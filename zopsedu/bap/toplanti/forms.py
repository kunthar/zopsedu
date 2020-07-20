"""ToplantiView Formlari"""
from wtforms import BooleanField, Form, IntegerField
from wtforms import SubmitField, SelectField, StringField, DateTimeField, FormField, FieldList
from wtforms.validators import InputRequired, Length
from flask_babel import gettext as _
from flask_wtf import FlaskForm

from zopsedu.lib.db import DB
from zopsedu.lib.form.fields import HiddenIntegerField, MultiFileField, SummerNoteField, MultiCheckboxField
from zopsedu.lib.form.fields import DateTimePickerField, HiddenStringField, DatePickerField
from zopsedu.bap.models.helpers import ToplantiDurumu, GundemTipi, KararDurumu, GundemDurumu
from zopsedu.models import AppState
from zopsedu.models.helpers import AppStates, StateTypes


class DatePickerForm(Form):
    """Example form for Date Picker"""
    toplanti_tarihi = DatePickerField(_('Toplantı Tarihi'), disable_older_dates=False)
    toplanti_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)


class DatePickerProjeForm(Form):
    """Example form for Date Picker"""
    baslama_tarihi = DatePickerField(_('Başlama Tarihi'), disable_older_dates=False)
    bitis_tarihi = DatePickerField(_('Bitiş Tarihi'), disable_older_dates=False)
    baslama_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)
    bitis_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)


class GundemListItemForm(FlaskForm):
    """Gundem listeleme formu"""
    toplantiya_alinsin = BooleanField("")
    proje_id = HiddenIntegerField()
    id = HiddenIntegerField()
    aciklama = HiddenStringField()


class ToplantiOlusturForm(FlaskForm):
    """Toplanti olusturma formu"""
    toplanti_tarih_saat = DateTimePickerField(
        _('Toplantı Tarih/Saat'),
        format="%Y-%m-%d %H:%M",
        validators=[InputRequired()]
    )
    gundem_listesi = FieldList(FormField(GundemListItemForm))


class ToplantiEkleForm(FlaskForm):
    """Toplanti Ekleme Formu"""
    toplanti_tarihi = DatePickerField(label=_('Toplantı Tarihi'), disable_older_dates=False)
    toplanti_durumu = SelectField(label=_('Toplantı Durumu '), choices=ToplantiDurumu.choices())
    ekle = SubmitField(label=_('Ekle'))


class ToplantiGundem(FlaskForm):
    """Toplanti gundem formu"""

    information = [
        "Toplantıya katılımcı eklemeden toplantıyı sonuçlandıramazsınız.",
        "Toplantıyı sonuçlandırabilmek için toplantıda bulunan bütün gündemlerin karar durumlarının belirlenmesi gerekir.",
        "Toplantıyı sonuçlandırdıktan sonra toplantıya gündem/karar ekleyip çıkaramaz var olan kararlarda düzenleme yapamazsınız.",
        "Toplantıyı sonuçlandırdığınızda toplantı durumu sistem tarafından 'gerçekleşti' olarak degiştirilir.",

    ]
    gundem_id = HiddenIntegerField()
    proje_id = HiddenIntegerField()
    toplanti_id = HiddenIntegerField()
    sablon_id = HiddenIntegerField()

    ek_dosya_id = MultiFileField("Gündeme Ait Ek Dosya")
    karar = SummerNoteField(_("Karar"))
    aciklama = SummerNoteField(_("Gündem"))
    tipi = SelectField(_("Gündem Tipi"),
                       choices=GundemTipi.choices(),
                       coerce=GundemTipi.coerce)
    karar_durum = SelectField(_("Karar Durumu"),
                              choices=KararDurumu.choices(),
                              coerce=KararDurumu.coerce)

    sablon = SelectField(_("Gündem Şablonu"))

    gundem_sira_no = SelectField(_("Gündem Sıra No"), coerce=int)
    yonetime_bilgi_notu = SummerNoteField(_("Yönetime Bilgi Notu"))
    kisiye_ozel_not = SummerNoteField(_("Kişiye Özel Not"))

    proje_basligi = StringField("Proje Adı", validators=[Length(max=255)])


class DegerlendirilmemisGundemFiltreleForm(FlaskForm):
    """ Değerlendirilmemiş Gündemler Filtre Formu """
    gundem_tipi = SelectField(label=_('Gündem Tipi'))
    gundem_durumu = SelectField(label=_('Gündem Durumu'))
    date = FormField(DatePickerForm)
    proje_numarasi = StringField(label=_('Proje Numarası'), validators=[Length(max=20)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gundem_tipi_choices = GundemTipi.choices()
        gundem_tipi_choices.insert(0, ("tüm_gündemler", "Tüm Gündemler"))
        self.gundem_tipi.choices = gundem_tipi_choices

        gundem_durumu_choices = GundemDurumu.choices()
        gundem_durumu_choices.insert(0, ("tüm_durumlar", "Tüm Durumlar"))
        self.gundem_durumu.choices = gundem_durumu_choices

    def validate(self):
        if not any([self.proje_numarasi.data, self.date.toplanti_tarihi.data]):
            return False
        return True


class ProjeFiltreleForm(FlaskForm):
    """Proje Arama Formu"""
    ad = StringField(label='Proje Adı', validators=[Length(max=50)])
    proje_no = IntegerField(label="Proje Numarası", validators=[Length(max=20)])

    proje_sureci = SelectField(label=_('Projelerin Genel Süreci'),
                               choices=[("-1", "Tümü"),
                                        (AppStates.basvuru_kabul, AppStates.basvuru_kabul.value),
                                        (AppStates.devam, AppStates.devam.value),
                                        (AppStates.son, AppStates.son.value)],
                               default="-1")
    date = FormField(DatePickerProjeForm)

    proje_durumu = SelectField(label="Proje Durum Kodu")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        durumlar = DB.session.query(AppState).filter(AppState.state_type == StateTypes.proje).all()

        durum_list = [(0, _("Tüm Durumlar"))]

        for durum in durumlar:
            durum_list.append((durum.id, durum.state_code))

        self.proje_durumu.choices = durum_list
        self.proje_durumu.default = 0

    def validate(self):
        if not any([self.ad.data,
                    self.proje_no.data,
                    self.proje_durumu.data]):
            return False
        return True


class Toplanti(FlaskForm):
    """Toplanti Formu"""
    toplanti_id = HiddenIntegerField()
    toplanti_tarihi = DateTimeField(_("Toplantı Tarihi"))
    gundemler = FieldList(FormField(ToplantiGundem))


class ToplantiKararFiltreleForm(FlaskForm):
    """Toplanti kararlarını filtreler"""
    ara_text = StringField(label=_('Karar'))
    ara = SubmitField(label=_('Ara'))
    tarih_arama = FormField(DatePickerForm)
    temizle = SubmitField(label=_('Temizle'))

    choices = GundemTipi.choices()
    choices.insert(0, ("-1", "Tümü"))
    gundem_tipi = SelectField(label=_('Gündem Tipi'), choices=choices, default='-1')

    def validate(self):
        if not any([self.ara_text.data, self.tarih_arama.toplanti_tarihi.data]):
            return False
        return True


class ToplantiKatilimciForm(FlaskForm):
    secili_mi = BooleanField(_("Seçiniz"), default=False)
    idari_personel_id = HiddenIntegerField("IPI")
    ad = HiddenStringField(_("İsim Soyisim"))
    gorevi = HiddenStringField(_("Görevi"))


class ToplantiKatilimciEkleForm(FlaskForm):
    katilimcilar = FieldList(FormField(ToplantiKatilimciForm), min_entries=0)


class ProjeSec(Form):
    secili_mi = BooleanField("Proje Seçiniz")
    proje_id = HiddenIntegerField("Proje Id")
    proje_durum_aciklamasi = HiddenStringField("ProjeDurumAciklamasi")
    proje_baslik = HiddenStringField("ProjeBaslik")
    proje_no = HiddenStringField("ProjeNo")
    bitis_tarihi = HiddenStringField("BitisTarihi")
    kabul_edilen_baslama_tarihi = HiddenStringField("KabulEdilenBaslamaTarihi")


class GundemOlustur(FlaskForm):
    information = [
        "Gündem oluşturmak istediğiniz projeleri seçiniz",
        "Seçilen gündem tipi şablonundan otomatik olarak gündem ve karar metinleri oluşturulacaktır.",
        "Gündem şablonlarını yönetim bölümünün altında bulunan gündem şablonları bölümünden düzenleyebilirsiniz"
        "Gündemler sayfasından oluşturulan gündemleri düzenleyebilir ve toplantıya atayabilirsiniz"
    ]

    projeler = FieldList(FormField(ProjeSec), min_entries=0)
    gundem_tipi = SelectField("Gündem Tipi", choices=GundemTipi.choices(), coerce=GundemTipi.coerce,
                              default=GundemTipi.projenin_desteklenmesi)


class ToplantiFiltreleForm(FlaskForm):
    date = FormField(DatePickerForm)
    choice = ToplantiDurumu.choices()
    choice = [('0', 'Hepsi')] + choice
    toplanti_durumu = SelectField(label='Toplantı Durumu', choices=choice, default=0)

    def validate(self):
        if any([self.date.toplanti_tarihi.data]):
            return True
        return False
