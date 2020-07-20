"""Bap ayarlar diger Form Modulu"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, FormField, BooleanField, PasswordField

from zopsedu.lib.form.fields import SummerNoteField


# todo: form eklendi ama ekranda gosterilmedi. yayın islemleri baslayinca bu ayarlar yayın modulu ayarları altina tasınacak
class YayinAyarlariFormu(FlaskForm):
    sistemde_olmayan_projenin_yayinini_girebilsin_mi = BooleanField(_("Sistemde olmayan projenin yayını girilebilsin mi?"))
    eklenirken_email_gonderilsin_mi = BooleanField(_("Yayın eklenirken email gönderilsin mi?"))
    onaylanirken_email_gonderilsin_mi = BooleanField(_("Yayın onaylanırken email gönderilsin mi?"))
    proje_personelleri_mukerrer_yayin_yukleyebilir_mi = BooleanField(_("Proje personelleri mükerrer yayın yükleyebilsin mi?"))
    yayin_giris_uyarisi_gosterilsin_mi = BooleanField(_("Yayın girilirken uyarı gösterilsin mi?"))
    yayin_onaya_sunulsun_mu = BooleanField(_("Yayın onaya sunulsun mu?"))
    yayin_dilekcesi_gosterilsin_mi = BooleanField(_("Yayın dilekçesi gösterilsin mi?"))


# todo: form eklendi ama ekranda gosterilmedi. firma islemleri baslayinca bu ayarlar firma modulu ayarları altina tasınacak
class FirmaAyarlari(FlaskForm):
    teslimat_gecikme_emaili_gonderilsin_mi = BooleanField(_("Teslimat gecikme email gönderilsin mi?"))
    yoneticiye_teslimat_gecikme_emaili_gonderilsin_mi = BooleanField(_("Yöneticiye teslimat gecikme emaili gönderilsin mi?"))
    kabul_beyan_metni = SummerNoteField(_("Kabul beyan metni"))


class DigerAyarlarFormu(FlaskForm):
    tamamlanan_projelerde_yurutucu_gorunsun_mu = BooleanField(_("Tamamlanan projelerde yürütücü görünsün mü?"))
    # todo: mail kime gonderilecek? ogrenilince tooltip title icine yazilabilir
    proje_personel_ekleme_emaili_gonderilsin_mi = BooleanField(_("Proje personeli ekleme maili gönderilsin mi?"))
    # todo: mail kime gonderilecek? ogrenilince tooltip title icine yazilabilir
    proje_personel_cikartma_emaili_gonderilsin_mi = BooleanField(_("Proje personeli çıkartma maili gönderilsin mi?"))
    uyarilar_yurutucunun_ikincil_emailine_gonderilsin_mi = BooleanField(_("Uyarılar yürütücünün ikincil email adresine gönderilsin mi?"))
    # password alani encryptlenmeden konulamayacagi icin commente alinmistir
    # tubitak_dergileri_tesvik_sorgulama_username = StringField(_("TÜBİTAK dergileri teşvik sorguma kullanıcı adı"))
    # tubitak_dergileri_tesvik_sorgulama_password = PasswordField(_("TÜBİTAK dergileri teşvik sorguma kullanıcı parola"))


class DigerFormu(FlaskForm):
    yayinlar = FormField(YayinAyarlariFormu)
    firma = FormField(FirmaAyarlari)
    diger = FormField(DigerAyarlarFormu)
