"""Signals"""
from datetime import datetime
from blinker import Namespace

from zopsedu.bap.models.proje_mesajlari import ProjeMesaj
from zopsedu.common.mesaj.models import Mesaj, MesajTipleri
from zopsedu.lib.db import DB
from zopsedu.lib.decorators import signal_listener
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.mail import send_mail_with_template
from zopsedu.models.activity_log import AktiviteKaydi


# pylint: disable=unused-argument
@signal_listener('activity_log')
def log_signal_listener(sender, **extra):
    """
    Log signalini dinler.
    Args:
        sender:
        **extra (dict):
            * log_message (str): Log mesaji

    Returns:

    """
    DB.session.add(AktiviteKaydi(**extra))
    DB.session.commit()
    # pylint: enable=unused-argument


# pylint: disable=unused-argument
@signal_listener('notification')
def notification_signal_listener(sender, **extra):
    """
    Notification signalini dinler.
    Args:
        sender:
        **extra (dict):
            * notification_sender
            * notification_receiver
            * notification_message
            * notification_title
            * proje_id

    Returns:

    """
    n_sender = extra.get('notification_sender')
    n_receiver = extra.get('notification_receiver')
    n_message = extra.get('notification_message')
    n_title = extra.get('notification_title')
    proje_id = extra.get('proje_id')
    related_table = extra.get("related_table", None)
    mesaj = Mesaj(
        gonderen=n_sender,
        alici=n_receiver,
        baslik=n_title,
        metin=n_message,
        gonderim_zamani=datetime.now(),
        mesaj_tipi=MesajTipleri.sistem
    )
    DB.session.add(mesaj)
    DB.session.flush()
    if related_table == "proje_mesaj":
        proje_mesaj = ProjeMesaj(mesaj_id=mesaj.id, proje_id=proje_id)
        DB.session.add(proje_mesaj)

    DB.session.commit()
    # pylint: enable=unused-argument


# pylint: disable=unused-argument
@signal_listener('sms')
def sms_signal_listener(sender, **extra):
    """
    sms signalini dinler.
    Args:
        sender:
        **extra (dict):

    Returns:

    """
    pass
    # pylint: enable=unused-argument


# pylint: disable=unused-argument
@signal_listener('email')
def email_signal_listener(sender, **extra):
    """
    Email signalini dinler.
    Args:
        sender:
        **extra (dict):
    Returns:

    """
    email_recipients = extra.get("email_recipients")
    if not email_recipients and not isinstance(email_recipients, list):
        raise Exception("Alıcı mail adresi bulunamadı")

    email_person_id = extra.get("email_person_id")
    if not email_person_id and not isinstance(email_person_id, list):
        raise Exception("Alıcı id bulunamadı")

    email_system_person_id = extra.get("email_system_person_id", None)

    email_subject = extra.get("email_subject", None)
    email_content_text = extra.get("email_content_text", None)

    email_logo_src = extra.get("email_logo_src", None)
    email_logo_text = extra.get("email_logo_text", None)
    email_logo_href = extra.get("email_logo_href", None)

    email_title_text = extra.get("email_title_text", None)

    email_greeting = extra.get("email_greeting", None)
    email_greeting_name = extra.get("email_greeting_name", None)

    email_button_href = extra.get("email_button_href", None)
    email_button_text = extra.get("email_button_text", None)

    email_content_end_text = extra.get(" email_content_end_text", None)
    email_footer_text = extra.get(" email_footer_text", None)
    email_attachments = extra.get(" email_attachments", None)
    email_cc = extra.get("email_cc", None)
    email_bcc = extra.get("email_bcc", None)
    email_body = extra.get("email_body", None)
    email_sender = extra.get("email_sender", None)
    email_template = extra.get("template", "email_template_ping.html")

    email_proje_id = extra.get("email_proje_id", None)

    email_related_table = extra.get("related_table", None)

    send_mail_with_template(recipients=email_recipients, subject=email_subject,
                            content_text=email_content_text, logo_src=email_logo_src,
                            logo_text=email_logo_text, logo_href=email_logo_href,
                            title_text=email_title_text, greeting=email_greeting,
                            greeting_name=email_greeting_name, button_href=email_button_href,
                            button_text=email_button_text,
                            content_end_text=email_content_end_text, footer_text=email_footer_text,
                            template=email_template, attachments=email_attachments, cc=email_cc,
                            bcc=email_bcc, body=email_body, sender=email_sender)

    for person_id in email_person_id:
        try:
            mesaj = Mesaj(
                gonderen=email_system_person_id,
                alici=person_id,
                baslik=email_subject,
                metin=email_content_text,
                gonderim_zamani=datetime.now(),
                mesaj_tipi=MesajTipleri.eposta
            )
            DB.session.add(mesaj)
            DB.session.flush()
            if email_related_table == "proje_mesaj":
                proje_mesaj = ProjeMesaj(mesaj_id=mesaj.id, proje_id=email_proje_id)
                DB.session.add(proje_mesaj)

            DB.session.commit()

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(
                hata="Sistem tarafından email gonderilirken bir hata oluştu "
                     "Hata: {}, Proje id: {}".format(email_proje_id, exc)
            )


# pylint: disable=invalid-name
zopsedu_signals = Namespace()
activity_log_signal = zopsedu_signals.signal('activity_log')
notification_signal = zopsedu_signals.signal('notification')
sms_signal = zopsedu_signals.signal('sms')
email_signal = zopsedu_signals.signal('email')
# pylint: enable=invalid-name
