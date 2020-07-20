"""Satinalma dashboard muhasebe fisleri bolumu formlari"""
from datetime import date
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import StringField, Form, FieldList, FormField, IntegerField, SelectField, \
    TextAreaField
from wtforms.meta import DefaultMeta
from wtforms.validators import DataRequired, Length

from zopsedu.lib.form.fields import Select2Field, DatePickerField, ZopseduDecimalField
from zopsedu.lib.form.validators import DecimalLength


class MuhasebeFisiListelemeInformation(FlaskForm):
    """
    Muhasebe Fisi lisleteme ekrani information
    """

    uyari_mesajlari = [
        _("Satınalma \"Satınalma işlemleri tamamlandı\" veya \"Satınalma"
          " kısmen tamamlandı\" durumuna gelmeden muhasebe fişi oluşturamazsınız"),
        _("Muhasebe fiş alanlarının otomasyon tarafından doldurulabilmesi için bütçe kısmındaki "
          "bütçe kodlarını doldurmanız gerekir.")
    ]


class MuhasebeFisMaddesi(Form):
    class Meta(DefaultMeta):
        locales = ["tr"]

    # todo: select2
    hesap_kodu = Select2Field(_("Hesap Kodu"),
                              url="/select/detayli-hesap-kodu",
                              placeholder=_("Detaylı Hesap Kodu"),
                              validators=[
                                  DataRequired(_("Bu alan boş bırakılamaz")),
                              ])
    kurumsal_kod = StringField(_("Kurumsal Kod"),
                               render_kw={"class": "form-control"},
                               validators=[
                                   DataRequired(_("Bu alan boş bırakılamaz")), Length(max=20),
                               ])
    fonksiyonel_kod = SelectField(_("Fonksiyonel Kodlar"),
                                  render_kw={"class": "form-control"},
                                  validators=[
                                      DataRequired(_("Bu alan boş bırakılamaz")),
                                  ])
    finans_kodu = StringField(_("Finans Kodu"),
                              render_kw={"class": "form-control"},
                              validators=[
                                  DataRequired(_("Bu alan boş bırakılamaz")),
                              ], default=2)
    borc = ZopseduDecimalField(_('Borç(TL)'),
                               validators=[
                                   DecimalLength(max_length=12,
                                                 error_message="Borç için en fazla 12 "
                                                               "haneli bir değer girebilirsiniz")])
    alacak = ZopseduDecimalField(
        _('Alacak(TL)'),
        validators=[
            DecimalLength(max_length=12,
                          error_message="Alacak için en fazla 12 "
                                        "haneli bir değer girebilirsiniz")])


class OdemeYapilacakKisiBilgileri(Form):
    adi_soyadi = StringField(_("Adı Soyadı"),
                             validators=[
                                 DataRequired(_("Bu alan boş bırakılamaz")), Length(max=50),
                             ])
    banka_sube = StringField(_("Banka/şube"),
                             validators=[
                                 DataRequired(_("Bu alan boş bırakılamaz")), Length(max=50),
                             ])
    vergi_no = StringField(_("Vergi No"),
                           validators=[
                               DataRequired(_("Bu alan boş bırakılamaz")), Length(max=50),
                           ])
    hesap_no = StringField(_("IBAN"),
                           validators=[
                               DataRequired(_("Bu alan boş bırakılamaz")),Length(max=40),
                           ])
    vergi_dairesi_id = Select2Field(_('Vergi Dairesi'),
                                    url="/select/vergi-dairesi",
                                    placeholder=_("Vergi Dairesi Adı"),
                                    validators=[
                                        DataRequired(_("Bu alan boş bırakılamaz")),
                                    ])


# {"kurum_adi": "zopsedu kurumu", "kurum_kodu": "39.00.00", "birim_adi": "zopsedu birim",
#  "birim_kodu": "901", "muhasebe_birimi_adi": "zopsedu muhasebe birim ad\u0131",
#  "muhasebe_birimi_kodu": "123123",
#  "kurum_banka_bilgisi": {"hesap_adi": "", "iban": "", "banka_adi": "", "banka_subesi": "",
#                          "vergi_no": "", "vergi_dairesi_id": null, "csrf_token": ""},
#  "kdv_kodlari": {"kdv_tevkifat_kodu": "", "kdv_tevkifat_adi": "", "kdv_tevkifat_orani": "",
#                  "csrf_token": ""}}


class FisGenelBilgiler(Form):
    kurum_adi = StringField(_("Kurum Adı"),
                            validators=[
                                DataRequired(_("Bu alan boş bırakılamaz")),
                            ])
    kurum_kodu = StringField(_("Kurum Kodu"),
                             validators=[
                                 DataRequired(_("Bu alan boş bırakılamaz")),
                             ])
    muhasebe_birimi_adi = StringField(_("Muhasebe Birim Adı"),
                                      validators=[
                                          DataRequired(_("Bu alan boş bırakılamaz")),
                                      ])
    muhasebe_birimi_kodu = StringField(_("Muhasebe Kodu"),
                                       validators=[
                                           DataRequired(_("Bu alan boş bırakılamaz")),
                                       ])
    birim_adi = StringField(_("Birim Adı"),
                            validators=[
                                DataRequired(_("Bu alan boş bırakılamaz")),
                            ])
    birim_kodu = StringField(_("Birim Kodu"),
                             validators=[
                                 DataRequired(_("Bu alan boş bırakılamaz")),
                             ])
    fakulte_bolum = StringField(_("Fakülte/Bölüm"),
                                validators=[
                                    DataRequired(_("Bu alan boş bırakılamaz")),
                                ])
    yil = IntegerField(_("Yıl"), default=date.today().year,
                       validators=[
                           DataRequired(_("Bu alan boş bırakılamaz")),
                       ])
    belge_tarihi = DatePickerField(_("Belge Tarihi"),
                                   validators=[DataRequired(
                                       message=_("Bu Alan Boş Bırakılamaz"))],
                                   disable_older_dates=False,
                                   disable_further_dates=True)
    belge_numarasi = StringField(_("Belge Numarası"),
                                 validators=[DataRequired(_("Bu alan boş bırakılamaz"))])


class FaturaBilgileri(Form):
    fatura_no = StringField(_("Fatura No."),
                            validators=[
                                DataRequired(_("Bu alan boş bırakılamaz")),
                            ])
    fatura_tarihi = DatePickerField(_("Fatura Tarihi"),
                                    validators=[DataRequired(
                                        message=_("Bu Alan Boş Bırakılamaz"))],
                                    disable_older_dates=False,
                                    disable_further_dates=True)
    aciklama = TextAreaField(_("Açıklama"),
                             validators=[
                                 DataRequired(_("Bu alan boş bırakılamaz")),
                             ])


class MuhasebeFisiForm(FlaskForm):
    uyari_mesajlari = [
        _("Gerekli alanların otomasyon tarafından doldurulması için bütçe ayarları kısmından ilgili"
          " kodları kaydettiğinizden emin olun."),
        _("Muhasebe fişi oluşturulduğunda proje bütçesinden rezerv edilen tutar kullanılan bütçeye"
          " aktarılacaktır.")
    ]

    fis_genel_bilgileri = FormField(FisGenelBilgiler)
    odeme_yapilacak_kisi_bilgileri = FormField(OdemeYapilacakKisiBilgileri)
    fis_maddeleri = FieldList(FormField(MuhasebeFisMaddesi), min_entries=4)
    fatura_bilgileri = FormField(FaturaBilgileri)
