from datetime import datetime

from flask import current_app, render_template_string
from flask_mail import Mail, Message
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPHeloError
from sqlalchemy import desc
from sqlalchemy.exc import InternalError, ProgrammingError

from zopsedu.app import app
from zopsedu.bap.models.proje_mesajlari import ProjeMesaj
from zopsedu.common.mesaj.models import Mesaj, MesajTipleri
from zopsedu.lib.db import DB
from zopsedu.lib.sessions import SessionHandler
from zopsedu.models import SiteAyarlari, Sablon


def init_mail(app=None):
    """
    flask-mail i initialize eder
    """
    if app is None:
        app = current_app

    mail = Mail()

    try:
        universite_id = SessionHandler.universite_id()
        ayarlar = DB.session.query(SiteAyarlari).filter_by(universite_id=universite_id).first()
        mail_sunucu_ayarlari = ayarlar.params["mail_sunucu_ayarlari"]
        mail_config = {
            "MAIL_SERVER": mail_sunucu_ayarlari['mail_server'],
            "MAIL_PORT": mail_sunucu_ayarlari['mail_port'],
            "MAIL_USE_TLS": mail_sunucu_ayarlari['mail_use_tls'],
            "MAIL_USE_SSL": mail_sunucu_ayarlari['mail_use_ssl'],
            "MAIL_USERNAME": mail_sunucu_ayarlari['mail_username'],
            "MAIL_PASSWORD": ayarlar.mail_password,
            "MAIL_DEFAULT_SENDER": mail_sunucu_ayarlari['mail_default_sender'],
            "MAIL_MAX_EMAILS": mail_sunucu_ayarlari['mail_max_emails']
        }
        app.logger.info("Mail ayarlari databaseden tekrar yuklendi")
        state = mail.init_mail(config=mail_config)
        app.extensions['mail'] = state

    except (AttributeError, RuntimeError, InternalError, ProgrammingError):
        app.logger.info("Mail ayarlari databaseden yuklenemedi config'den aliniyor")
        mail.init_app(app=app)


def connection_test(config):
    smtp = SMTP
    if config['mail_use_ssl']:
        smtp = SMTP_SSL
    try:
        with smtp(host=config['mail_server'], port=config['mail_port']) as conn:
            if config['mail_use_tls']:
                conn.starttls()
            conn.login(user=config['mail_username'], password=config['mail_password'])
        return True
    except (SMTPAuthenticationError, SMTPHeloError):
        return False


