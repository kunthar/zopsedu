from flask_wtf import FlaskForm
from flask_babel import gettext as _

from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

from zopsedu.lib.form.fields import Select2Field
from zopsedu.models.helpers import BapIdariUnvan


class AkademikPersonelSearchForm(FlaskForm):
    ad = StringField("Adı")
    soyad = StringField("Soyadı")

    unvan_id = Select2Field(label=_('Ünvan'),
                            url='/select/hitap_unvan')

    durumu = SelectField(label='Kullanıcı Durumu',
                         choices=[('-1', 'Tümü'), ('1', 'Aktif'), ('0', 'Pasif')], default=-1)

    # fakulte_id = Select2Field(_('Fakülte Seç'),
    #                           url="/select/birim",
    #                           placeholder=_("Fakülte"),
    #                           node_name="proje_bolum_parent",
    #                           birim_tipi=BirimTipiEnum.fakulte.value,
    #                           kurum_ici=True)
    #
    # bolum_id = Select2Field(_('Bölüm Seç'), url="/select/birim",
    #                         placeholder=_("Bölüm"),
    #                         dependent="proje_bolum_parent",
    #                         node_name="proje_anabilim_dali_parent",
    #                         birim_tipi=BirimTipiEnum.bolum.value,
    #                         kurum_ici=True)

    def validate(self):
        if any([self.ad.data,
                self.soyad.data,
                self.unvan_id.data
                # self.fakulte_id.data,
                # self.bolum_id.data
                ]):
            return True
        return False


class IdariPersonelSearchForm(FlaskForm):
    ad = StringField("Adı")
    soyad = StringField("Soyadı")

    unvan_id = Select2Field(label=_('Ünvan'),
                            url='/select/hitap_unvan')

    durumu = SelectField(label='Kullanıcı Durumu',
                         choices=[('-1', 'Tümü'), ('1', 'Aktif'), ('0', 'Pasif')], default=-1)

    choice = BapIdariUnvan.choices()
    choice = [('0', 'Hepsi')] + choice
    gorevi = SelectField(label='Görevi', choices=choice, default=0)

    def validate(self):
        if any([self.ad.data,
                self.soyad.data,
                self.unvan_id.data
                ]):
            return True
        return False


class IdariPersonelEkle(FlaskForm):
    personel_id = Select2Field(label=_('Personel Seç'), url='/select/personel',
                               validators=[DataRequired(message=_('Bu alan boş bırakılamaz.'))])
    gorevi = SelectField(label='Görevi', choices=BapIdariUnvan.choices(), coerce=BapIdariUnvan.coerce)
    gorev_aciklamasi = StringField("Görev Açıklaması", validators=[Length(max=255)])


class PersonelDurumForm(FlaskForm):
    durum_listesi = SelectField(label='Seçilebilecek kullanıcı durumu: ',
                                choices=[(1, 'Aktif'), (0, 'Pasif')])
    kaydet = SubmitField(label='Durumu Kaydet')
