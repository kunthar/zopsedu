"""Proje Turu ile alakalı formlar modülü"""

from flask_wtf import FlaskForm
from sqlalchemy.orm import lazyload
from wtforms import StringField, SelectField, BooleanField, IntegerField, FormField, \
    FieldList
from wtforms import validators
from flask_babel import lazy_gettext as _
from wtforms.validators import DataRequired

from zopsedu.lib.db import DB
from zopsedu.models import Sablon, SablonTipi, GiderSiniflandirma
from zopsedu.bap.proje.forms.proje_turu.personel import ProjeTuruPersonel
from zopsedu.bap.proje.forms.proje_turu.butce import ButceKalemi, ProjeTuruButce
from zopsedu.bap.proje.forms.proje_turu.cikti import Cikti
from zopsedu.bap.proje.forms.proje_turu.ek_dosya import EkDosya
from zopsedu.lib.form.fields import DatePickerField, Select2Field
from zopsedu.lib.form.validators import LessThan
from zopsedu.bap.models.helpers import ProjeTuruKategorisi, ButceTercihleri, \
    ProjeSuresiBirimi
from zopsedu.bap.models.helpers import EkTalepTipi
from zopsedu.lib.form.fields import SummerNoteField

PROJE_TURU_GELIR_KODLARI = [
    "03.6",
    "05.4.1",
    "06.5",
    "03.3",
    "03.5",
    "03.5.9",
    "03.2",
    "03.7",
    "06.1",
    "03.8",
    "06.3",
    "01",
    "03.5.9.03",
    # "630.99",
]