def send_mail_with_template(recipients: list, subject, content_text, logo_src=None,
                            logo_text=None, logo_href=None, title_text=None, greeting=None,
                            greeting_name=None, button_href=None, button_text=None,
                            content_end_text=None, footer_text=None,
                            template=None, attachments=None, cc=None,
                            bcc=None, body=None, sender=None):
    """

    :param recipients: recipient mail addresses. List of strings
    :param subject: subject of the mail. Passed to Message instance
    :param logo_src: url of logo passed to template,
                    default : logo located in SiteAyarlari or Zopsedu logo
    :param logo_text: logo text located under the logo, passed to template.
    :param logo_href: href value passed to both logo_text and logo_url
    :param title_text: title text passed to template
    :param greeting: greeting for the greeting name, passed to template
    :param greeting_name: greeting name, passed to the template
    :param content_text: content text, passed to the template
    :param button_href: href value of button, passed to the template
    :param button_text: text value of button, passed to the template
    :param content_end_text: content end text, passed to the template
    :param footer_text: footer text passed to template
    :param template: template name for the send mail. Gets used for rendering the mail.
    :param attachments: A list of Attachment instances, gets added to the Message instance
    :param cc: CC mail addresses. List of strings
    :param bcc: BCC mail addresses. List of strings
    :param body: Plain text value for body of mail. Passed to Message instance
    :param sender: Sender mail address of mail. default: default sender mail address set
                while initiating mail instance
    :return: returns rendered template html
    """
    ayarlar = DB.session.query(SiteAyarlari).filter_by(
        universite_id=SessionHandler.universite_id()).first()
    genel_ayarlar = None
    if ayarlar and ayarlar.params and ayarlar.params["site_ayarlari"] and ayarlar.params["site_ayarlari"]["genel"]:
        genel_ayarlar = ayarlar.params["site_ayarlari"]["genel"]

    if not logo_src:
        if ayarlar and ayarlar.logo and genel_ayarlar:
            logo_src = "{}{}".format(genel_ayarlar["site_adi"],
                                     ayarlar.logo.url)
            logo_href = genel_ayarlar["site_adi"]
        else:
            logo_src = 'http://v2.zopsedu.net/static/assets/img/brand-logo2-white.png'

    if template is None:
        # sablon tipi 52 email sablonunu isaret eder. degistirilmemelidir.
        guncel_email_sablonu = DB.session.query(Sablon).filter(
            Sablon.kullanilabilir_mi == True,
            Sablon.sablon_tipi_id == 52
        ).order_by(
            desc(Sablon.updated_at)
        ).first()
        template = guncel_email_sablonu.sablon_text

    if not footer_text and genel_ayarlar:
        footer_text = """
                        <strong>Telefon: {}</strong><br>
                        <strong>Faks: {}</strong><br>
                        <strong>Adres: {}</strong><br>
                      """.format(genel_ayarlar.get("telefon", "-"),
                                 genel_ayarlar.get("faks", "-"),
                                 genel_ayarlar.get("adres", "-"))

    html = render_template_string(template,
                                  logo_src=logo_src,
                                  logo_text=logo_text,
                                  logo_href=logo_href,
                                  title_text=title_text if title_text else subject,
                                  greeting=greeting,
                                  greeting_name=greeting_name,
                                  content_text=content_text,
                                  button_href=button_href,
                                  button_text=button_text,
                                  content_end_text=content_end_text,
                                  footer_text=footer_text,
                                  )

    msg = Message(recipients=recipients, attachments=attachments, cc=cc,
                  bcc=bcc, body=body, sender=sender, subject=subject)
    msg.html = html
    current_app.extensions['mail'].send(msg)
    return html


def mail_gonder(recipients: list, subject, content_text, sender, proje_id=None, **mail_params):
    """
    Recipients = [
        {
          "email": "halil.duruakan@zetaops.io"
          "person_id": 1
        },
        {
          "email": "samedhan.karamese@zetaops.io"
          "person_id": 2
        },
    ]
    :param recipients: list of dict
    :param sender: mesaji gonderen kisinin person id si. Genel olarak system userdir.
    :param subject: mesaj konusu
    :param content_text: mesaj içerigi
    :param proje_id: eger gonderilecek mail proje ile alakali ise proje mesajlarina eklenmesi icin
                     bu parametre gereklidir
    :param mail_params: send_mail_with_template icin gerekli parametreleri icerir
    :return:
    """
    with app.app_context():
        if not sender:
            system_user = SessionHandler.system_user()
            sender = system_user["user_id"]

        email_list = []
        person_ids = []
        for recipient in recipients:
            email_list.append(recipient["email"])
            person_ids.append(recipient["person_id"])

        send_mail_with_template(recipients=email_list, sender=None,
                                subject=subject, content_text=content_text,
                                **mail_params)

        for person_id in person_ids:
            try:
                mesaj = Mesaj(
                    gonderen=sender,
                    alici=person_id,
                    baslik=subject,
                    metin=content_text,
                    gonderim_zamani=datetime.now(),
                    mesaj_tipi=MesajTipleri.eposta
                )
                DB.session.add(mesaj)
                DB.session.flush()
                if proje_id:
                    proje_mesaj = ProjeMesaj(mesaj_id=mesaj.id, proje_id=proje_id)
                    DB.session.add(proje_mesaj)

                DB.session.commit()

            except Exception as exc:
                DB.session.rollback()
                current_app.logger.error("Mail gönderilmeye  calisilirken bir hata ile "
                                         "karsilasildi. Hata: {}".format(exc))

