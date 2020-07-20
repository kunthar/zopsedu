"""Proje Arama Formu"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import StringField, Form, FormField
from wtforms import IntegerField, DecimalField, SelectField
from wtforms.validators import Length

from zopsedu.lib.db import DB
from zopsedu.lib.form.fields import DatePickerField
from zopsedu.models import AppState
from zopsedu.models.helpers import StateTypes, AppStates


class DatePickerForm(Form):
    """Example form for Date Picker"""
    baslama_tarihi = DatePickerField(_('Başlama Tarihi'), disable_older_dates=False)
    bitis_tarihi = DatePickerField(_('Bitiş Tarihi'), disable_older_dates=False)
    baslama_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)
    bitis_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)


class SearchForm(FlaskForm):
    """Proje Arama Formu"""
    ad = StringField(label='Proje Adı', validators=[Length(max=250)])
    proje_turu_adi = StringField(label="Proje Türü Adı", validators=[Length(max=255)])
    proje_no = IntegerField(label="Proje Numarası")
    butce = DecimalField(label='Bütçe')
    butce_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)

    proje_sureci = SelectField(label=_('Projelerin Genel Süreci'),
                               choices=[("-1", "Tümü"),
                                        (AppStates.basvuru_kabul, AppStates.basvuru_kabul.value),
                                        (AppStates.devam, AppStates.devam.value),
                                        (AppStates.son, AppStates.son.value)],
                               default="-1")

    yurutucu = StringField(label='Yürütücü Adı')
    date = FormField(DatePickerForm)
    proje_durumu = SelectField(label="Proje Durum Kodu")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        durumlar = DB.session.query(AppState).filter(AppState.state_type == StateTypes.proje).all()

        durum_list = [(0, _("Tüm Durumlar"))]

        for durum in durumlar:
            durum_list.append((durum.id, durum.state_code))

        self.proje_durumu.choices = durum_list
        self.proje_durumu.default = 0

    def validate(self):
        if not any([self.ad.data,
                    self.proje_turu_adi.data,
                    self.proje_no.data,
                    self.butce.data,
                    self.yurutucu.data,
                    self.date.baslama_tarihi.data,
                    self.date.bitis_tarihi.data,
                    self.proje_durumu.data]):
            return False
        return True


class BAPProjeSearchForm(FlaskForm):
    """Bap Projeler Arama Formu"""
    proje_ad = StringField(label='Proje Adı', validators=[Length(max=250)])
    proje_turu_adi = StringField(label="Proje Türü Adı", validators=[Length(max=255)])
    proje_no = IntegerField(label="Proje Numarası")
    date = FormField(DatePickerForm)

    def validate(self):
        if not any([self.proje_ad.data,
                    self.proje_turu_adi.data,
                    self.proje_no.data,
                    self.date.bitis_tarihi.data]):
            return False
        return True
