"""Icerik ve baglantili formlarini iceren modul"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, BooleanField
from wtforms.validators import DataRequired, Length

from zopsedu.lib.form.fields import DatePickerField, SummerNoteField, MultiFileField, HiddenIntegerField, \
    DateTimePickerField


class IcerikEkDosyaFormu(FlaskForm):
    """Icerik ek dosya Formu"""
    icerik_ek_dosya_id = HiddenIntegerField()
    adi = StringField(_("Ek Dosya Adı"))
    icerik_id = MultiFileField()


class BapDuyuruForm(FlaskForm):
    """Bap Duyuru Formu"""
    form_information_list = [
        _("Bir duyurunun duyurular listesinde görünebilmesi için başlangıç, bitiş tarihleri "
          "arasında olmalı ve 'Duyuru Listesinde Görünsün mü?' kutucuğu işaretlenmelidir."),
        _("'Ön Sayfa Görünürlüğü' duyurunun bap anasayfasındaki duyurular bölümünde görünme "
          "durumunu belirtir."),
    ]
    icerik_id = HiddenIntegerField()
    ekleyen_ad_soyad = StringField(_("Ekleyen Kişi"), render_kw={"class": "form-control"})

    baslik = StringField(_("Duyuru Başlığı"),
                         validators=[
                             DataRequired(message=_("Duyuru Başlığı Alanı Boş Bırakılamaz")), Length(max=255)
                         ],
                         render_kw={"class": "form-control"})
    icerik = SummerNoteField(_("Duyuru Metni"),
                             validators=[
                                 DataRequired(message=_("Duyuru Metni Alanı Boş Bırakılamaz"))
                             ],
                             render_kw={"class": "form-control"})

    on_sayfa_gorunurlugu = BooleanField(_("Ön Sayfa Görünürlüğü"),
                                        render_kw={"class": "form-control"})
    aktif_mi = BooleanField(_("Duyuru Listesinde Görünsün mü ?"),
                            render_kw={"class": "form-control"})

    bitis_tarihi = DateTimePickerField(_("Son Geçerlilik Tarihi"),
                                   validators=[
                                       DataRequired(message=_("'Son Geçerlilik Tarihi' Alanı Boş Bırakılamaz"))
                                   ],
                                   render_kw={"class": "form-control"})
    baslangic_tarihi = DateTimePickerField(_("Aktif Olma Tarihi"),
                                       validators=[
                                           DataRequired(message=_("'Aktif Olma Tarihi' Alanı Boş Bırakılamaz"))
                                       ],
                                       render_kw={"class": "form-control"})

    ek_dosyalar = FieldList(FormField(IcerikEkDosyaFormu))
