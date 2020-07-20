from flask import Blueprint, render_template, current_app, url_for
from flask_babel import gettext as _
from flask_login import login_required
from flask_mail import Message, Attachment

from zopsedu.lib.db import DB
from zopsedu.lib.mail import send_mail_with_template
from zopsedu.models import SiteAyarlari

mail_sending_blueprint = Blueprint(
    'mail',
    __name__,
    template_folder='templates', )


@mail_sending_blueprint.route('/', methods=['GET'])
@login_required
def index():
    """
    Message(subject='', recipients=None, body=None, html=None, sender=None, cc=None, bcc=None,
    attachments=None, reply_to=None, date=None, charset=None, extra_headers=None, mail_options=None,
     rcpt_options=None)
    """

    """Development configinde default olarak emailler supress edilmistir."""

    body = """
        Bu ornek bir maildir.!!
    """

    html = render_template('ornek_mail.html', title="Zopsedu ornek mail", name="Zopsedu")

    msg = Message('Subject', recipients=['example@zopsedu.net'], body=body,
                  # cc=['example2@zopsedu.net']
                  )

    # msg.bcc = ['example3@zopsedu.net', 'example4@zopsedu.net']

    # Eger sender elle verilmezse configte belirtilen default sender kullanilir
    msg.sender = 'example@zopsedu.net'

    # url_for sonucunda '/static/assets/img/brand-logo2.png' stringi geliyor. ancak open_resource
    #  ile birlikte kullanilirken bastaki slash in '/' olmamasi gerekli

    file_to_send = url_for('static', filename='assets/img/brand-logo2.png').replace('/', '',
                                                                                    count=1)
    # with current_app.open_resource('static/assets/img/brand-logo2.png') as fp:
    with current_app.open_resource(file_to_send) as fp:
        msg.attach(filename="image.png", content_type="image/png", data=fp.read())

    msg.html = html

    current_app.extensions['mail'].send(msg)

    return '200'


@mail_sending_blueprint.route('/template_ping', methods=['GET'])
@login_required
def template_ping():
    """
    Message(subject='', recipients=None, body=None, html=None, sender=None, cc=None, bcc=None,
    attachments=None, reply_to=None, date=None, charset=None, extra_headers=None, mail_options=None,
     rcpt_options=None)
    """

    """Development configinde default olarak emailler supress edilmistir."""

    attachments = []

    with current_app.open_resource('static/assets/img/brand-logo2.png') as fp:
        attachments.append(Attachment(filename="image.png",
                                      content_type="image/png", data=fp.read()))

    html = send_mail_with_template(recipients=['example@zopsedu.net'],
                                   subject=_("Ornek mail"),
                                   template='email_template_ping.html',
                                   logo_text=_("Zopsedu"),
                                   title_text=_("Ornek Mail"),
                                   greeting=_("Merhaba"),
                                   greeting_name="Zopsedu",
                                   content_text="Lorem ipsum dolor sit amet, consectetur "
                                                "adipiscing elit. Curabitur et nisi vehicula, "
                                                "convallis dolor sed, pulvinar odio. Vestibulum "
                                                "fermentum faucibus sapien vestibulum "
                                                "consectetur. Etiam non blandit diam, "
                                                "non fermentum neque. "
                                                "Donec fringilla eget arcu in sagittis. Vestibulum "
                                                "ante ipsum primis in faucibus orci "
                                                "luctus et ultrices posuere ",
                                   button_href="http://v2.zopsedu.net",
                                   button_text="Zopsedu",
                                   content_end_text="Sevgilerle, <br>Zopsedu",
                                   attachments=attachments
                                   )

    return html
