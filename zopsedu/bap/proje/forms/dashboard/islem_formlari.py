from datetime import datetime

from flask import request, current_app
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import joinedload
from wtforms import validators, BooleanField, Form, IntegerField, SelectField, StringField, \
    FormField, FieldList
from wtforms.meta import DefaultMeta
from wtforms.validators import DataRequired, ValidationError, Optional

from zopsedu.bap.models.helpers import ProjeSuresiBirimi, ProjeDegerlendirmeSonuc, GundemTipi, \
    KararDurumu
from zopsedu.bap.models.proje_detay import ProjeDegerlendirmeleri, ProjeHakemDavetDurumlari
from zopsedu.bap.models.proje_rapor import ProjeRaporDurumu, ProjeRaporTipi
from zopsedu.bap.models.toplanti import GundemSablon, BapToplanti
from zopsedu.lib.form.validators import DecimalLength
from zopsedu.models import ProjeRapor, ProjeHakemleri, Personel
from zopsedu.lib.db import DB
from zopsedu.lib.form.fields import SummerNoteField, DatePickerField, MultiFileField, \
    HiddenIntegerField, HiddenStringField, ZopseduDecimalField
from zopsedu.personel.models.hakem import Hakem


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
        label=_('Proje yürütücüsü e-mail yolu ile bilgilendirilsin.'),
    )


class ProjeKalemiFormu(Form):
    class Meta(DefaultMeta):
        locales = ["tr"]

    proje_kalemi_id = HiddenIntegerField(_("PKI"))
    proje_kalemi_adi = HiddenStringField(_("Proje Kalemi"))

    teklif_edilen_miktar = HiddenIntegerField(_("TM"))
    onerilen_yil_1 = HiddenStringField(_("OY1"))
    onerilen_yil_2 = HiddenStringField(_("OY2"))
    onerilen_yil_3 = HiddenStringField(_("OY3"))

    kabul_edilen_miktar = IntegerField(_("Kabul Edilen Miktar"))
    kabul_edilen_yil_1 = ZopseduDecimalField(_('Kabul Edilen 1. Yıl'),
                                             validators=[
                                                 DecimalLength(max_length=10,
                                                               error_message="Bütçe 1. yıl için en fazla 10 "
                                                                             "haneli bir değer girebilirsiniz")
                                             ])
    kabul_edilen_yil_2 = ZopseduDecimalField(_('Kabul Edilen 2. Yıl'),
                                             validators=[
                                                 DecimalLength(max_length=10,
                                                               error_message="Bütçe 2. yıl için en fazla 10 "
                                                                             "haneli bir değer girebilirsiniz")
                                             ])
    kabul_edilen_yil_3 = ZopseduDecimalField(_('Kabul Edilen 3. Yıl'),
                                             validators=[
                                                 DecimalLength(max_length=10,
                                                               error_message="Bütçe 3. yıl için en fazla 10 "
                                                                             "haneli bir değer girebilirsiniz")
                                             ])


