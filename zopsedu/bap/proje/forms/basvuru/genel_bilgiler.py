"""Proje Basvuru Genel Bilgiler Formlari"""

from flask_babel import gettext as _
from wtforms import Form, SelectField, IntegerField, StringField, TextAreaField, FormField
from zopsedu.lib.form.fields import SummerNoteField
from wtforms.validators import DataRequired, Length, Email
from zopsedu.lib.form.fields import DatePickerField, Select2Field
from zopsedu.bap.models.helpers import ProjeSuresiBirimi
from zopsedu.models.helpers import BirimTipiEnum


class GenelBilgilerForm(Form):
    """
    Arastirma projesi basvurusu Genel Bilgiler Form Wizard adımının içindeki Genel Bilgiler
    panelinin form classı.
    """
    form_title = _('Genel Bilgiler (*)')
    proje_turu_read_only = SelectField(_('Proje Türü'), choices=[('2', 'Araştırma Projesi')],
                                       default="2")

    proje_disiplinler_arasi_mi = SelectField(
        _('Proje Disiplinler Arası mı?'),
        choices=[(1, _('Evet')), (0, _('Hayır'))],
        default=0,
        coerce=int
    )
    proje_suresi = IntegerField(_('Proje Süresi'), validators=[DataRequired(
        message=_("Proje Süresi Alanı Boş Bırakılamaz"))], default=0)
    proje_suresi_birimi = SelectField(choices=ProjeSuresiBirimi.choices(),
                                      default=ProjeSuresiBirimi.ay,
                                      coerce=ProjeSuresiBirimi.coerce)
    etik_kurul_izin_belgesi = SelectField(
        _('Etik Kurulu İzin Belgesi'),
        choices=[(1, _('Gerekli')), (0, _('Gerekli değil'))],
        default=0,
        coerce=int
    )
    proje_basligi = StringField(_('Proje Başlığı'), validators=[Length(max=250),
                                                                DataRequired(
                                                                    message=_("Proje Başlığı Alanı Boş Bırakılamaz"))])
    project_title = StringField(_('Project Title Optional'), validators=[Length(max=250)])
    anahtar_kelimeler = TextAreaField(_('Anahtar Kelimeler'), validators=[Length(max=255)],
                                      description='Kelimeler arasında virgül kullanınız.')


class FakulteForm(Form):
    """
    Arastirma Projesi basvurusu Genel Bilgiler Form Wizard adımının içindeki projenin
    yürütüleceği fakülte/bölüm/bilim dalı bilgilerinin bulunduğu panelin form classı
    """
    form_title = _('Projenin Yürütüleceği Faküllte/Bölüm/Ana Bilim Dalı Bilgileri (*)')

    proje_fakulte = Select2Field(_('Fakülte Seç'),
                                 url="/select/birim",
                                 validators=[
                                     DataRequired(message=_("Fakülte Alanı Boş Bırakılamaz"))
                                 ],
                                 placeholder=_("Fakülte"),
                                 node_name="proje_bolum_parent",
                                 birim_tipi=BirimTipiEnum.fakulte.value,
                                 kurum_ici=True)

    proje_bolum = Select2Field(_('Bölüm Seç'), url="/select/birim",
                               validators=[DataRequired(message=_("Bölüm Alanı Boş Bırakılamaz"))],
                               placeholder=_("Bölüm"),
                               dependent="proje_bolum_parent",
                               node_name="proje_anabilim_dali_parent",
                               birim_tipi=BirimTipiEnum.bolum.value,
                               kurum_ici=True)

    proje_ana_bilim_dali = Select2Field(_('Ana Bilim Dalı Seç'),
                                        url="/select/birim",
                                        validators=[
                                            DataRequired(
                                                message=_("Ana Bilim Dalı Alanı Boş Bırakılamaz"))
                                        ],
                                        placeholder=_("Anabilim Dalı"),
                                        dependent="proje_anabilim_dali_parent",
                                        node_name="proje_bilim_dali_parent",
                                        birim_tipi=BirimTipiEnum.ana_bilim_dali.value,
                                        kurum_ici=True)

    # proje_bilim_dali = Select2Field(_('Proje Bilim Dali Seç'),
    #                                 url="/select/birim",
    #                                 placeholder=_("Proje Bilim Dali"),
    #                                 dependent="proje_bilim_dali_parent",
    #                                 kurum_ici=True)


class OnaylayanYetkiliForm(Form):
    """
    Arastirma Projesi basvurusu Genel Bilgiler Form Wizard adımının içindeki projenin onaylayan
    yetkili bilgilerini içeren panelin form classı
    """
    form_title = _('Onaylayan Yetkili')
    # onaylayan yetkili
    onaylayan_yetkili_id = Select2Field(_('Onaylayan Yetkili Seç'),
                                        url="/select/personel",
                                        validators=[
                                            DataRequired(message=_(
                                                "Onaylayan Yetkili Alanı Boş Bırakılamaz"))
                                        ],
                                        placeholder=_("Onaylayan Yetkili"))
    onay_tarihi = DatePickerField(_('Onay Tarihi'), format='%d.%m.%Y',
                                  validators=[
                                      DataRequired(message=_("Onay Tarihi Alanı Boş Bırakılamaz"))
                                  ], disable_older_dates=False, disable_further_dates=True)


class ProjeOzetBilgileri(Form):
    form_title = _('Genel Bilgiler 2')
    ozet = SummerNoteField(
        _("Proje Özeti"))
    literatur_ozet = SummerNoteField(_("Literatür Özeti"))
    amac_kapsam = SummerNoteField(_("Amaç, Konu ve Kapsam"))
    gerec_yontem = SummerNoteField(
        _("Materyal ve Yöntem"))
    arastirma_olanaklari = SummerNoteField(
        _("Araştırma Olanakları"))
    beklenen_bilimsel_katki = SummerNoteField(_("Yaygın Etki"))
    uygulama_plani = SummerNoteField(_("Çalışma Takvimi"))


class DestekleyenKurulusForm(Form):
    """
    Arastirma Projesi basvurusu Genel Bilgiler Form Wizard adımının içindeki projenin destekleyen
    kuruluş bilgilerini içeren panelin form classı

    """
    form_title = _('Destekleyen Kuruluş')
    # destekleyen kurulus
    adi = StringField(_('Adı'), validators=[Length(max=100)])
    telefon = StringField(_('Telefon'), validators=[Length(max=25)])
    yetkili_ad_soyad = StringField(_('Destekleyen Kuruluş Yetkilisi Adı Soyadı'), validators=[Length(max=100)])
    adres = StringField(_('Adres'), validators=[Length(max=300)])
    eposta = StringField(_('E-posta'),
                         validators=[Length(max=100),
                                     Email(message=_('Geçersiz e-posta.'))])
    yetkili_gorev = StringField(_('Destekleyen Kuruluş Yetkilisi Görevi'), validators=[Length(max=100)])


# Form Wizard Adımları
class GenelBilgilerFormWizardForm(Form):
    """
    Arastirma Projesi basvurusu Genel Bilgiler Form Wizard adımı içindeki panelleri barındıran
    form classı
    """
    genel_bilgiler = FormField(GenelBilgilerForm)
    ozet_bilgiler = FormField(ProjeOzetBilgileri)
    fakulte = FormField(FakulteForm)
    onaylayan_yetkili = FormField(OnaylayanYetkiliForm)
    destekleyen_kurulus = FormField(DestekleyenKurulusForm)
