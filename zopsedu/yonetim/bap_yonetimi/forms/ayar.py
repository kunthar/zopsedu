"""Ayarlar form"""
from flask_wtf import FlaskForm
from wtforms import FormField

from zopsedu.yonetim.bap_yonetimi.forms.ebys_ayarlari import EbysAyarlari
from zopsedu.yonetim.bap_yonetimi.forms.mail_sunucu_ayarlari import MailSunucuAyarlariForm
from zopsedu.yonetim.bap_yonetimi.forms.site_ayarlari import SiteAyarlariForm


class AyarlarForm(FlaskForm):
    """Ayarlar genel form """
    site_ayarlari = FormField(SiteAyarlariForm)
    mail_sunucu_ayarlari = FormField(MailSunucuAyarlariForm)
    ebys_ayarlari = FormField(EbysAyarlari)