class IslemFormlari:
    class PA1(FlaskForm, GenelIslemler):
        islem_adi = StringField(
            label=_('İşlem adını yazınız'),
            validators=[DataRequired(message=_("İşlem Adı Boş Bırakılamaz"))])

    class PA2(FlaskForm, GenelIslemler):
        ozel_not = SummerNoteField(
            label=_('Projeye Özel Not Giriniz'),
            validators=[
                validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            ])

    class PA3(FlaskForm, GenelIslemler):
        ozel_not = SummerNoteField(
            label=_('Proje Yürütücüsüne Özel Not Giriniz'),
            validators=[
                validators.DataRequired(message=_('Bu alan boş bırakılamaz')),
            ])

    class PA12(FlaskForm, GenelIslemler):

        toplanti_tarihi = SelectField(label=_("Toplantı tarihi seçiniz"),
                                      validators=[
                                          validators.DataRequired(
                                              message=_('Bu alan boş bırakılamaz')),
                                      ],
                                      coerce=int)

        gundem_tipi = SelectField(label=_("Gündem Tipi"),
                                  choices=GundemTipi.choices(),
                                  coerce=GundemTipi.coerce)

        karar_durum = SelectField(label=_("Karar Durumu"),
                                  validators=[
                                      validators.DataRequired(message=_('Bu alan boş bırakılamaz')),
                                  ],
                                  choices=KararDurumu.choices(),
                                  coerce=KararDurumu.coerce)

        karar_sira_no = IntegerField(label=_("Karar Sıra No"),
                                     validators=[validators.DataRequired(
                                         message=_('Bu alan boş bırakılamaz'))])

        karar = SummerNoteField(
            label=_('Karar'),
            validators=[
                validators.DataRequired(message=_('Bu alan boş bırakılamaz.')),
            ])

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            toplantilar = DB.session.query(BapToplanti).all()

            toplanti_list = [(0, _("Lütfen kararın alındığı toplantıyı seçiniz"))]

            for toplanti in toplantilar:
                toplanti_list.append((toplanti.id,
                                      "Toplanti Tarihi: {}".format(
                                          toplanti.toplanti_tarihi.strftime('%d.%m.%Y'))))

            self.toplanti_tarihi.choices = toplanti_list
            self.toplanti_tarihi.default = 0

    class PA13(FlaskForm, GenelIslemler):
        klasor_sira_no = IntegerField(
            label=_('Klasör Sıra Numarası Giriniz'),
            validators=[DataRequired(message=_("Bu alan boş bırakılamaz"))])

    class PA6(FlaskForm, GenelIslemler):
        hakemler = SelectField(_("Hakem Seçiniz"), coerce=int)
        butun_hakemlere_gonderilsin_mi = BooleanField(_("Bütün Hakemlere Gönderilsin Mi ?"),
                                                      default=False)

        def validate_raporlar(self, _):
            if not self.raporlar.data:
                raise ValidationError(message="Lütfen rapor seçiniz")

        def validate_hakemler(self, _):
            if not self.hakemler.data and not self.butun_hakemlere_gonderilsin_mi.data:
                raise ValidationError(message="Lütfen hakem seçiniz")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            proje_hakemleri = DB.session.query(ProjeHakemleri).options(
                joinedload(ProjeHakemleri.hakem).joinedload("*")
            ).filter(ProjeHakemleri.proje_id == proje_id,
                     ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi).all()
            proje_hakemleri_list = [(0, _("Lütfen Hakem Seçiniz"))]
            for proje_hakemi in proje_hakemleri:
                if proje_hakemi.hakem.personel_id:
                    proje_hakemleri_list.append((proje_hakemi.id,
                                                 proje_hakemi.hakem.personel.person.ad + " " + proje_hakemi.hakem.personel.person.soyad))
                else:
                    proje_hakemleri_list.append((proje_hakemi.id,
                                                 proje_hakemi.hakem.person.ad + " " + proje_hakemi.hakem.person.soyad))
            self.hakemler.choices = proje_hakemleri_list
            self.hakemler.default = 0

    class PA7(FlaskForm, GenelIslemler):
        raporlar = SelectField(_("Rapor Seçiniz"), coerce=int)
        hakemler = SelectField(_("Hakem Seçiniz"), coerce=int)
        butun_hakemlere_gonderilsin_mi = BooleanField(_("Bütün Hakemlere Gönderilsin Mi ?"),
                                                      default=False)

        def validate_raporlar(self, _):
            if not self.raporlar.data:
                raise ValidationError(message="Lütfen rapor seçiniz")

        def validate_hakemler(self, _):
            if not self.hakemler.data and not self.butun_hakemlere_gonderilsin_mi.data:
                raise ValidationError(message="Lütfen hakem seçiniz")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            proje_raporlari = DB.session.query(ProjeRapor).filter(ProjeRapor.proje_id == proje_id,
                                                                  ProjeRapor.durumu == ProjeRaporDurumu.tamamlandi,
                                                                  or_(
                                                                      ProjeRapor.rapor_tipi == ProjeRaporTipi.sonuc_raporu,
                                                                      ProjeRapor.rapor_tipi == ProjeRaporTipi.ara_rapor)).all()
            proje_hakemleri = DB.session.query(ProjeHakemleri).options(
                joinedload(ProjeHakemleri.hakem).joinedload("*")
            ).filter(ProjeHakemleri.proje_id == proje_id,
                     ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi).all()
            proje_hakemleri_list = [(0, _("Lütfen Hakem Seçiniz"))]
            for proje_hakemi in proje_hakemleri:
                if proje_hakemi.hakem.personel_id:
                    proje_hakemleri_list.append((proje_hakemi.id,
                                                 proje_hakemi.hakem.personel.person.ad + " " + proje_hakemi.hakem.personel.person.soyad))
                else:
                    proje_hakemleri_list.append((proje_hakemi.id,
                                                 proje_hakemi.hakem.person.ad + " " + proje_hakemi.hakem.person.soyad))
            self.hakemler.choices = proje_hakemleri_list
            self.hakemler.default = 0

            proje_raporlari_list = [(0, _("Lütfen Rapor Seçiniz"))]
            for proje_rapor in proje_raporlari:
                proje_raporlari_list.append(
                    (proje_rapor.id, "{} - {} - {}".format(proje_rapor.rapor_tipi.value,
                                                           proje_rapor.created_at.strftime(
                                                               "%d-%m-%Y"),
                                                           proje_rapor.rapor_degerlendirme_durumu.value
                                                           ))
                )

            self.raporlar.choices = proje_raporlari_list
            self.raporlar.default = 0

    class PA10(FlaskForm, GenelIslemler):
        degerlendirmeler = SelectField(_("Değerlendirme Seçiniz"), coerce=int)

        def validate_degerlendirmeler(self, _):
            if not self.degerlendirmeler.data:
                raise ValidationError(message="Lütfen değerlendirme seçiniz")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            proje_degerlendirmeleri = DB.session.query(ProjeDegerlendirmeleri).options(
                joinedload(ProjeDegerlendirmeleri.rapor),
                joinedload(
                    ProjeDegerlendirmeleri.degerlendirme_hakemi
                ).load_only("id", "hakem_id").joinedload(
                    ProjeHakemleri.hakem).load_only("id", "person_id", "personel_id").joinedload(
                    Hakem.person).load_only("ad", "soyad"),
                joinedload(
                    ProjeDegerlendirmeleri.degerlendirme_hakemi
                ).load_only("id", "hakem_id").joinedload(
                    ProjeHakemleri.hakem).load_only("id", "person_id", "personel_id").joinedload(
                    Hakem.personel).load_only("id", "person_id").joinedload(
                    Personel.person).load_only("ad",
                                               "soyad"),
            ).filter(
                and_(and_(ProjeRapor.proje_id == proje_id,
                          and_(
                              ProjeDegerlendirmeleri.degerlendirme_sonuclandi_mi == True,
                              ProjeDegerlendirmeleri.degerlendirme_incelendi_mi == False)
                          ), ProjeRapor.rapor_tipi == ProjeRaporTipi.proje_basvuru
                     )
            ).all()

            degerlendirmeler_list = [(0, _("Lütfen değerlendirme seçiniz"))]
            for degerlendirme in proje_degerlendirmeleri:
                if degerlendirme.degerlendirme_hakemi.hakem.person:
                    hakem_ad_soyad = "{} {}".format(
                        degerlendirme.degerlendirme_hakemi.hakem.person.ad,
                        degerlendirme.degerlendirme_hakemi.hakem.person.soyad)
                else:
                    hakem_ad_soyad = "{} {}".format(
                        degerlendirme.degerlendirme_hakemi.hakem.personel.person.ad,
                        degerlendirme.degerlendirme_hakemi.hakem.personel.person.soyad)
                degerlendirmeler_list.append((degerlendirme.id,
                                              "{} - {} - {}".format(
                                                  hakem_ad_soyad,
                                                  degerlendirme.rapor.rapor_tipi.value,
                                                  degerlendirme.degerlendirme_gonderim_tarihi.strftime(
                                                      current_app.config[
                                                          'DATE_FORMAT']))))

            self.degerlendirmeler.choices = degerlendirmeler_list
            self.degerlendirmeler.default = 0

    class PA11(FlaskForm, GenelIslemler):
        degerlendirmeler = SelectField(_("Değerlendirme Seçiniz"), coerce=int)

        def validate_raporlar(self, _):
            if not self.degerlendirmeler.data:
                raise ValidationError(message="Lütfen değerlendirme seçiniz")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            proje_degerlendirmeleri = DB.session.query(ProjeDegerlendirmeleri).options(
                joinedload(ProjeDegerlendirmeleri.rapor),
                joinedload(
                    ProjeDegerlendirmeleri.degerlendirme_hakemi
                ).load_only("id", "hakem_id").joinedload(
                    ProjeHakemleri.hakem).load_only("id", "person_id", "personel_id").joinedload(
                    Hakem.person).load_only("ad", "soyad"),
                joinedload(
                    ProjeDegerlendirmeleri.degerlendirme_hakemi
                ).load_only("id", "hakem_id").joinedload(
                    ProjeHakemleri.hakem).load_only("id", "person_id", "personel_id").joinedload(
                    Hakem.personel).load_only("id", "person_id").joinedload(
                    Personel.person).load_only("ad",
                                               "soyad"),
            ).filter(
                and_(and_(ProjeRapor.proje_id == proje_id,
                          and_(
                              ProjeDegerlendirmeleri.degerlendirme_sonuclandi_mi == True,
                              ProjeDegerlendirmeleri.degerlendirme_incelendi_mi == False)
                          ), or_(ProjeRapor.rapor_tipi == ProjeRaporTipi.ara_rapor,
                                 ProjeRapor.rapor_tipi == ProjeRaporTipi.sonuc_raporu)
                     )
            ).all()

            degerlendirmeler_list = [(0, _("Lütfen değerlendirme seçiniz"))]

            for degerlendirme in proje_degerlendirmeleri:
                if degerlendirme.degerlendirme_hakemi.hakem.person:
                    hakem_ad_soyad = "{} {}".format(
                        degerlendirme.degerlendirme_hakemi.hakem.person.ad,
                        degerlendirme.degerlendirme_hakemi.hakem.person.soyad)
                else:
                    hakem_ad_soyad = "{} {}".format(
                        degerlendirme.degerlendirme_hakemi.hakem.personel.person.ad,
                        degerlendirme.degerlendirme_hakemi.hakem.personel.person.soyad)
                degerlendirmeler_list.append(
                    (degerlendirme.id,
                     "{} - {} - {}".format(
                         hakem_ad_soyad,
                         degerlendirme.rapor.rapor_tipi.value,
                         degerlendirme.degerlendirme_gonderim_tarihi.strftime(
                             current_app.config[
                                 'DATE_FORMAT'])))
                )

            self.degerlendirmeler.choices = degerlendirmeler_list
            self.degerlendirmeler.default = 0

    class PA14(FlaskForm, GenelIslemler):
        proje_basligi = StringField(
            label=_('Yeni projenin başlağını yazınız'),
            validators=[DataRequired(message=_("Proje Başlığı Alanı Boş Bırakılamaz"))])

        project_title = StringField(
            label=_('Yeni projenin ingilizce başlağını yazınız (New Project Title)'),
        )

        proje_no = StringField(
            label=_('Yeni projenin numarasını yazınız'),
            validators=[validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))],
        )

    class PA16(FlaskForm, GenelIslemler):
        proje_baslangic_tarihi = DatePickerField(label='Proje Başlangıç Tarihi',
                                                 disable_older_dates=False)
        proje_suresi = IntegerField(_('Proje Süresi'), validators=[DataRequired(
            message=_("Proje Süresi Alanı Boş Bırakılamaz"))], default=0)
        proje_suresi_birimi = SelectField(choices=ProjeSuresiBirimi.choices(),
                                          default=ProjeSuresiBirimi.ay,
                                          coerce=ProjeSuresiBirimi.coerce)

    class PA19(FlaskForm, GenelIslemler):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            toplantilar = DB.session.query(BapToplanti).filter(
                BapToplanti.sonuclandi_mi == False).all()

            toplanti_list = [(0, _("Lütfen kararın alındığı toplantıyı seçiniz"))]
            for toplanti in toplantilar:
                toplanti_list.append((toplanti.id,
                                      "Toplanti Tarihi: {}".format(
                                          toplanti.toplanti_tarihi.strftime('%d.%m.%Y'))))

            self.toplanti_tarihi.choices = toplanti_list
            self.toplanti_tarihi.default = 0

        toplanti_tarihi = SelectField(label=_("Toplantı tarihi seçiniz"),
                                      coerce=int)
        ek_dosya_id = MultiFileField("Gündeme Ait Ek Dosya", validators=[Optional()])
        sablon_id = HiddenIntegerField()
        karar = SummerNoteField(_("Karar"))
        aciklama = SummerNoteField(_("Gündem"))
        tipi = SelectField(_("Gündem Tipi"),
                           choices=GundemTipi.choices(),
                           coerce=GundemTipi.coerce)
        karar_durum = SelectField(_("Karar Durumu"),
                                  choices=KararDurumu.choices(),
                                  coerce=KararDurumu.coerce)

    class PA20(FlaskForm, GenelIslemler):
        proje_kalemleri = FieldList(FormField(ProjeKalemiFormu))


