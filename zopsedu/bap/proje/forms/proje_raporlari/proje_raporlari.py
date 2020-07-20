"""Bap Projelerinin Raporlarini Filtrelemek icin kullanilir"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, FormField
from flask_babel import gettext as _
from zopsedu.bap.models.proje_rapor import ProjeRaporTipi
from zopsedu.lib.form.fields import CustomFileField, HiddenIntegerField, SummerNoteField, MultiFileField, BooleanField


# class ProjeRaporFiltrelemeForm(FlaskForm):
#     """Proje Rapor Filtreleme Formu"""
#     rapor_tipi = SelectField(label=_('Rapor Tipi'),
#                              choices=[(rapor.name, rapor.value) for rapor in ProjeRaporTipi])
#     temizle = SubmitField(label=_('Temizle'))
#     submit = SubmitField(label=_('Ara'))


# class ProjeRaporDuzenleForm(FlaskForm):
#     """Proje Rapor Duzenleme Formu"""
#     yeni_rapor = CustomFileField(label=_('Yükleyeceğiniz yeni raporu seçiniz: '))
#     rapor_file_id = HiddenIntegerField()
#     yukle = SubmitField(label=_('Yükle'))


class RaporForm(FlaskForm):
    information = [
        _("Lütfen rapor metnini doldurunuz."),
        _("Rapor için ek dosya yükleyebilirsiniz"),
        _("Raporu tamamla seçeneğini işaretlerseniz daha sonra düzenleyemezsiniz.(Düzenleyebilmek "
          "için yetkili ile iletişime geçmeniz gerekir.)")
    ]
    rapor_metni = SummerNoteField(_("Rapor Metni"))
    rapor_dosya = MultiFileField("Rapor Dosya")
    tamamlandi_mi = BooleanField(_("Raporu Tamamla"))


# class ProjeRaporEkleForm(FlaskForm):
#     """Proje Rapor Ekleme Formu"""
#     rapor_tipi = SelectField(label=_('Rapor Tipi'),
#                              choices=[(rapor.name, rapor.value) for rapor in ProjeRaporTipi if not ProjeRaporTipi.proje_basvuru])
#     rapor = FormField(RaporForm)


# class ProjeRaporDuzenlenebilirForm(FlaskForm):
#     """Proje raporunun duzenlebilirligi"""
#
#     rapor_duzenlenebilir_mi = SelectField(label=_('Rapor düzenlenmeye açılsın mı? '),
#                                           choices=[(1, 'Evet'), (0, 'Hayır')])
#     duzenlenebilir_rapor_file_id = HiddenIntegerField()
#     kaydet = SubmitField(label=_('Kaydet'))


