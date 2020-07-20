"""Kullanici Profil"""

from flask_wtf import FlaskForm
from flask_babel import gettext as _
from wtforms import SelectField

from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif
from zopsedu.bap.models.siparis_takip import SiparisTakip
from zopsedu.lib.db import DB


class FirmaSelectForm(FlaskForm):
    """Kullanici Avatar Guncelleme Formu"""

    firma_select = SelectField(label='Firma Seçiniz', render_kw={'class': 'form-control'}, coerce=int)

    def __init__(self, satinalma_id,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.satinalma_id = satinalma_id

        firma_list = [(0, _("Lütfen firma seçiniz"))]

        firmalar = DB.session.query(BapFirma).\
            join(FirmaSatinalmaTeklif, FirmaSatinalmaTeklif.firma_id == BapFirma.id).\
            join(SiparisTakip, FirmaSatinalmaTeklif.id == SiparisTakip.kazanan_firma_teklif_id).\
            filter(FirmaSatinalmaTeklif.satinalma_id == self.satinalma_id).all()


        for firma in firmalar:
            firma_list.append((firma.id, firma.adi))

        self.firma_select.choices = firma_list
        self.firma_select.default = 0