class DurumFormlari:
    class GenelForm(FlaskForm, GenelIslemler):
        pass

    class P13(FlaskForm, GenelIslemler):
        information = [
            _("Proje hakemleri bölümünden yeni hakem ekleyip çıkartabilirsiniz"),
            _("Proje işlemleri bölümünden hakemlere ara rapor gönderebilirsiniz")
        ]

    class P15(FlaskForm, GenelIslemler):
        information = [
            _("Eğer raporun sonucunu revizyon bekleniyor durumuna getirirseniz proje "
              "durumunu 'p20' olarak ayarlamanız gerekir.")
        ]
        raporlar = SelectField(_("Ara Raporlar"), coerce=int)
        degerlendirme_sonucu = SelectField(_("Değerlendirme Sonucu"),
                                           choices=ProjeDegerlendirmeSonuc.choices(),
                                           default=ProjeDegerlendirmeSonuc.degerlendirilmedi,
                                           coerce=ProjeDegerlendirmeSonuc.coerce)

        def validate_raporlar(self, _):
            if not self.raporlar.data:
                raise ValidationError(message="Lütfen rapor seçiniz")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            # todo: query moduleleri olusturuldugunda rapor tipine ve proje id sine gore bir query yazıp o module taşı
            proje_ara_raporlari = DB.session.query(ProjeRapor).filter(
                ProjeRapor.proje_id == proje_id,
                ProjeRapor.durumu == ProjeRaporDurumu.tamamlandi,
                ProjeRapor.rapor_tipi == ProjeRaporTipi.ara_rapor
            ).all()
            proje_raporlari_list = [(0, _("Lütfen Rapor Seçiniz"))]
            for proje_rapor in proje_ara_raporlari:
                proje_raporlari_list.append(
                    (proje_rapor.id, "{} - {} - {}".format(proje_rapor.rapor_tipi.value,
                                                           proje_rapor.created_at.strftime(
                                                               "%d-%m-%Y"),
                                                           proje_rapor.rapor_degerlendirme_durumu.value
                                                           ))
                )

            self.raporlar.choices = proje_raporlari_list
            self.raporlar.default = 0

    class P18(FlaskForm, GenelIslemler):
        information = [
            _("Proje hakemleri bölümünden yeni hakem ekleyip çıkartabilirsiniz"),
            _("Proje işlemleri bölümünden hakemlere sonuç raporu gönderebilirsiniz")
        ]

    class P19(FlaskForm, GenelIslemler):
        information = [
            _("Eğer raporun sonucunu revizyon bekleniyor durumuna getirirseniz proje "
              "durumunu 'p20' olarak ayarlamanız gerekir.")
        ]
        raporlar = SelectField(_("Ara Raporlar"), coerce=int)
        degerlendirme_sonucu = SelectField(_("Değerlendirme Sonucu"),
                                           choices=ProjeDegerlendirmeSonuc.choices(),
                                           default=ProjeDegerlendirmeSonuc.degerlendirilmedi,
                                           coerce=ProjeDegerlendirmeSonuc.coerce)

        def validate_raporlar(self, _):
            if not self.raporlar.data:
                raise ValidationError(message="Lütfen rapor seçiniz")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            proje_id = request.view_args.get("proje_id")

            # todo: query moduleleri olusturuldugunda rapor tipine ve proje id sine gore bir query yazıp o module taşı
            proje_ara_raporlari = DB.session.query(ProjeRapor).filter(
                ProjeRapor.proje_id == proje_id,
                ProjeRapor.durumu == ProjeRaporDurumu.tamamlandi,
                ProjeRapor.rapor_tipi == ProjeRaporTipi.sonuc_raporu
            ).all()
            proje_raporlari_list = [(0, _("Lütfen Rapor Seçiniz"))]
            for proje_rapor in proje_ara_raporlari:
                proje_raporlari_list.append(
                    (proje_rapor.id, "{} - {} - {}".format(proje_rapor.rapor_tipi.value,
                                                           proje_rapor.created_at.strftime(
                                                               "%d-%m-%Y"),
                                                           proje_rapor.rapor_degerlendirme_durumu.value
                                                           ))
                )

            self.raporlar.choices = proje_raporlari_list
            self.raporlar.default = 0

    class P22(FlaskForm, GenelIslemler):
        proje_bitis_tarihi = DatePickerField(
            "Y.K Toplantısında belirlenen proje sonlandırma tarihi :",
            format='%d.%m.%Y',
            validators=[validators.DataRequired(message=_("Bu alan boş bırakılamaz"))],
            disable_older_dates=False)

        yk_toplanti_sayisi = IntegerField(_('Proje Bitiş Y.K Toplantı Sayısı'),
                                          validators=[DataRequired(
                                              message=_("Bu alan boş Bırakılamaz"))], default=0)

        ilgili_karar = SelectField(label=_('İlgili Karar'))

    class P23(FlaskForm, GenelIslemler):
        yk_toplanti_tarihi = DatePickerField(
            "Proje sonuç raporunun kabul edildiği komisyon tarihi :",
            format='%d.%m.%Y',
            validators=[validators.DataRequired(message=_("Bu alan boş bırakılamaz"))],
            disable_older_dates=False)

        yk_toplanti_sayisi = IntegerField(_('Komisyon Sayısı'), validators=[DataRequired(
            message=_("Bu alan boş bırakılamaz"))], default=0)

    class P24(FlaskForm, GenelIslemler):
        dondurulacak_tarih = DatePickerField("Hangi tarihe kadar dondurulacak? :",
                                             format='%d.%m.%Y',
                                             validators=[validators.DataRequired(
                                                 message=_("Bu alan boş bırakılamaz"))],
                                             disable_older_dates=False)

    class P34(FlaskForm, GenelIslemler):
        kaldirma_nedeni = StringField(
            label=_('Yetki kaldırma nedeni. Not:Bu neden yürütücüye gösterilecektir'),
            validators=[DataRequired(message=_("Bu alan boş bırakılamaz"))])
