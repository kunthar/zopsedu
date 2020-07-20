"""Proje Arama Formu"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import SubmitField, StringField, Form, FormField
from wtforms import IntegerField, SelectField
from zopsedu.lib.form.fields import DatePickerField


class DatePickerForm(Form):
    """Example form for Date Picker"""
    siparis_tarihi = DatePickerField(_('Sipariş Tarihi'), disable_older_dates=False)
    siparis_tarihi_option = SelectField(
        choices=[('0', 'Önceki Tarih'), ('1', 'Şuanki Tarih'), ('2', 'Sonraki Tarih')], default=1)
    teslim_edilmesi_beklenen_tarih = DatePickerField(_('Teslim Edilmesi Beklenen Tarihi'), disable_older_dates=False)
    teslim_edilmesi_beklenen_tarih_option = SelectField(
        choices=[('0', 'Önceki Tarih'), ('1', 'Şuanki Tarih'), ('2', 'Sonraki Tarih')], default=1)


class TeslimiBeklenenFirmalarSearchForm(FlaskForm):
    """Proje Arama Formu"""
    firma_adi = StringField(label="Firma Adı")
    proje_no = StringField(label="Proje No")
    yurutucu = StringField(label='Yürütücü Adı')
    siparis_no = StringField(label="Sipariş No")
    date = FormField(DatePickerForm)
    gun_gecikmesi = SelectField(label="Gün Gecikmesi",
                                choices=[('0', 'Tümü'), ('1', 'Günü Geçmeyenler'), ('2', 'Günü Geçenler'),
                                         ('3', 'Bugün')], default=0)

    temizle = SubmitField(label='Temizle')
    submit = SubmitField(label='Ara')

    def validate(self):
        if not any([self.firma_adi.data,
                    self.proje_no.data,
                    self.yurutucu.data,
                    self.siparis_no.data,
                    self.date.siparis_tarihi.data,
                    self.date.teslim_edilmesi_beklenen_tarih.data]):
            return False
        return True
