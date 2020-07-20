from flask_wtf import FlaskForm
from flask_babel import gettext as _

from wtforms import StringField, IntegerField


class EbysAyarlari(FlaskForm):
    """
    Ebys kullanici bilgileri formu
    """
    p_user_id = IntegerField(label=_('Kullanıcı Id'), default=0)
    p_token = StringField(label=_("Servis Token"))
    docdefid = IntegerField(label="Doküman Tanım Id", default=0)
    integration_url = StringField(label=_("Integration Url"))
    system_integration_url = StringField(label=_("System Integration Url"))
