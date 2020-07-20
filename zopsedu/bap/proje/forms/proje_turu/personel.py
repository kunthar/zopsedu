"""Proje Turu formu personel kismi"""
from wtforms import Form
from wtforms import SelectField, BooleanField, IntegerField
from flask_babel import lazy_gettext as _

from zopsedu.lib.form.validators import LessThan
from zopsedu.bap.models.helpers import YardimciArastirmaciSecenekleri


class ProjeTuruPersonel(Form):
    # Proje türü Formu Personel ayarlari bölümü
    yardimci_arastirmaci_secenekleri = SelectField(
        _("Yardımcı Araştırmacı Seçenekleri"),
        choices=YardimciArastirmaciSecenekleri.choices(),
        default=YardimciArastirmaciSecenekleri.sadece_danisman_ve_tez_ogrencisi,
        coerce=YardimciArastirmaciSecenekleri.coerce)

    yardimci_arastirmaci_alt_limiti = IntegerField(_("Yardımcı Araştırmacı Alt Limiti"), default=0)
    yardimci_arastirmaci_ust_limiti = IntegerField(_("Yardımcı Araştırmacı Üst Limiti"), default=0)

    ozgecmis_yuklenmesi_zorunlu_mu = BooleanField(_("Özgeçmiş Yüklemek Zorunlu Mu?"),
                                                  default=False)
    dosya_olarak_ozgecmis_yuklenebilir_mi = BooleanField(
        _("Dosya Olarak Özgeçmiş Yüklenebilir Mi ?"),
        default=False)
    banka_bilgilerini_girmek_zorunlu_mu = BooleanField(
        _("Başvuru Sırasında Banka Bilgilerini Girmek Zorunlu Mu ?"),
        default=False)

    def validate_yardimci_arastirmaci_alt_limiti(self, field):
        """
        Eğer yardimci_arastirmaci_senecekleri degiskeninin degeri Sınırlı olarak secilirse bu
        validasyon uygulanır
        :param field:
        :return:
        """
        if self.yardimci_arastirmaci_secenekleri.data == YardimciArastirmaciSecenekleri.sinirli:
            LessThan("yardimci_arastirmaci_ust_limiti",
                     message=_("Yardımcı araştırmacı alt limit değeri "
                               "yardımcı araştırmacı üst limitinden küçük olmalıdır")
                     ).__call__(self, field)