class ProjeTuruFormu(FlaskForm):
    """
    Proje Türü Formu
    """

    information = [
        "Proje türünü taslak olarak kaydedip daha sonra işlem yapmaya devam edebilirsiniz",
        "Başvuru yapılmış bir proje türünü güncelleyemezsiniz.",
        "Başvuru yapılmış bir projeyi güncellemek isterseniz versiyonlama özelliğini kullanabilirsiniz",
        "Bir proje türünü versiyonlarsanız eski versiyona artık başvuru yapılamayacaktır. Başvurular yeni versiyona yapılabilir."
        "Basvuru aktif mi seçeneğini işaretlemezseniz proje türü başvuruya açık olmaz",
    ]
    # Proje türü formu Genel Ayarlar-1 Bölümü
    # pylint: disable=line-too-long
    ad = StringField(_("Proje Tür Adı"),
                     [validators.DataRequired(message=_("Proje Tür Adı Alanı Boş Olamaz"))])

    proje_turu_aciklama = SummerNoteField(_("Proje Türü Açıklaması"))
    kategori = SelectField(_("Kategori"),
                           choices=ProjeTuruKategorisi.choices(),
                           default=ProjeTuruKategorisi.bilimsel_arastirma_projesi,
                           coerce=ProjeTuruKategorisi.coerce)
    gelir_kasasi_id = Select2Field(_('Kasa Seç'),
                                   url="/select/gelir-kasasi",
                                   validators=[
                                       DataRequired(message=_("Kasa alanı boş bırakılamaz"))
                                   ],
                                   placeholder=_("Kasa Seçiniz"))

    basvuru_baslama_tarihi = DatePickerField("Başvuru Başlangıç Tarihi", format='%d.%m.%Y',
                                             validators=[validators.DataRequired(
                                                 message=_("Başvuru Başlama Tarihi Giriniz"))])
    basvuru_bitis_tarihi = DatePickerField("Başvuru Bitiş Tarihi", format='%d.%m.%Y',
                                           validators=[validators.DataRequired(
                                               message=_("Başvuru Bitiş Tarihi Giriniz"))])

    hakem_onerilsin_mi = BooleanField("Hakem Önerilsin mi?",
                                      default=False)
    basvuru_hakem_oneri_sayisi = IntegerField("Hakem Öneri Sayısı", default=0)

    hakem_degerlendirmesi_gerekli_mi = BooleanField("Hakem Değerlendirmesi Gerekli mi?",
                                                    default=False)

    sure_alt_limiti = IntegerField(
        "Proje Süre Alt Limiti",
        validators=[
            validators.DataRequired(
                message=_("Süre alt limiti alanı boş bırakılamaz")),
            LessThan("sure_ust_limiti",
                     message="Proje süre alt limit değeri süre üst limit değerinden küçük olmalıdır")])

    sure_ust_limiti = IntegerField("Proje Süre Üst Limiti",
                                   validators=[validators.DataRequired(
                                       message=_("Süre Üst Limiti Alanı Boş Bırakılamaz"))])
    sure_birimi = SelectField(_("Proje Süre Birimi"),
                              choices=ProjeSuresiBirimi.choices(),
                              default=ProjeSuresiBirimi.ay,
                              coerce=ProjeSuresiBirimi.coerce)

    proje_mali_destek_suresi = IntegerField(_("Proje Mali Destek Süresi"), default=0)
    mali_destek_suresi_birimi = SelectField(_("Mali Destek Süresi Birimi"),
                                            choices=ProjeSuresiBirimi.choices(),
                                            default=ProjeSuresiBirimi.ay,
                                            coerce=ProjeSuresiBirimi.coerce)

    # Proje Türü Formu Genel Ayarlar-2 Bölümü
    # # ek süre ile ilgili alanlar
    ek_sure_talep_tipi = SelectField("Ek Süre Talep Tipi",
                                     choices=EkTalepTipi.choices(),
                                     default=EkTalepTipi.yok,
                                     coerce=EkTalepTipi.coerce)
    ek_sure_talep_degeri = IntegerField(_("Ek Süre Talep Değeri"), default=0)
    ek_sureler_proje_sure_limitine_dahil_mi = BooleanField(
        _("Ek Süre Proje Süre Limitine Dahil mi?"),
        default=False)
    #
    # # Proje tipi yuksek lisans / doktora (uzmanlik) veya belirtilmemis
    # proje_tipi = SelectField("Proje Tipi",
    #                          choices=ProjeTipi.choices(),
    #                          default=ProjeTipi.yuksek_lisans,
    #                          coerce=ProjeTipi.coerce)

    # diger alanlardan bagımsız boolean fieldlar
    basvuru_aktif_mi = BooleanField(_("Başvuru Aktif mi ?"),
                                    default=True)
    proje_ek_talepleri_icin_rapor_kontrolu_yapilacak_mi = BooleanField(
        _("Proje Ek Talepleri İçin Rapor Kontrolü Yapılacak mı ?"),
        default=False)
    herkese_acik_proje_listesinde_yer_alacak_mi = BooleanField(
        _("Herkese Açık Proje Listesinde Yer Alacak mı ?"),
        default=False)

    # butce tercihi
    # todo sabit secenekler elimizde olmadigindan daha sonra eklenmek üzere
    #  secenekler arasından kaldırıldı.
    #     ButceTercihleri.sabit_seceneklerden_birini_secsin.value),
    #  _("Sabit Bütçe Seçeneklerinden Birini Seçsin")),

    butce_tercihi = SelectField(_("Bütçe Tercihleri"),
                                choices=ButceTercihleri.choices(),
                                default=ButceTercihleri.proje_yurutucusu_onersin,
                                coerce=ButceTercihleri.coerce)

    # Proje türü formu ek dosya ayarlari Bölümü
    proje_yurutucusu_ek_dosyalar_ekleyebilir_mi = BooleanField(
        _("Proje Yürütücüsü Ek Dosyalar Ekleyebilir mi ?"),
        default=True)
    is_zaman_plani_otomasyon_icerisinde_doldurulsun_mu = BooleanField(
        _("İş Zamanı Planı Otomasyon İçerisinde Doldurulsun mu ?"),
        default=False)
    ek_dosya_yuklenebilir_mi = BooleanField(_("Ek Dosya Yüklenebilir mi ?"),
                                            default=False)
    # proje türü için gerekli formlar
    oneri_sablon_id = SelectField(_("Öneri Şablonu"),
                                  choices=[],
                                  coerce=int)
    hakem_degerlendirme_sablon_id = SelectField(_("Hakem Proje Değerlendirme Şablonu"),
                                                choices=[],
                                                coerce=int)
    hakem_ara_rapor_sablon_id = SelectField(_("Hakem Ara Rapor Şablonu"),
                                            choices=[],
                                            coerce=int)
    hakem_sonuc_rapor_sablon_id = SelectField(_("Hakem Sonuc Raporu Şablonu"),
                                              choices=[],
                                              coerce=int)
    ara_rapor_sablon_id = SelectField(_("Ara Rapor Şablonu"),
                                      choices=[],
                                      coerce=int)
    sonuc_raporu_sablon_id = SelectField(_("Sonuç Raporu Şablonu"),
                                         choices=[],
                                         coerce=int)
    sozlesme_sablon_id = SelectField(_("Proje Sözleşmesi Şablonu"),
                                     choices=[],
                                     coerce=int)

    # Hangi raporlar gerekli? Sadece sonuc, ara ve sonuc, ikisi de gerekli degil
    ara_rapor_gerekli_mi = BooleanField(_("Ara Rapor Gerekli mi ?"),
                                        default=False)
    sonuc_raporu_gerekli_mi = BooleanField(_("Sonuç Raporu Gerekli mi ?"),
                                           default=False)
    rapor_gecikmelerinde_satinalma_yapabilecek_mi = BooleanField(
        _("Rapor Gecikmelerinde Satınalma Talebi Yapabilecek mi ?"),
        default=False)
    rapor_gecikmelerinde_yolluk_talebi_yapabilecek_mi = BooleanField(
        _("Rapor Gecikmelerinde Yolluk Talebi Yapabilecek mi ?"),
        default=False)
    rapor_gecikmelerinde_ek_talep_yapabilecek_mi = BooleanField(
        _("Rapor Gecikmelerinde Ek Talep Yapabilecek mi ?"),
        default=False)
    sonuc_raporu_sonrasi_islem_yapilsin_mi = BooleanField(
        _("Sonuç Raporundan sonra işlem yapabilir mi ?"),
        default=False)
    rapor_araligi_suresi = IntegerField(_("Rapor Aralığı Süresi"), default=0,
                                        validators=[validators.Optional()])
    rapor_araligi_birimi = SelectField(_("Rapor Aralığı Birimi"),
                                       choices=ProjeSuresiBirimi.choices(),
                                       default=ProjeSuresiBirimi.ay,
                                       coerce=ProjeSuresiBirimi.coerce)
    sonuc_raporu_icin_ek_sure = IntegerField(_("Sonuç Raporu İçin Ek Süre"), default=0,
                                             validators=[validators.Optional()])
    sonuc_raporu_icin_ek_sure_birimi = SelectField(_("Sonuç Raporu İçin Ek Süre Birimi"),
                                                   choices=ProjeSuresiBirimi.choices(),
                                                   default=ProjeSuresiBirimi.ay,
                                                   coerce=ProjeSuresiBirimi.coerce)

    rapor_gecikme_mail_suresi = IntegerField(_("Rapor Gecikme Mail Süresi"), default=0,
                                             validators=[validators.Optional()])
    rapor_gecikme_mail_suresi_birimi = SelectField(_("Rapor Gecikme Mail Süresi Birimi"),
                                                   choices=ProjeSuresiBirimi.choices(),
                                                   default=ProjeSuresiBirimi.ay,
                                                   coerce=ProjeSuresiBirimi.coerce)

    personel_ekrani_bilgilendirme_mesaji = SummerNoteField(
        _("Personel Ekranı Bilgilendirme Mesajı"))
    proje_yurutucusu_icin_yardim_mesaji = SummerNoteField(_("Proje Yürütücüsü İçin Yardım Mesajı"))
    basvuru_yapilmadan_gelecek_uyari = SummerNoteField(_("Basvuru Yapilmadan Gelecek Uyari Mesajı"))
    basvuru_tamamlandiktan_sonra_bilgilendirme = SummerNoteField(
        _("Başvuru Tamamlandıktan Sonra Bilgilendirme Mesajı"))
    gonder_islemi_yapilirken_yurutucuye_gosterilecek_uyari = SummerNoteField(
        _("Gönder İşlemi Yapılırken Yurutucuye Gösterilecek Uyarı Mesajı"))
    ek_dosyalar_ekrani_bilgilendirme = SummerNoteField(_("Ek Dosyalar Ekranı Bilgilendirme Mesajı"))
    hakem_onerisi_bilgilendirme = SummerNoteField(_("Hakem Önerisi Bilgilendirme Mesajı"))
    ara_rapor_uyari = SummerNoteField(_("Ara Rapor İçin Uyarı Mesajı"))
    sonuc_raporu_uyari = SummerNoteField(_("Sonuc Raporu İçin Uyarı Mesajı"))
    butce_ekrani_bilgilendirme = SummerNoteField(_("Bütçe Ekranı Bilgilendirme Mesajı"))
    yurutucu_proje_sozlesme_bekleme_mesaji = SummerNoteField(
        _("Yürütücü Proje Sözleşme Bekleme Mesajı"))
    degerlendirme_ekraninda_bilgi_notu = SummerNoteField(_("Değerlendirme ekranında bilgi notu"))
    degerlendirme_sonunda_bilgi_notu = SummerNoteField(_("Değerlendirme sonunda bilgi notu"))

    # Proje türü formu personel ayarlari bölümü
    personel_ayarlari = FormField(ProjeTuruPersonel)
    # Proje türü butce sablon ayarlari bölümü
    butce_ayarlari = FormField(ProjeTuruButce)
    butce_kalemleri = FieldList(FormField(ButceKalemi))

    ek_dosyalar = FieldList(FormField(EkDosya), min_entries=1)
    ciktilar = FieldList(FormField(Cikti), min_entries=1)
    cikti_secenekleri = SelectField(_("Çıktı Seçenekleri"),
                                    choices=[],
                                    coerce=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sablon_types = {
            4: [],  # oneri sablon type id
            5: [],  # Hakem proje degerlendirme sablon type id
            8: [],  # hakem souc raporu degerlendirme sablon type id
            9: [],  # Hakem Ara Raporu Değerlendirme Şablonu
            14: [],  # Sonuç Raporu Şablonu sablon type id
            15: [],  # Ara Rapor Şablonu  sablon type id
            3: [],  # sözlesme sablon type id
        }

        proje_turu_sablonlari = DB.session.query(
            Sablon.id.label("sablon_id"),
            Sablon.adi.label("sablon_adi"),
            SablonTipi.id.label("sablon_tipi_id"),
            SablonTipi.adi.label("sablon_tipi_adi")
        ).join(Sablon.sablon_tipi).filter(Sablon.module_name == "BAP",
                                          Sablon.kullanilabilir_mi == True,
                                          SablonTipi.id.in_(sablon_types.keys())).all()

        for sablon in proje_turu_sablonlari:
            sablon_types[sablon.sablon_tipi_id].append(
                (sablon.sablon_id, sablon.sablon_adi))

        self.set_field_choices(self.oneri_sablon_id, sablon_types[4])

        self.set_field_choices(self.hakem_degerlendirme_sablon_id,
                               sablon_types[5])

        self.set_field_choices(self.hakem_ara_rapor_sablon_id,
                               sablon_types[9])

        self.set_field_choices(self.hakem_sonuc_rapor_sablon_id,
                               sablon_types[8])

        self.set_field_choices(self.sonuc_raporu_sablon_id, sablon_types[14])

        self.set_field_choices(self.ara_rapor_sablon_id, sablon_types[15])

        self.set_field_choices(self.sozlesme_sablon_id, sablon_types[3])

        bap_sablon_tipleri = DB.session.query(Sablon).options(lazyload(Sablon.query)).filter(
            Sablon.module_name == "BAP").filter(~Sablon.sablon_tipi_id.in_(sablon_types.keys())).all()
        if bap_sablon_tipleri:
            sablon_secenekleri = []
            for sablon in bap_sablon_tipleri:
                sablon_secenekleri.append((sablon.id, "{sablon_adi} ({sablon_tipi})".format(
                    sablon_tipi=sablon.sablon_tipi.adi, sablon_adi=sablon.adi)))

            self.cikti_secenekleri.choices = sablon_secenekleri
            self.cikti_secenekleri.default = sablon_secenekleri[0]
            self.cikti_secenekleri.coerce = int

        # proje turu basvurusunda gorunecek analitik gelir kodlarini db den alip proje turu
        # formu butce_kalemleri icerisine ekler
        if not self.butce_kalemleri.entries:
            analitik_butce_kodlari = DB.session.query(GiderSiniflandirma).filter(
                GiderSiniflandirma.kodu.in_(PROJE_TURU_GELIR_KODLARI)).all()
            for butce_kodu in analitik_butce_kodlari:
                self.butce_kalemleri.append_entry(
                    {"gider_siniflandirma_id": butce_kodu.id,
                     "secili_mi": False,
                     "butce_kalemi_adi": "{} {}".format(butce_kodu.kodu,
                                                        butce_kodu.aciklama)
                     })

    @staticmethod
    def set_field_choices(field, choices):
        """

        :param field: form field
        :param choices: tuple list of choices
        :return:
        """
        if choices:
            setattr(field, "choices", choices)
            setattr(field, "default", getattr(field, "choices")[0])
