from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, validators, TextAreaField, StringField
from flask_babel import lazy_gettext as _

from zopsedu.lib.helpers import WTFormEnum


class GorunurlukSecenekleri(str, WTFormEnum):
    """
    "proje_personelini_bilgileri_gorunurlugu" alanı için olusturulmuş enum sınıf
    """
    personel_bilgilerini_goremez = _("Proje personellerinin bilgilerini göremez")
    yurutucu_dahil_tum_personeli_gorebilir = _("Yürütücü dahil tüm personeli görebilir")


class HakemlikIptalSecenekleri(str, WTFormEnum):
    """
    "hakemlik_iptal_durumu" alanı için olusturulmuş enum sınıf
    """
    uyari_sonrasi_hakem_islem_yapamasin = _("Uyarı sonrası hakem işlem yapamasın")
    uyari_sonrasi_hakem_islem_yapabilsin = _("Uyarı sonrası hakem işlem yapabilsin")


class SureBirimleri(str, WTFormEnum):
    saat = _("Saat")
    gun = _("Gün")
    hafta = _("Hafta")
    ay = _("Ay")


class EtikKurallarHangiTurdeGorunurSecenekleri(str, WTFormEnum):
    """
    "etik_kurallar_hangi_turde_gorunur" alanı için olusturulmuş enum sınıf
    """
    proje_basvurusu = _("Proje Başvurusu")


class HakemForm(FlaskForm):
    proje_personeli_bilgileri_gorunurlugu = SelectField(
        _("Personel bilgi görünürlüğü"),
        choices=GorunurlukSecenekleri.choices(),
        default=GorunurlukSecenekleri.personel_bilgilerini_goremez,
        coerce=GorunurlukSecenekleri.coerce,
        render_kw={"class": "form-control"})

    beklenen_yanitlama_suresi = IntegerField(_("Beklenen yanıtlama süresi"), validators=[
        validators.DataRequired(message=_("Lütfen beklenen yanıtlama süresini giriniz.")),
        validators.NumberRange(min=0,
                               message=_("Beklenen yanıtlama süresi pozitif bir sayı olmalıdır."))])

    beklenen_yanitlama_suresi_birim = SelectField(
        _("Sürenin etki birimi"),
        choices=SureBirimleri.choices(),
        default=SureBirimleri.gun,
        coerce=SureBirimleri.coerce,
        render_kw={"class": "form-control"})

    onceden_uyarma = IntegerField(_("Önceden uyarma süresi"), validators=[
        validators.DataRequired(message=_("Lütfen önceden uyarma süresini giriniz.")),
        validators.NumberRange(min=0,
                               message=_("Önceden uyarma süresi pozitif bir sayı olmalıdır."))])

    onceden_uyarma_birim = SelectField(
        _("Sürenin etki birimi"),
        choices=SureBirimleri.choices(),
        default=SureBirimleri.gun,
        coerce=SureBirimleri.coerce,
        render_kw={"class": "form-control"})

    gecikme_uyarma_suresi = IntegerField(
        _("Gecikme uyarma süresi"), validators=[
            validators.DataRequired(message=_("Lütfen gecikme uyarma süresini giriniz.")),
            validators.NumberRange(min=0,
                                   message=_("Gecikme durumunda uyarma "
                                             "süresi pozitif bir sayı olmalıdır."))])

    gecikme_uyarma_suresi_birim = SelectField(
        _("Sürenin etki birimi"),
        choices=SureBirimleri.choices(),
        default=SureBirimleri.gun,
        coerce=SureBirimleri.coerce,
        render_kw={"class": "form-control"})

    gecikme_uyari_tekrar_suresi = IntegerField(
        _("Uyarı tekrar süresi", default=0), validators=[
            validators.DataRequired(message=_("Lütfen uyarı tekrar süresini giriniz.")),
            validators.NumberRange(min=0,
                                   message=_("Uyarı tekrar süresi pozitif bir sayı olmalıdır."))])

    gecikme_uyari_tekrar_suresi_birim = SelectField(
        _("Sürenin etki birimi"),
        choices=SureBirimleri.choices(),
        default=SureBirimleri.gun,
        coerce=SureBirimleri.coerce,
        render_kw={"class": "form-control"})

    hakemlik_iptal_durumu = SelectField(
        _("Hakemlik İptal Durumu"),
        choices=HakemlikIptalSecenekleri.choices(),
        default=HakemlikIptalSecenekleri.uyari_sonrasi_hakem_islem_yapamasin,
        coerce=HakemlikIptalSecenekleri.coerce,
        render_kw={"class": "form-control"})

