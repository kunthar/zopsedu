"""Proje Arama Formu"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import SubmitField, StringField, Form, FormField
from wtforms import SelectField

from zopsedu.lib.db import DB
from zopsedu.lib.form.fields import DatePickerField
from zopsedu.models import AppState
from zopsedu.models.helpers import StateTypes, AppStates


class DatePickerForm(Form):
    """Example form for Date Picker"""
    talep_tarihi = DatePickerField(_('Talep Tarihi'), disable_older_dates=False)
    talep_tarihi_option = SelectField(
        choices=[('0', 'Önceki Tarih'), ('1', 'Şuanki Tarih'), ('2', 'Sonraki Tarih')], default=1)


class SatinalmaTalepSearchForm(FlaskForm):
    """Proje Arama Formu"""
    proje_no = StringField(label="Proje No")
    proje_turu_adi = StringField(label="Proje Türü Adı")
    yurutucu = StringField(label='Yürütücü Adı')
    date = FormField(DatePickerForm)
    talep_durumu = SelectField(label="Satinalma Durum Kodu")
    temizle = SubmitField(label='Temizle')
    submit = SubmitField(label='Ara')
    satinalma_sureci = SelectField(label=_('Satınalma Genel Süreci'),
                                   choices=[("-1", "Tümü"),
                                            (AppStates.basvuru_kabul, AppStates.basvuru_kabul.value),
                                            (AppStates.devam, AppStates.devam.value),
                                            (AppStates.son, AppStates.son.value)],
                                   default="-1")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        talepler = DB.session.query(AppState).filter(AppState.state_type == StateTypes.satinalma).all()

        talep_list = [(0, _("Tüm Durumlar"))]

        for talep in talepler:
            talep_list.append((talep.id, talep.state_code))

        self.talep_durumu.choices = talep_list
        self.talep_durumu.default = 0

    def validate(self):
        if not any([self.proje_no.data,
                    self.proje_turu_adi.data,
                    self.yurutucu.data,
                    self.date.talep_tarihi.data]):
            return False
        return True
