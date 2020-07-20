"""Proje Turu formu butce kismi"""
from wtforms import Form
from wtforms.validators import Optional
from wtforms.meta import DefaultMeta
from wtforms import SelectField, BooleanField, IntegerField
from zopsedu.bap.models.helpers import EkTalepTipi
from flask_babel import lazy_gettext as _

from zopsedu.lib.form.fields import HiddenIntegerField, HiddenStringField, ZopseduDecimalField
from zopsedu.lib.form.validators import LessThan, DecimalLength


class ButceKalemi(Form):
    """
    Proje Türü Bütçe Kalemleri Formu
    """

    class Meta(DefaultMeta):
        locales = ["tr"]

    gider_siniflandirma_id = HiddenIntegerField()
    secili_mi = BooleanField(default=False)
    butce_kalemi_adi = HiddenStringField()
    butce_alt_limiti = ZopseduDecimalField(validators=[
        Optional(),
        DecimalLength(max_length=10,
                      error_message="Min. Bütçe için en fazla "
                                    "10 haneli bir değer girebilirsiniz")
    ])
    butce_ust_limiti = ZopseduDecimalField(validators=[
        Optional(),
        DecimalLength(max_length=10,
                      error_message="Max. Bütçe için en fazla "
                                    "10 haneli bir değer girebilirsiniz")
    ])

    def validate_butce_alt_limiti(self, field):
        if self.secili_mi.data:
            LessThan("butce_ust_limiti",
                     message=_("Bütçe alt limiti bütçe üst limitinden"
                               " büyük olamaz.")).__call__(self, field)


class ProjeTuruButce(Form):
    # Proje türü formu Butce ayarlari Bölümü
    class Meta(DefaultMeta):
        locales = ["tr"]

    # proje butce limitleri
    butce_alt_limiti = ZopseduDecimalField(
        _("Bütçe alt limiti"),
        validators=[
            LessThan("butce_ust_limiti",
                     message=_(
                         "Bütçe alt limit değeri bütçe üst limit değerinden küçük olmalıdır")),
            DecimalLength(max_length=10,
                          error_message="Bütçe alt limiti için en fazla 10 "
                                        "haneli bir değer girebilirsiniz")
        ],
    )
    butce_ust_limiti = ZopseduDecimalField(_("Bütçe üst limiti"),
                                           validators=[
                                               DecimalLength(max_length=10,
                                                             error_message="Bütçe üst limiti için en fazla "
                                                                           "10 haneli bir değer girebilirsiniz")
                                           ]
                                           )
    # ek butce ile ilgili alanlar
    ek_butce_talep_tipi = SelectField(_("Ek Bütçe Talep Tipi"),
                                      choices=EkTalepTipi.choices(),
                                      default=EkTalepTipi.yok,
                                      coerce=EkTalepTipi.coerce)
    ek_butce_talep_degeri = IntegerField(_("Ek Bütçe Talep Değeri"), default=0)
    ek_butce_proje_butce_limitine_dahil_mi = BooleanField(
        _("Ek Butce Proje Butçe Limitine Dahil Mi ?"),
        default=False)

    kalemlere_ait_butce_yillara_gore_verilebilecek_mi = BooleanField(
        "Kalemlere ait bütçe yıllara göre verilebilecek mi?",
        default=False)

    # kalemlere_ait_kdv_girilsin_mi = BooleanField("Kalemlere ait kdv girilsin mi",
    #                                              default=False)
    # kalemlere_ait_butce_kodlari_girilsin_mi = BooleanField(
    #     _("Kalemlere ait bütçe kodlari girilsin mi ?"),
    #     default=False)
