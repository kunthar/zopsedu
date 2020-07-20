"""Satinalma dashboard firmalar bolumu formlari"""
from flask_wtf import FlaskForm
from flask_babel import gettext as _


class FirmalarBolumuInformation(FlaskForm):
    """
    Firmalar bolumu "firma teklifleri", "kabul edilen teklifler" ve "genel" sekmeleri icin
    kullaniciya bilgi verir
    """

    kabul_edilen_teklifler_information = [
        _("Kabul edilen firma teklifleri aşağıda listelenmiştir."),
        _("Kabul edilen teklifi sil butonunu kullanarak iptal edebilir firma teklifleri "
          "kısmından başka bir teklif kabul edebilirsiniz.")
    ]

    # satinalma dashboard firma teklifleri kismi uyari mesajlari
    firma_teklifleri_information = [
        _("Firma teklifleri aşağıda listelenmiştir."),
        _("İşlemler bölümünden teknik şartname uygunluğunu belirleyebilir ve firma "
          "teklifini kabul edebilirsiniz "),
        _("Teknik şartnameye uygun olmayan teklifleri kabul edemezsiniz.")
    ]

    genel_uyari_mesajlari = [
        _("Satınalma firma teklifleri ile alakalı işlemleri bu sayfadan yapabilirsiniz."),
        _("Bu sayfadaki işlemler yalnız ST6(Satınalma duyurusu tamamlandı) durumunda yapılabilir."),
        _("ST7 Durumuna geçtiğinizde teklik kabul/ret işlemleri yapamazsınız."),
        _("Lütfen uyarıları dikkate alınız.")
    ]
