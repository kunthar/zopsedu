from flask_login import current_user

from zopsedu.models.helpers import JobTypes
from zopsedu.lib.base_job_handler import BaseJobHandler
from zopsedu.lib.mail import mail_gonder


def email_scheduler(recipients: list,
                    sender=None,
                    subject=None,
                    content_text=None,
                    proje_id=None,
                    scheduler_params=None,
                    tracker_description="Mail Gönderildi",
                    **mail_params):
    """

    :param recipients: mesaj alici listesi
    :param sender: mesaji gonderen kisinin person id
    :param proje_id: eger mesaj proje ile alakali ise ProjeMesaj instance icin gerekli parametre
    :param subject: mesajin konusu
    :param content_text: mesaj icerigi
    :param tracker_description: AppStateTracker icin gerekli olan description
    :param mail_params: Mail ayarlari icin gerekli olan diger parametreleri ve
           scheduler icin gerekli parametreleri icerir.
           ek mail parametreleri icin zopsedu.lib.mail.py dosyasindaki send_mail_with_template
           fonksiyonu incelenebilir.
    :param scheduler_params: dict olarak scheduler icin gerekli parametreler gonderilmelidir.
           ornegin {"trigger": "date", "run_date": datetime.now() + timedelta(seconds=10)}
           scheduler parametreleri icin :
           cron ------> https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html#module-apscheduler.triggers.cron
           interval --> https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html#module-apscheduler.triggers.interval
           date ------> https://apscheduler.readthedocs.io/en/latest/modules/triggers/date.html#module-apscheduler.triggers.date
           dokumanlari incelenebilir
    :return:
    """

    function_kwargs = {
        "recipients": recipients,
        "sender": sender,
        "subject": subject,
        "content_text": content_text,
        "proje_id": proje_id,
    }
    function_kwargs.update(mail_params)
    tracker_info_params = {"proje_id": proje_id} if proje_id else {}
    tracker_info_params.update(function_kwargs)
    tracker_info_params.update(mail_params)
    email_job = {
        'func': mail_gonder,
        'kwargs': function_kwargs,
        'tracker_info': {
            'params': tracker_info_params,
            'triggered_by': current_user.id,
            'description': tracker_description,
            'job_type': JobTypes.email,
        }
    }
    email_job.update(scheduler_params)
    BaseJobHandler.add_jobs(email_job)
