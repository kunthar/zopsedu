"""Signal Sender"""
import json
from datetime import datetime
from flask import current_app, session, request
from flask_login import current_user

from zopsedu.lib.sessions import SessionHandler
from zopsedu.lib.signals.signals import activity_log_signal, email_signal
from zopsedu.lib.signals.signals import sms_signal, notification_signal



#todo paremetreler notification, sms ve emaile gore tekrar duzenlenecek
def signal_sender(log=True, notification=False, sms=False, email=False,
                  database=False, notification_sender=None, notification_receiver=None,
                  notification_message=None, notification_title=None, proje_id=None, **payload):
    """
    User aktivitelerinden olusan eventlerin track edilmesini ve gerekli ise yeni
    actionlar alinmasini saglayan metot.

    Examples:
        For only log purposes:
        log_message = "Message to log"
        signal_sender(payload={"log_message": log_message})

        For sending notification:
        payload = {
            "nesne": "Rol",
            "nesne_id": 5,
            "ekstra_mesaj": "5 idli Rol update edildi.",
            "notification_receiver": 27,
            "notification_title": "Rol Update Başarılı",
        }
        ntf_message = "Message to send as a notification"
        signal_sender(notification=True, notification_message=ntf_message, **payload)
        // sender göndermediğimiz için sender current_user oldu.

    Args:
        log (bool): Log kaydi olsun/olmasin
        notification (bool): System notificationi gonderilsin/gonderilmesin
        sms (bool): Sms gonderilsin/gonderilmesin
        email (bool): Email gonderilsin/gonderilmesin
        database (bool):
        notification_sender (str):
        notification_message (str):
        **payload (dict): Gelen parametrelerin tetikleyecegi actiona gore gerekecek datayi iceren
                          dictionary
            * nesne (str): adi,
            * nesne_id (int): id,
            * etkilenen_nesne (str): adi,
            * etkilenen_nesne (int): id,
            * ekstra_mesaj (str): ,

    Returns:

    """
    payload.update({
        "zaman": datetime.now(),
        "session": session.get("_id"),
        "context": session.get("activity_context"),
        "user_id": current_user.id,
        "username": current_user.username,
        "user_role_id": session.get('current_user_role'),
        "role_id": session.get('current_role'),
        "role_name": session.get('current_role_name'),
        "remote_ip": request.remote_addr,
        "tarayici_bilgisi": request.headers.get('User-Agent'),
        "host": request.headers.get('Host'),
        "origin": request.headers.get('Origin'),
        "referer": request.headers.get('Referer'),
        "cookie": request.headers.get('Cookie'),
        "endpoint_url": request.base_url,
        "method": request.method,
    })

    sender = current_app._get_current_object()  # pylint: disable=protected-access

    if log:
        activity_log_signal.send(sender, **payload)

    if notification:
        if not notification_sender:
            system_user = SessionHandler.system_user()
            notification_sender = system_user['person_id']
        if not notification_message:
            notification_message = payload['ekstra_mesaj']
        payload['notification_message'] = notification_message
        payload['notification_sender'] = notification_sender
        payload['notification_receiver'] = notification_receiver
        payload['notification_title'] = notification_title
        payload['proje_id'] = proje_id
        notification_signal.send(sender, **payload)

    if sms:
        sms_signal.send(sender, **payload)

    if email:
        system_user = SessionHandler.system_user()
        payload['email_system_person_id'] = system_user['person_id']
        email_signal.send(sender, **payload)

    if database:
        # todo: database
        pass
