"""gelen kutusu form modülü"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import SelectField

from zopsedu.common.mesaj.models import MesajTipleri


class MesajSearchForm(FlaskForm):
    choices = [("-1", "Tümü"),
               (MesajTipleri.sms, MesajTipleri.sms.value),
               (MesajTipleri.eposta, MesajTipleri.eposta.value),
               (MesajTipleri.sistem, MesajTipleri.sistem.value)]

    mesaj_turu = SelectField(
        label="Mesaj Tipleri",
        choices=choices, default="-1")

    mesaj_okunma_durumu=SelectField(
        label="Mesaj Okunma Durumu",
        choices=[("-1", "Tüm Mesajlar"),("0","Okunmamış Mesajlar")]
    )

