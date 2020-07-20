"""Proje Arama Formu"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import SubmitField, StringField, Form, FormField
from wtforms import SelectField
from zopsedu.lib.form.fields import DatePickerField
from zopsedu.models.helpers import SiparisDurumu


class DatePickerForm(Form):
    """Example form for Date Picker"""
    muayeneye_gonderilen_tarih = DatePickerField(_('Muayeneye Gönderilen Tarih'), disable_older_dates=False)
    muayeneye_gonderilen_tarih_option = SelectField(
        choices=[('0', 'Önceki Tarih'), ('1', 'Şuanki Tarih'), ('2', 'Sonraki Tarih')], default=1)


class MuayeneTeslimListesiSearchForm(FlaskForm):
    """Proje Arama Formu"""
    firma_adi = StringField(label="Firma Adı")
    malzeme_adi = StringField(label="Malzeme Adı")
    proje_no = StringField(label="Proje No")
    yurutucu = StringField(label='Yürütücü Adı')
    siparis_no = StringField(label="Sipariş No")
    date = FormField(DatePickerForm)

    # todo: Kullaniliyormu ???
    firma_bekleniyor = "Firma Bekleniyor"
    teslim_alindi = "Teslim Alındı"
    muayene_onayladi = "Muayene Komisyonu Onayladı"
    muayene_reddetti = "Muayene Komisyonu Reddetti"
    siparis_tamamlandi = "Sipariş Tamamlandı"

    choices = [("-1", "Tümü"),
               (SiparisDurumu.muayeneye_gonderildi, SiparisDurumu.muayeneye_gonderildi.value),
               (SiparisDurumu.muayene_onayladi, SiparisDurumu.muayene_onayladi.value),
               (SiparisDurumu.muayene_reddetti, SiparisDurumu.muayene_reddetti.value)]

    muayene_durumu = SelectField(choices=choices, default="-1")
    temizle = SubmitField(label='Temizle')
    submit = SubmitField(label='Ara')

    def validate(self):
        if not any([self.firma_adi.data,
                    self.proje_no.data,
                    self.yurutucu.data,
                    self.siparis_no.data,
                    self.malzeme_adi.data,
                    self.date.muayeneye_gonderilen_tarih.data]):
            return False
        return True
