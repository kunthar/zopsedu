from flask_wtf import FlaskForm
from flask_babel import gettext as _

from zopsedu.lib.form.fields import Select2Field


class AnasayfaFormu(FlaskForm):
    proje_ara = Select2Field(label=_('Proje Ara'),
                             url='')
    makine_ara = Select2Field(label=_('Makine/Teçhizat Ara'),
                              url='')
