from datetime import datetime

from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import validators, BooleanField, Form, FieldList, FormField, IntegerField, StringField, \
    ValidationError

from zopsedu.lib.form.fields import SummerNoteField, DatePickerField, Select2Field, \
    HiddenIntegerField, HiddenStringField


class GenelIslemler(Form):
    islem_tarihi = DatePickerField("İşlem Tarihi :", format='%d.%m.%Y',
                                   default=datetime.today(),
                                   validators=[validators.DataRequired(
                                       message=_("İşlem Tarihi  Giriniz"))],
                                   disable_older_dates=False)

    bap_admin_log = SummerNoteField(
        label=_('İşlemin Açıklaması (Yöneticilere gönderilecek)'))
    yurutucu_log = SummerNoteField(
        label=_('İşlemin Açıklaması (Proje yürütücüsüne gönderilecek)'))

    email = BooleanField(
        label=_('Proje yürütücüsü e-mail yolu ile bilgilendirilsin.')
    )


class TalepKalemi(Form):
    talep_kalemi_id = HiddenIntegerField(_("STKI"))
    kalem_adi = StringField(_("Kalem Adı"))
    talep_miktari = IntegerField(label=_("Talep Miktarı"))
    birim = StringField(_("Talep Birimi"))


class TalepKalemiWithTeknikSartname(TalepKalemi):
    secili_mi = BooleanField("Seçiniz")
    teknik_sartname_id = HiddenIntegerField("Teknik Şartname")


class SiparisTakip(Form):
    secili_mi = BooleanField(_("Seçiniz"))
    siparis_id = HiddenIntegerField(_("HSI"))
    firma_adi = HiddenStringField()
    proje_kalemi_adi = HiddenStringField()
    talep_miktari = HiddenIntegerField()
    birim = HiddenStringField()
    teslim_suresi = HiddenIntegerField()


class SiparisFatura(SiparisTakip):
    fatura_no = StringField(_("Fatura No"))
    fatura_tarihi = DatePickerField("Fatura Tarihi", format='%d.%m.%Y',
                                    default=datetime.today(),
                                    validators=[validators.DataRequired(
                                        message=_("Fatura tarihi giriniz"))],
                                    disable_older_dates=False,
                                    disable_further_dates=True)

    def validate_secili_mi(self, _):
        if self.secili_mi.data:
            if not self.fatura_no.data or not self.fatura_tarihi.data:
                raise ValidationError(message="Bütün alanlarını doldurunuz.")


