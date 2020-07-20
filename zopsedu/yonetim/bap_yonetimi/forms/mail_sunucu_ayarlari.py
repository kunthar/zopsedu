"""Mail Sunucusu Ayar Formu"""

from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField
from wtforms.validators import EqualTo, Optional

from zopsedu.lib.mail import connection_test


class MailSunucuAyarlariForm(FlaskForm):
    mail_server = StringField(_("Mail sunucusunun adresi"))
    mail_port = IntegerField(_("Mail sunucusunun port numarası"), validators=[Optional()])
    mail_use_tls = BooleanField(_("TLS kullanılsın"), default=False)
    mail_use_ssl = BooleanField(_("SSL kullanılsın"), default=False)
    mail_username = StringField(_("Mail sunucusu kullanıcı adı*"))

    mail_password = PasswordField(_("Mail sunucusu kullanıcı parolası"), validators=[
        EqualTo('mail_password_repeat', message=_('Girdiğiniz parolalar eşleşmelidir.'))
    ])
    mail_password_repeat = PasswordField(_("Mail sunucusu kullanıcı parolası tekrar"))

    mail_default_sender = StringField(_("Varsayılan gönderen mail adresi"), default=0)

    # Mail sunucusu tarafindan konulan baglanti basina gonderilebilen mail siniri.
    # Bulk mail gonderimi sirasinda eger bu sayidan fazla mail gonderilmeye calisilirsa
    # Siniri yenilemek icin yeni connection olusturulur.
    mail_max_emails = IntegerField(_("Bağlantı başına gönderilebilen mail limiti"), validators=[Optional()])

    # todo: mail connection test edilmesi gerekiyor mu ?
    # def validate(self):
    #     self.connection_success = False
    #     self.errors["form_errors"] = []
    #     # Alanlarin bir kaci veya hepsi dolu mu kontrol eder.
    #     has_any_data = False
    #     has_all_data = True
    #     for key in self.data.keys():
    #         # Do not evaluate boolean fields and some fields
    #         if key is 'csrf_token' or self.data[key] is True or self.data[key] is False or \
    #                 key is 'mail_max_emails':
    #             continue
    #         if self.data[key]:
    #             has_any_data = True
    #         else:
    #             has_all_data = False
    #     if has_any_data:
    #         if has_all_data:
    #             config = {
    #                 'mail_use_ssl': self.mail_use_ssl.data,
    #                 'mail_use_tls': self.mail_use_tls.data,
    #                 'mail_server': self.mail_server.data,
    #                 'mail_port': self.mail_port.data,
    #                 'mail_username': self.mail_username.data,
    #                 'mail_password': self.mail_password.data
    #             }
    #             conn_test_result = connection_test(config)
    #             if not conn_test_result:
    #                 self.errors["form_errors"].append(_("Verilen ayarlar ile mail "
    #                                                     "sunucusuna bağlantı kurulamadı."))
    #                 return False
    #             self.connection_success = True
    #         else:
    #             # Alanlarin bir kaci doldurulmus ancak hepsi doldurulmamis.
    #             self.errors["form_errors"].append(_("Mail sunucusu ayarlarında "
    #                                                 "yıldız(*) ile işaretli alanların "
    #                                                 "girilmesi zorunludur."))
    #             return False
    #     return True
