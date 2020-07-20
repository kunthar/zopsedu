"""Proje Basvuru Proje Elemanları Formları"""
from uuid import uuid4

from flask_babel import gettext as _
from wtforms import Form, StringField, TextAreaField, BooleanField, FormField, FloatField, \
    DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email
from zopsedu.lib.form.fields import Select2Field, SummerNoteField, MultiFileField


class ProjeCalisani(Form):
    """
        ProjeCalisanlari(bursiyer, arastirmaci, harici_arastirmaci, yurutucu)
        icin gecerli olan ortak fieldlari icerir
    """
    projeye_katkisi = DecimalField(_('Katki (%)'),
                                   default=0,
                                   validators=[
                                       NumberRange(min=0, max=100,
                                                   message=_(
                                                       "Projeye Katkisi Alanı İçin 0-100 Arası Bir Sayı Girmelisiniz."))
                                   ])
    projeye_bilimsel_katkisi = TextAreaField(_('Yapacağı Bilimsel Katkı'))
    projedeki_gorevi = TextAreaField(_('Projedeki Görevi'))

    ozgecmis_text = SummerNoteField(_("Özgeçmiş"), placeholder=_("Özgeçmişinizi Ekleyiniz"))
    banka_bilgisi = StringField(
        _("Banka Hesap Bilgisi(IBAN)"),
        validators=[
            Length(max=32, message=_(
                "Banka Hesap Bilgisi Alanı En Fazla 32 Karakter İçerebilir"))
        ])


class YurutucuForm(ProjeCalisani):
    """
    Arastirma Projesi basvurusu Genel Bilgiler Form Wizard adımının içindeki projenin
    yürütücü bilgilerini içeren panelin form classı
    """
    form_title = _('Proje Yürütücüsü')
    # yurutucu alanlari
    yurutucu_id = Select2Field(_('Yürütücü Seç'),
                               url="/select/ogretim-elemani",
                               placeholder=_("Yürütücü"),
                               disabled=True)
    projeye_katkisi = FloatField(_('Katki (%)'),
                                 default=0,
                                 validators=[
                                     DataRequired(message=_("Katkı Alanı Boş Bırakılamaz")),
                                     NumberRange(min=0, max=100,
                                                 message=_(
                                                     "Projeye Katkisi Alanı İçin 0-100 Arası Bir Sayı Girmelisiniz."))
                                 ])
    ozgecmis_file_id = MultiFileField(_("Özgeçmiş Yükle"),
                                      validators=[Optional()], ids=uuid4().hex)


class ArastirmaciForm(ProjeCalisani):
    """
    Proje personelleri arasına eklenecek araştırmacı paneline karşılık gelen formdur
    """
    form_title = _('Araştırmacı')

    personel_id = Select2Field(_("Personel Seç"),
                               url="/select/personel",
                               placeholder=_("Personel"))

    yonetici_yetkisi_var_mi = BooleanField(
        _('Bu kişi online olarak projeyi ve ara raporları düzenleyebilir/güncelleyebilir'))
    ozgecmis_file_id = MultiFileField(_("Özgeçmiş Yükle"),
                                      validators=[Optional()], ids=uuid4().hex)


# Proje Personeli
class Bursiyer(ProjeCalisani):
    """
    Proje personelleri arasına eklenecek tez öğrencisi paneline karşılık gelen formdur
    """
    form_title = _('Bursiyer')

    ogrenci_id = Select2Field(_("Ögrenci Seç"),
                              url="/select/ogrenci",
                              render_kw={"class": "form-control"},
                              placeholder=_("Öğrenci"))

    yonetici_yetkisi_var_mi = BooleanField(
        _('Bu kişi online olarak projeyi ve ara raporları düzenleyebilir/güncelleyebilir'))
    ozgecmis_file_id = MultiFileField(_("Özgeçmiş Yükle"),
                                      validators=[Optional()], ids=uuid4().hex)


class HariciArastirmaciForm(ProjeCalisani):
    """
    Proje personelleri arasına eklenecek araştırmacı paneline karşılık gelen formdur
    """
    form_title = _('Üniversite Dışı Araştırmacı')

    ad = StringField(_('Adı'), validators=[Length(max=50)], render_kw={"class": "form-control"})
    soyad = StringField(_('Soyadı'), validators=[Length(max=50)], render_kw={"class": "form-control"})
    hitap_unvan_id = Select2Field(_('Unvan Seç'),
                                  url="/select/hitap_unvan",
                                  render_kw={"class": "form-control"},
                                  placeholder=_("Unvan"))

    fakulte_id = Select2Field(_('Fakülte Seç'),
                              url="/select/birim",
                              render_kw={"class": "form-control"},
                              placeholder=_("Fakülte/Enstitü/Yüksek Okul/Merkez"))
    bolum_id = Select2Field(_('Bölüm Seç'), url="/select/birim",
                            render_kw={"class": "form-control"},
                            placeholder=_("Bölüm/Ana Bilim Dalı"))
    eposta = StringField(_('E-posta'), validators=[Length(max=80),
                                                   Email(message=_('Geçersiz e-posta.'))],
                         render_kw={"class": "form-control"})

    is_telefonu = StringField(_('İş Telefonu'), validators=[Length(max=16)], render_kw={"class": "form-control"})

    yonetici_yetkisi_var_mi = BooleanField(
        _('Bu kişi online olarak projeyi ve ara raporları düzenleyebilir/güncelleyebilir'))

    ozgecmis_file_id = MultiFileField(_("Özgeçmiş Yükle"),
                                      validators=[Optional()], ids=uuid4().hex)


class ProjePersoneliFormWizardForm(Form):
    """
    Arastirma Projesi basvurusu Proje Personeli Form Wizard adımı içindeki panelleri barındıran
    form classı
    """
    form_title = _('Proje Ekibi')
    form_description = [_("""Yürütücü ve araştırmacıların katkıları <u>toplam 100
                olacak şekilde</u> projenizde çalışacak personeli buradan ekleyebilir,
                düzenleyebilir ve silebilirsiniz.""")]

    yurutucu = FormField(YurutucuForm)
    arastirmaci = FormField(ArastirmaciForm)
    harici_arastirmaci = FormField(HariciArastirmaciForm)
    bursiyer = FormField(Bursiyer)