class DurumFormlari:
    class GenelForm(FlaskForm, GenelIslemler):
        pass

    class ST5(FlaskForm, GenelIslemler):
        duyuru_icerigi = SummerNoteField(
            label=_('Duyuru Metni'),
            validators=[
                validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            ], default="BU ŞABLONDUR AYARLARA EKLENEMLİDİR")

        baslangic_tarihi = DatePickerField("Başlangıç Tarihi :", format='%d.%m.%Y',
                                           default=datetime.today(),
                                           validators=[validators.DataRequired(
                                               message=_("Başlangıç Tarihini  Giriniz"))],
                                           disable_older_dates=False)

        bitis_tarihi = DatePickerField("Bitiş Tarihi :", format='%d.%m.%Y',
                                       default=datetime.today(),
                                       validators=[validators.DataRequired(
                                           message=_("Bitiş Tarihini Giriniz"))],
                                       disable_older_dates=False)

    class ST6(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Bu işlemi yaptığınızda satınalmaya ilişkin duyuru kaldırılır."),
            _("Duyuru kaldırıldıktan sonra firmalar satınalma kalemlerine teklif yapamaz"),
        ]

    class ST7(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Satınalma talep kalemleri ve talebi karşılayacak firmalar aşağıda listelenmiştir"),
            _("Düzenleme yapmak için firmalar bölümünü kullanmanız gerekmektedir."),
            _("Bu aşamadan sonra firma tekliflerinde düzenleme yapamazsınız"),
            _("İşlem onaylandıktan sonra ilgili firmalara sipariş durumu bildirilecektir.")
        ]

    class ST9(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Satınalma talebini tamamalabilmeniz için;"),
            _("Talep edilen bütün ürünlerin siparişinin verilmiş olması,"),
            _("Bütün siparişlerin faturalarının firmalardan teslim alınması gerekiyor."),
            _("Eğer gerekli şartları sağlamıyor ise \"Satınalma İşlemleri Kısmen Tamamlandı\" durumuna geçebilirsiniz."),
            _("Bu işlemden sonra muhasebe fişleri bölümünden ödeme emri oluşturabilirsiniz."),

        ]

    class ST10(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Satınalma talebini kısmen tamamalabilmeniz için;"),
            _("Siparişi verilen ürünlerin durumlarının \"Firma Faturası Teslim Alındı\", \"Sipariş Tamamlandı\" veya \"Sipariş İptal Edildi\" olması gerekir"),
            _("Lütfen işlemi tamamlayabilmek için siparisleri gerekli duruma getiriniz."),
            _("Satınalma kısmen tamamlandı işlemi gerçekleştiğinde;"),
            _("Siparişe çıkılmayan talep kalemlerinin talep miktarları kullanılabilir miktara aktarılır."),
            _("Bu işlemden sonra muhasebe fişleri bölümünden ödeme emri oluşturabilirsiniz."),

        ]

    class ST11(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Bu işlem tamamlandığında satınalma talebi yapılırken rezerv"
              " edilen talep miktarları kullanılabilir miktara aktarılacaktır."),
            _("Satınalma reddedildikten sonra satınalma ile ilgili başka işlem yapamazsınız.")

        ]

    class ST12(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Satınalmayı iptal edebilmek için siparişlerin durumlarının \"Sipariş İptal Edildi\" olması gerekiyor"),
            _("Satınalmayı iptal etme işlemi tamamlandığında;"),
            _("Siparişe çıkılmayan talep kalemlerinin talep miktarları kullanılabilir miktara aktarılır.")
        ]


class IslemFormlari:
    class STA1(FlaskForm, GenelIslemler):
        ilgili_memur = Select2Field(label=_('İlgili Memur Adı Soyadı'), validators=[
            validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    class STA2(FlaskForm, GenelIslemler):
        talep_kalemleri = FieldList(FormField(TalepKalemi), min_entries=0)

    class STA3(FlaskForm, GenelIslemler):
        pass

    class STA7(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Teslim alınacak siparişi seçiniz")
        ]
        siparisler = FieldList(FormField(SiparisTakip), min_entries=0)

    class STA8(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Muayene komisyonuna gönderilecek kalemleri seçiniz")
        ]
        siparisler = FieldList(FormField(SiparisTakip), min_entries=0)

    class STA9(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Muayene ve kabulu tamamlanacak ürünleri seçiniz")
        ]
        siparisler = FieldList(FormField(SiparisTakip), min_entries=0)

    class STA10(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Muayeneye gönderilip kabul edilmeyen ürünleri seçiniz")
        ]
        siparisler = FieldList(FormField(SiparisTakip), min_entries=0)

    class STA11(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Faturası teslim alınan firmaları seçip fatura bilgilerini giriniz")
        ]
        siparis_faturalari = FieldList(FormField(SiparisFatura), min_entries=0)

    class STA13(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Sipariş iptal edildiğinde;"),
            _("Yürütücü satınalma talebi yaptığında rezerv edilen talep miktarı kullanılabilir miktara aktarılır."),
            _("Firma teklifi kabul edildiğinde rezerv edilen sipariş tutarı kullanılabilir bütçeye aktarılır."),
        ]
        siparisler = FieldList(FormField(SiparisTakip), min_entries=0)

    class STA15(FlaskForm, GenelIslemler):
        uyari_mesajlari = [
            _("Teknik şartnamesini düzenlemesini istediğiniz talep kalemlerini seçiniz")
        ]
        talep_kalemleri = FieldList(FormField(TalepKalemiWithTeknikSartname), min_entries=0)
