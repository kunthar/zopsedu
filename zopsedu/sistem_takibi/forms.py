""" Sistem Takibi Form Modlülü"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SelectField, SubmitField, FormField

from zopsedu.lib.form.fields import DatePickerField



class DateSearchForm(Form):
    """
    Tarih arama formu.
    """
    baslama_tarihi = DatePickerField(_('Başlama Tarihi'), disable_older_dates=False)
    bitis_tarihi = DatePickerField(_('Bitiş Tarihi'), disable_older_dates=False)
    baslama_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)
    bitis_tarihi_option = SelectField(
        choices=[('0', 'Küçük'), ('1', 'Eşit'), ('2', 'Büyük')], default=1)


class KayitGecmisiForm(FlaskForm):
    """Kayit Gecmisi Formu"""
    ara_text = StringField(label=_('Aktivite Açıklamada Ara'))
    activite_tipleri = SelectField(_("Aktivite Tiplerinde Ara"), coerce=int)
    username = StringField(_('Kullanıcılarda Ara'))
    ara = SubmitField(label=_('Ara'))
    tarih_arama = FormField(DateSearchForm)
    temizle = SubmitField(label=_('Temizle'))

    def validate(self):
        return any([self.ara_text.data,
                    self.activite_tipleri,
                    self.tarih_arama.baslama_tarihi.data,
                    self.tarih_arama.bitis_tarihi.data])

