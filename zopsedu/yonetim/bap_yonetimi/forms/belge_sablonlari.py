"""Belge Sablonlari form"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import SelectField, FileField, StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length

from zopsedu.lib.db import DB
from zopsedu.lib.form.validators import FileExtensionRestriction
from zopsedu.lib.helpers import SABLON_FILE_EXTENTIONS
from zopsedu.models import SablonTipi


class VarsayilanSablonYuklemeForm(FlaskForm):
    """Sablon Tipleri için varsayilan YuklemeForm"""
    file_extention_uyari_mesaji = _("İzin verilen dosya uzantıları: {}".format(
        '%s' % ', '.join(SABLON_FILE_EXTENTIONS.keys())))
    form_description = [
        _("Şablon için şablon metni girebilirsiniz veya dosya yükleyebilirsiniz(İkisini beraber kaydedemezsiniz)"),
        _("Lütfen şablon tipi ve dosya yüklerken dikkat ediniz. Daha sonra bu alanları güncellemeniz mümkün değildir."),
        _(
            "Şablon ismini ve kullanılabilirlik şeçeneğini şablon listesinde bulunan güncelle alanı aracılıgıyla güncelleyebilirsiniz"),
        _("Şablon query fonksiyonu seçerken fonksiyonun argümanlarına dikkat ediniz."),
        file_extention_uyari_mesaji
    ]

    sablon_tipi_id = SelectField(label=_("Sablon Tipi"), coerce=int)
    sablon_adi = StringField(label=_("Şablon Adı"), validators=[
        DataRequired(message=_("Şablon adi alanı boş bırakılamaz")), Length(max=255)
    ])
    sablon_kullanilabilir_mi = BooleanField(label=_("Kullanılabilir mi?"), default=False)

    sablon_ebys_icin_kullanibilir_mi = BooleanField(label=_("EBYS Sisteminde Kullanılabilir mi?"), default=False)

    sablon_text = TextAreaField(_("Şablon Metni"), render_kw={"cols": 20, "rows": 20})
    sablon_dosya = FileField(label=_("Dosya Yükle"), validators=[
        FileExtensionRestriction(allowed_extentions=SABLON_FILE_EXTENTIONS,
                                 error_message=file_extention_uyari_mesaji)])
    query_helper_id = SelectField(label=_("Query Fonksiyonları"), coerce=int)


class SablonSearchForm(FlaskForm):
    kullanilabilir_mi = SelectField(label=_('Kulllanilabilir mi?'), choices=[(0, 'Tümü'), (1, 'Evet'), (2, 'Hayır')],
                                    default=0, coerce=int)
    sablon_tipi = SelectField(label=_('Şablon Tipi'), coerce=int)
    sablon_adi = StringField(label=_('Şablon adı'), validators=[Length(max=255)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sablon_tipleri = DB.session.query(SablonTipi).all()

        sablon_tipi_list = [(0, _("Tümü"))]

        for sablon_tipi in sablon_tipleri:
            sablon_tipi_list.append((sablon_tipi.id, sablon_tipi.adi))

        self.sablon_tipi.choices = sablon_tipi_list
        self.sablon_tipi.default = 0
