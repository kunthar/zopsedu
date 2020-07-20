"""Proje Arama Formu"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import SubmitField, StringField, Form, DecimalField, FormField
from wtforms import IntegerField, SelectField
from zopsedu.lib.form.fields import DatePickerField


class DatePickerForm(Form):
    """ form for Date Picker"""

    siparis_kabul_tarihi = DatePickerField(_('Sipariş Kabul Tarihi'), disable_older_dates=False)
    siparis_kabul_tarihi_option = SelectField(
        choices=[('0', 'Önceki Tarih'), ('1', 'Şuanki Tarih'), ('2', 'Sonraki Tarih')], default=1)


class SatinalinanMalzemelerSearchForm(FlaskForm):
    """Satinalinan Malzeme Arama Formu"""
    malzeme_adi = StringField(label="Malzeme Adı")
    siparis_no = StringField(label="Sipariş No")
    firma_adi = StringField(label="Firma Adı")
    proje_no = StringField(label="Proje No")
    yurutucu = StringField(label='Yürütücü Adı')
    date = FormField(DatePickerForm)
    talep_miktari = IntegerField(label="Talep Miktarı")
    talep_miktari_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)

    toplam_fiyati = DecimalField(label="Toplam Fiyatı")
    toplam_fiyati_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)

    temizle = SubmitField(label='Temizle')
    submit = SubmitField(label='Ara')

    def validate(self):
        if not any([
            self.malzeme_adi.data,
            self.siparis_no.data,
            self.proje_no.data,
            self.yurutucu.data,
            self.date.siparis_kabul_tarihi.data,
            self.talep_miktari.data,
            self.toplam_fiyati.data,
            self.firma_adi.data
        ]):
            return False
        return True
