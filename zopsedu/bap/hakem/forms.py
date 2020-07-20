"""Hakem Kayit ve Arama Formlari"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, validators, BooleanField
from flask_babel import gettext as _
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Length

from zopsedu.models.helpers import BirimTipiEnum
from zopsedu.personel.models.hakem import HakemTuru
from zopsedu.lib.form.fields import Select2Field

HAKEM = [(tur.name, tur.value) for tur in HakemTuru]


class HakemSearchForm(FlaskForm):
    """Proje Arama Formu"""
    ad = StringField(label=_('Adı'), validators=[Length(max=50)])
    soyad = StringField(label=_('Soyadı'), validators=[Length(max=50)])
    bolum = Select2Field(label=_('Bölüm'), url='/select/bolum')
    kurum_ici_option = SelectField(label='Kurum İçi',
                                   choices=[('0', 'Hepsi'), ('1', 'Kurum İçi'),
                                            ('2', 'Kurum Dışı')], default=0)

    choice = HakemTuru.choices()
    choice = [('0', 'Hepsi')] + choice

    hakem_turu_option = SelectField(label='Hakem Türü', choices=choice, default=0)

    def validate(self):
        if not any([self.ad.data,
                    self.soyad.data]):
            return False
        return True


class KurumIciHakemKayitForm(FlaskForm):
    """Proje Kayit Formu"""
    personel_sec = Select2Field(label=_('Adı Soyadı'), validators=[
        validators.DataRequired(message=_('Bu alan boş bırakılamaz.'))], url='/select/personel')

    kurum_ici_hakem_turu = SelectField(label=_('Hakem Türü'),
                                       choices=HAKEM)


class KurumDisiHakemKayitForm(FlaskForm):
    """Proje Kayit Formu"""

    ad = StringField(label=_('Adı'), validators=[Length(max=50)])
    soyad = StringField(label=_('Soyadı'), validators=[Length(max=50)])
    universitede_gorev_almayan = BooleanField(
        label=_('Herhangi bir üniversitede görev almayan hakem ekle'),
        default=False)

    kurum = StringField(label='Kurum', validators=[Length(max=120)])
    daire = StringField(label='Daire', validators=[Length(max=120)])
    birim = StringField(label='Birim', validators=[Length(max=120)])

    universite = Select2Field(_('Üniversite Seç'),
                              url="/select/birim",
                              placeholder=_("Üniversite"),
                              node_name="fakulte_parent",
                              birim_tipi=BirimTipiEnum.universite.value,
                              kurum_ici=False)

    fakulte = Select2Field(_('Fakülte Seç'), url="/select/birim",
                           placeholder=_("Fakülte"),
                           dependent="fakulte_parent",
                           node_name="bolum_parent",
                           birim_tipi=BirimTipiEnum.fakulte.value,
                           kurum_ici=False)

    bolum = Select2Field(_('Bölüm Seç'),
                         url="/select/birim",
                         placeholder=_("Bölüm"),
                         dependent="bolum_parent",
                         birim_tipi=BirimTipiEnum.bolum.value,
                         kurum_ici=False)

    unvan = Select2Field(label=_('Ünvan'),
                         validators=[
                             DataRequired(
                                 message=_("Ünvan boş bırakılamaz"))
                         ],
                         url='/select/hitap_unvan')

    email = EmailField('E-posta',
                       validators=[DataRequired(message=_('E-posta alanı boş bırakılamaz')),
                                   Email(message='Bir email adresi girmelisiniz'), Length(max=80)])

    hakem_turu = SelectField(label=_('Hakem Türü'),
                             choices=HAKEM)
