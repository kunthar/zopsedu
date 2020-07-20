"""Sms Form Modulu"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField


class SmsForm(FlaskForm):
    sms_aktif_mi = BooleanField(_("Sms Aktif Mi?"))
    akademik_personele_aktif_mi = BooleanField(_("Akademik Personele Aktif Mi?"))
    firmalara_aktif_mi = BooleanField(_("Firmalara Aktif Mi?"))
    yonetim_kurulu_katilimcilarina_aktif_mi = BooleanField(_("Yönetim Kurulu Katılımcılarına Aktif Mi?"))
    proje_yurutuculerine_aktif_mi = BooleanField(_("Proje Yürütücülerine Aktif Mi?"))
    hakemlere_aktif_mi = BooleanField(_("Hakemlere Aktif Mi?"))
    yoneticilere_aktif_mi = BooleanField(_("Yöneticilere Aktif Mi?"))
