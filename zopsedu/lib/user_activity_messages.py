"""
User activity messages kullanicilarin activitylerinden dogan mesajlarin tek bir noktadan
kontrol edilmesi icin olusturulmustur.Blueprintlere göre gruplandirilarak mesajlar eklenmistir.

"""
from collections import namedtuple
from flask_babel import gettext as _

UserActivity = namedtuple("UserActivity", ["type_index", "message"])

USER_ACTIVITY_MESSAGES = {
    "auth": {
        "login": UserActivity(1000, _("Kullanıcı sisteme giriş yaptı")),
        "logout": UserActivity(1001, _("Kullanıcı sistemden çıkış yaptı")),
        "signup": UserActivity(1002, _("Kullanıcı kaydı yapıldı"))
    },
    "ayarlar": {
        "ayar_guncelle": UserActivity(2000, _("Otomasyon ayarları güncellendi")),
        "bap_sms_guncelle": UserActivity(2001, _("Bap sms ayarları güncellendi")),
        "bap_proje_guncelle": UserActivity(2002, _("Bap proje ayarları güncellendi")),
        "bap_sablon_kaydet": UserActivity(2003, _("Bap şablon kaydet")),
        "bap_sablon_guncelle": UserActivity(2004, _("Bap şablon güncellendi")),
        "bap_email_guncelle": UserActivity(2005, _("Bap email ayarları güncellendi")),
        "bap_hakem_guncelle": UserActivity(2006, _("Bap hakem ayarları güncellendi")),
    },
    "bap": {
        "kisi_ekle": UserActivity(3000, _("Sisteme yeni bir kişi eklendi")),
        "personel_hakem_yap": UserActivity(3001, _("Personel hakem yapıldı")),
        "person_hakem_yap": UserActivity(3002, _("Kişi hakem yapıldı")),
        "hakem_duzenle": UserActivity(3003, _("Hakem düzenlendi")),
        "hakem_atama": UserActivity(3004, _("Projeye hakem ataması yapıldı")),
        "hakem_atama_sil": UserActivity(3005, _("Hakem proje hakemlerinden cıkarıldı")),
        "gundem_sablon_ekle": UserActivity(3006, _("Gündem şablonu kaydedildi")),
        "gundem_sablon_guncelle": UserActivity(3007, _("Gündem şablonu güncellendi")),
        "gundem_sablon_sil": UserActivity(3008, _("Gündem şablonu güncellendi")),
        "proje_degerlendirdi": UserActivity(3009, _("Hakem proje değerlendirdi")),
        "degerlendirme_teklifi_cevaplandi": UserActivity(3010, _(
            "Hakem proje değerlendirme teklifini cevapladı")),
        "oe_hakem_onerildi": UserActivity(3011, _("Öğretim elemanı hakem olarak önerildi")),
        "kisi_hakem_onerildi": UserActivity(3012, _("Kişi hakem olarak önerildi")),
        "hakem_onerisi_kaldirildi": UserActivity(3013, _("Kişi hakem önerilerinden çıkarıldı")),
        "proje_basvuru_basla": UserActivity(3014, _("Proje başvurusu işlemine başlandı")),
        "proje_basvuru_tamamla": UserActivity(3015, _("Proje başvurusu tamamlandı")),
        "proje_basvuru_guncelle": UserActivity(3016, _("Proje başvurusu güncellendi")),
        "projeye_arastirmaci_eklendi": UserActivity(3017, _("Projeye araştırmacı çalışan eklendi")),
        "projeye_bursiyer_eklendi": UserActivity(3018, _("Projeye bursiyer çalışan eklendi")),
        "projeye_harici_arastirmaci_eklendi": UserActivity(3019,
                                                           _("Projeye bursiyer çalışan eklendi")),
        "proje_calisani_sil": UserActivity(3020, _("Proje çalışanı silindi")),
        "proje_calisan_guncelle": UserActivity(3021, _("Proje çalışanı güncellendi")),
        "proje_eki_indirildi": UserActivity(3022, _("Proje eki indirildi")),
        "proje_durumu_degistirildi": UserActivity(3023, _("Proje durumu degiştirildi")),
        "proje_turu_versiyonla": UserActivity(3024, _("Proje türü versiyonlandı")),
        "proje_turu_olusturuldu": UserActivity(3025, _("Proje türü oluşturuldu")),
        "proje_turu_taslak_kaydet": UserActivity(3026, _("Proje türü taslağı kaydedildi")),
        "proje_turu_taslak_guncelle": UserActivity(3027, _("Proje türü taslağı güncellendi")),
        "proje_turu_guncelle": UserActivity(3028, _("Proje türü güncellendi")),
        "proje_raporu_indir": UserActivity(3029, _("Proje raporu indirildi")),
        "proje_rapor_dosyasi_sil": UserActivity(3030, _("Proje rapor dosyası silindi")),
        "proje_raporu_guncellendi": UserActivity(3031, _("Proje raporu güncellendi")),
        "proje_raporu_duzenlenebilir": UserActivity(3032, _("Proje raporu düzenlenebilir yapıldı")),
        "proje_raporu_eklendi": UserActivity(3033, _("Proje raporu eklendi")),
        "toplanti_gundem_cikar": UserActivity(3034, _("Gündem toplantı gündemlerinden çıkarıldı")),
        "proje_durum_degisimi": UserActivity(3035, _("Proje Durum Degişimi")),
        "proje_islem": UserActivity(3036, _("Proje işlemi yapıldı")),
        "rapor_hakeme_gonderildi": UserActivity(3037, _(
            "Proje raporu değerlendirilmesi için hakeme gönderildi")),
        "kasa_olusturuldu": UserActivity(3038, _("Kasa Oluşturuldu")),
        "kasa_girdi_ekle": UserActivity(3039, _("Kasaya Girdi Eklendi")),
        "kasa_girdi_sil": UserActivity(3040, _("Kasa Girdisi Silindi")),
        "butce_kodlari_kaydet": UserActivity(3041, _("Bütçe Kodları Kaydet")),
        "satinalma_durum_degisimi": UserActivity(3042, _("Satinalma durumu degiştirildi")),
        "firma_kaydet": UserActivity(3043, _("Firma Kaydı Oluşturuldu")),
        "firma_onay": UserActivity(3044, _("Firma Onaylandı")),
        "firma_red": UserActivity(3045, _("Firma Reddedildi")),
        "satinalma_talebi_olustur": UserActivity(3046, _("Satınalma Talebi Oluşturuldu")),
        "teknik_sartname_duzenle": UserActivity(3047, _("Satınalma Talep Kalemi Teknik Şartnamesi Düzenlendi")),
        "firma_teklifi_kabul_edildi": UserActivity(3048, _("Firma Teklifi Kabul Edildi")),
        "kabul_edilen_firma_teklifi_silindi": UserActivity(3049, _("Kabul Edilen Firma Teklifi Silindi")),
        "firma_teklif_teknik_sartname_degerlendirmesi": UserActivity(3050, _(
            "Firma teklifinin teknik şartname uygunluk durumu değiştirildi")),
        "proje_revizyonu_tamamlandi": UserActivity(3051, _("Proje revizyonu tamamlandı")),
        "proje_sozlesmesi_yuklendi": UserActivity(3052, _("Proje Sözleşmesi Yüklendi")),
        "kabul_edilen_proje_butcesi_belirlendi": UserActivity(3053, _("Proje Kabul Edilen Bütçesi Belirlendi")),
        "muhasebe_fisi_olusturuldu": UserActivity(3054, _("Muhasebe Fisi Oluşturuldu")),
        "satinalma_islemi": UserActivity(3055, _("Satınalma İşlemi Yapıldı")),
        "firma_satinalma_teklifi_yapti": UserActivity(3056, _("Firma Satınalma Teklifi Yaptı")),
    },
    "toplanti": {
        "toplanti_olustur": UserActivity(4000, _("Toplantı oluşturuldu")),
        "toplanti_sil": UserActivity(4001, _("Toplantı silindi")),
        "gundem_guncelle": UserActivity(4002, _("Toplantı gündemi güncellendi")),
        "gundem_sira_degistir": UserActivity(4003, _("Toplantı gündem sıra numarası degiştirildi")),
        "gundem_ekle": UserActivity(4004, _("Toplantı gündemi oluşuturuldu")),
        "toplanti_gundem_cikar": UserActivity(4005, _("Toplantı gündemi çıkarıldı")),
        "toplanti_sonuclandirildi": UserActivity(4006, _("Toplantı sonuçlandırıldı")),
        "toplu_gundem_olusturuldu": UserActivity(4007, _("Toplu gündem oluşturuldu")),
        "toplanti_katilimcilari_duzenlendi": UserActivity(4008, _("Toplantı katılımcıları düzenlendi")),
    },
    "common": {
        "dosya_sil": UserActivity(5000, _("Dosya silindi")),
        "dosya_yuklendi": UserActivity(5001, _("Dosya yüklendi")),
        "profil_fotograf_guncelle": UserActivity(5002, _("Profil fotoğrafı güncellendi")),
        "parola_degisikligi": UserActivity(5003, _("Kullanıcı parola değiştirdi")),
        "hatali_parola": UserActivity(5004, _(
            "Kullanıcı parolasını değiştirmek isterken hatalı parola girdi")),
        "parola_degistirirken_hata": UserActivity(5005, _(
            "Kullanıcı parola değiştirmeye çalışırken bir hata meydana geldi")),
        "gecerli_rol_degistir": UserActivity(5006, _("Kullanıcı geçerli rolünü degiştirdi")),
        "mesaj_okundu": UserActivity(5007, _("Kullanıcı mesaj okudu")),
        "mesaj_sildi": UserActivity(5008, _("Kullanıcı mesaj sildi")),
        "mesaj_ek_indir": UserActivity(5009, _("Kullanıcı mesaj sildi")),
        "ozgecmis_kaydet": UserActivity(5010, _("Kullanıcı özgeçmiş kaydetti")),
        "harici_profil_guncelle": UserActivity(5011, _(
            "Harici Öğretim Üyesi Profil Bilgilerini Güncelledi")),
        "gundem_ek_indir": UserActivity(5012, _("Gundem Ek Dosya İndirildi")),
    },
    "icerik": {
        "bap_duyuru_guncelle": UserActivity(6000, _("Bap duyurusu güncellendi")),
        "bap_duyuru_sil": UserActivity(6001, _("Bap duyurusu silindi")),
        "bap_duyuru_olustur": UserActivity(6002, _("Bap duyurusu oluşturuldu")),
        'satinalma_duyurusu_duzenlendi': UserActivity(6003, _("Satınalma duyurusu düzenlendi"))
    },
    "yonetim": {
        "yeni_rol_ekle": UserActivity(7000, _("Yeni Rol Eklendi")),
        "rol_guncelle": UserActivity(7001, _("Rol Güncellendi")),
        "rol_sil": UserActivity(7002, _("Rol Silindi")),
        "personel_durumu_belirle": (UserActivity(7003, _("Personel Durumu Güncellendi"))),
        "idari_personel_ekle": (UserActivity(7004, _("İdari Personel Eklendi"))),
        "idari_personel_sil": (UserActivity(7005, _("İdari Personel Çıkarıldı"))),
        "faaliyet_raporu_eklendi": (UserActivity(7006, _("Faaliyet Raporu Eklendi"))),
        "formlar_ve_belgeler_eklendi": (UserActivity(7007, _("Formlar ve Belgeler Eklendi"))),
        "mevzuat_eklendi": (UserActivity(7008, _("Mevzuat Eklendi"))),
        "bap_hakkinda_metni_eklendi": (UserActivity(7009, _("BAP Hakkında Metni Eklendi"))),
        "bap_belge_silindi": (UserActivity(7010, _("BAP Belge Silindi"))),

    },
    "ebys": {
        "ebys_evrak_gonder": UserActivity(8000, _("EBYS evrakı gönderildi")),
    }
}
