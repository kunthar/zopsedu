"""
Routelar için permissionların tutulduğu dict.

permissin tuple şeklinde tutulur

dict key permission icin uniq olmalidir. Bunun için perm name kullanılır.

Example:
    tuple(perm,perm_group,id)

IMPORTANT: Yeni bir permission eklemeden permissionın daha önceden eklenip eklenmediğini kontrol ediniz

"""

permission_dict = {
    'bap': {
        'butce': {
            'avans_verilen_projeler_goruntuleme': ('Avans Verilen Projeler Görüntüleme', "BAP.Bütçe", 1000),
            'butce_kodlari_goruntuleme': ("Bütçe Kodları Görüntüleme", "BAP.Bütçe", 1001),
            'butce_kodlari_kaydetme': ("Bütçe Kodları Kaydetme", "BAP.Bütçe", 1002),
            'genel_butce_goruntuleme': ("Genel Bütçe Görüntüleme", "BAP.Bütçe", 1003),
            'kasa_olusturma': ("Kasa Oluşturma", "BAP.Bütçe", 1004),
            'kasa_girdileri_goruntuleme': ("Kasa Girdileri Görüntüleme", "BAP.Bütçe", 1005),
            'kasa_girdisi_ekleme': ("Kasaya Girdi Ekleme", "BAP.Bütçe", 1006),
            'kasa_girdisi_silme': ("Kasaya Girdi Silme", "BAP.Bütçe", 1007),
            'muhasebe_fisleri_goruntuleme': ("Muhasebe Fişleri Görüntüleme", "BAP.Bütçe", 1008),
            'strateji_teslim_listesi_goruntuleme': ("Strateji Teslim Listesi Görüntüleme", "BAP.Bütçe", 1009),
        },
        'firma': {
            'firma_anasayfa_goruntuleme': ("Firma Anasayfa Görüntüleme", "BAP.Firma", 1010),
            'satinalma_duyuru_listeleme': ("Satınalma Duyuru Listeleme", "BAP.Firma", 1011),
            'satinalmaya_teklif_yapma': ("Satınalmaya Teklif Yapma", "BAP.Firma", 1012),
            'satinalma_teklif_goruntuleme': ("Satınalma Teklif Görüntüleme", "BAP.Firma", 1013),
        },
        "hakem": {
            'hakem_listemele': ("Hakem Listeleme", "Yönetim.Hakem Yönetimi", 1014),
            'hakem_kayit_ekleme': ("Hakem Kaydı Ekleme", "Yönetim.Hakem Yönetimi", 1015),
            'hakem_kayit_duzenleme': ("Hakem Kaydı Düzenleme", "Yönetim.Hakem Yönetimi", 1016),
            'hakem_detay_goruntuleme': ("Hakem Detay Görüntüleme", "Yönetim.Hakem Yönetimi", 1017)

        },
        "hakem_dashboard": {
            'hakem_proje_degerlendirme': ("Hakem Proje Değerlendirme", "BAP.Hakem", 1018),
        },
        "proje": {
            "basvuru": {
                'proje_basvurusu_yapma': ("Proje Başvurusu Yapma", "BAP.Proje", 1019),
            },
            'dashboard': {
                'proje_ozeti_goruntuleme': ("Proje Özeti Görüntüleme", "BAP.Proje", 1020),
                'proje_sozlesmesi_yukleme': ("Proje Sözleşmesi Yükleme", "BAP.Proje", 1021),
                'proje_degerlendirme_goruntuleme': ('Proje Değerlendirme Görüntüleme', "BAP.Proje", 1023),
                'islem_gecmisi_goruntuleme': ("Proje İşlem Geçmişi Görüntüleme", "BAP.Proje", 1024),
                'proje_hakemleri_goruntuleme': ("Proje Hakemleri Görüntüleme", "BAP.Proje", 1025),
                'projeye_hakem_atama': ("Projeye Hakem Atama", "BAP.Proje", 1026),
                'proje_kararlari_goruntuleme': ("Proje Kararları Görüntüleme", "BAP.Proje", 1027),
                'proje_mesajlari_goruntuleme': ("Proje Mesajları Görüntüleme", "BAP.Proje", 1028),
                'proje_notlari_goruntuleme': ("Proje Notları Görüntüleme", "BAP.Proje", 1029),
                'proje_personelleri_goruntuleme': ("Proje Personelleri Görüntüleme", "BAP.Proje", 1030),
                'proje_raporlari_goruntuleme': ("Proje Raporları Görüntüleme", "BAP.Proje", 1031),
                'proje_raporlari_duzenleme': ("Proje Raporları Düzenleme", "BAP.Proje", 1032),
                'proje_raporlari_silme': ("Proje Raporları Silme", "BAP.Proje", 1033),
                'proje_sablon_ek_dosya_goruntuleme': ("Proje Şablon, Ek Dosya Görüntüleme", "BAP.Proje", 1034),
                'proje_satinalma_talepleri_goruntuleme': ("Proje Satınalma Talepleri Gorüntüleme", "BAP.Proje", 1035),
            },
            'hakem': {
                'projeye_hakem_onerme': ("Projeye Hakem Önerme", "BAP.Proje", 1036),
            },
            'proje_arama': {
                'eski_projeleri_arama': ("Eski Projeleri Arama", "BAP.Proje", 1037),
                'eski_projeleri_goruntuleme': ("Eski Projeleri Görüntüleme", "BAP.Proje", 1038),
                'projeleri_arama': ("Projeleri Arama", "BAP.Proje", 1039),
            },
            'proje_turu': {
                'proje_turu_yaratma_formu_goruntuleme': ("Proje Türü Yaratma Formu Görüntüleme", "BAP.Proje", 1040),
                'proje_turlerini_listeme': ("Proje Türlerini Listeleme", "BAP.Proje", 1041),
            }
        },
        'satinalma': {
            'satinalma_ozeti_goruntuleme': ("Satınalma Özeti Görüntüleme", "BAP.Satinalma", 1042),
            'satinalma_urun_listesi_goruntuleme': ("Satınalma Ürün Listesi Görüntüleme", "BAP.Satinalma", 1043),
            'satinalma_islem_gecmisi_goruntuleme': ("Satınalma İşlem Geçmişi Görüntüleme", "BAP.Satinalma", 1044),
            'avans_ile_alinan_malzemeler_listesi_goruntuleme': (
                "Avans ile Alınan Malzemeler Listesi Görüntüleme", "BAP.Satinalma", 1045),
            'avans_talepleri_listesi_goruntuleme': ("Avans Talepleri Listesi Görüntüleme", "BAP.Satinalma", 1046),
            'muayene_teslim_listesi_goruntuleme': ("Muayene Teslim Listesi Görüntüleme", "BAP.Satinalma", 1047),
            'satınalinan_malzemeler_listesi_goruntuleme': (
                "Satınalınan Malzemeler Listesi Görüntüleme", "BAP.Satinalma", 1048),
            'satınalma_talepleri_listesi_goruntuleme': (
                "Satınalma Talepleri Listesi Görüntüleme", "BAP.Satinalma", 1049),
            'teslimi_beklenen_firmalar_listesi_görüntüleme': (
                "Teslimi Beklenen Firmalar Listesi Görüntüleme", "BAP.Satinalma", 1051),
            'satinalma_firmalar_goruntuleme': ("Satınalma Firmalar Listesi Görüntüleme", "BAP.Satinalma", 1052),
            'satinalma_firma_teklif_kabul_etme': ("Satınalma Firma Teklifi Kabul Etme", "BAP.Satinalma", 1053),
            'satinalma_firma_teklif_silme': ("Satınalma Firma Teklifi Silme", "BAP.Satinalma", 1054),
            'satinalma_belgeleri_goruntuleme': ("Satınalma Belgeleri Görüntüleme", "BAP.Satinalma", 1062),
            'firma_tekliflerinin_teknik_sartnameye_uygunlugu': (
            "Firma Tekliflerinin Teknikşartnameye Uygunluğunu Belirleme", "BAP.Satinalma", 1063),
            'satinalma_muhasebe_fisi_goruntule': ("Satınalma Muhasebe Fişleri Görüntüle", "BAP.Satinalma", 1064),
            'satinalma_muhasebe_fisi_olustur': ("Satınalma Muhasebe Fişleri Oluşturma", "BAP.Satinalma", 1065),

        },
        'toplanti': {
            'toplanti_gundemi_listeleme': ("Toplantı Gündemi Listeleme", "BAP.Yönetim Kurulu", 1055),
            'toplanti_gundemi_guncelleme': ("Toplantı Gündemi Günceleme", "BAP.Yönetim Kurulu", 1056),
            'toplanti_kararlari_listesi_goruntuleme': (
                'Toplantı Kararları Listesi Görüntüleme', "BAP.Yönetim Kurulu", 1057),
            'toplanti_olusturma': ('Toplantı Oluşturma', "BAP.Yönetim Kurulu", 1058),
            'toplanti_guncelleme': ('Toplantı Güncelleme', "BAP.Yönetim Kurulu", 1059),
            'toplanti_silme': ('Toplantı Silme', "BAP.Yönetim Kurulu", 1060),
            'toplanti_listesi_goruntuleme': ("Toplantı Listesi Görüntüleme", "BAP.Yönetim Kurulu", 1061)
        }
    },
    'common': {
        'app': {
            'modal_filter': {
                'universite_arama': ("Üniversite Arama", "Genel", 2000),
                'birim_arama': ("Birim Arama", "Genel", 2001),
                'personel_arama': ("Personel Arama", "Genel", 2002),
                'person_arama': ("Kişi Arama", "Genel", 2003),
                'hakem_arama': ("Hakem Arama", "Genel", 2004),
                'ogrenci_arama': ("Öğrenci Arama", "Genel", 2005),
                'hitap_unvan_arama': ("Hitap Ünvan Arama", "Genel", 2006),
                'ogretim_uyesi_arama': ("Öğretim Üyesi Arama", "Genel", 2007),
                'vergi_dairesi_arama': ("Vergi Dairesi", "Genel", 2008),
                'belge_arama': ("Belge Arama", "Genel", 2009),
                'detayli_hesap_kodu_arama': ("Detaylı Hesap Kodu Arama", "Genel", 2011),
                'gelir_kasasi_arama': ("Gelir Kasası Arama", "Genel", 2013)
            },
            'sablon': {
                'sablon_onizleme': ("Şablon Önizleme", "Genel", 2010)
            }
        },
        'mesaj': {
            'gelen_kutusu_goruntuleme': ("Gelen Kutusu Görüntüleme", "Genel", 2012)
        }
    },
    'icerik': {
        'bap_duyuru': {
            'bap_duyuru_listeleme': ('BAP Duyuru Listeleme', "Yönetim.İçerik Yönetimi", 3000),
            'bap_duyuru_olusturma': ('BAP Duyuru Oluşturma', 'Yönetim.İçerik Yönetimi', 3001)
        }
    },
    'sistem_takibi': {
        'gonderilmis_epostalar': {
            'gonderilmis_epostalar_goruntuleme': ("Gönderilmiş E-postalar Görüntüleme", "Sistem Takibi", 4000)
        },
        'hata_loglari': {
            'hata_loglari_goruntuleme': ("Hata Logları Görüntüleme", "Sistem Takibi", 4001)
        },
        'aktivite_kaydi': {
            'aktivite_kayitlari_listeleme': ('Aktivite Kayitlarini Listeleme', "Sistem Takibi", 4002),
            'aktivite_kayit_gecmisi_detayi': ('Aktivite Kayit Geçmişi Detayı Görüntüleme', "Sistem Takibi", 4003),
        }
    },
    'yonetim': {
        'bap_yonetimi': {
            'diger_ayarlar': ("Diğer Ayarlar Yönetimi", "Yönetim.BAP Yönetimi", 5000),
            'gundem_sablonu_listeleme': ("Gündem Şablonu Listeleme", "Yönetim.BAP Yönetimi", 5002),
            'gundem_sablonu_ekleme': ("Gündem Şablonu Ekleme", "Yönetim.BAP Yönetimi", 5003),
            'gundem_sablonu_duzenleme': ("Gündem Şablonu Duzenleme", "Yönetim.BAP Yönetimi", 5004),
            'gundem_sablonu_silme': ("Gündem Şablonu Silme", "Yönetim.BAP Yönetimi", 5005),
            "hakem_ayarlari": ("Hakem Ayarları Yönetimi", "Yönetim.BAP Yönetimi", 5006),
            'otomasyon_ayarlari': ("Otomasyon Ayarları Yönetimi", "Yönetim.BAP Yönetimi", 5007),
            'sablon_ayarlari': ("Şablon Ayarları Yönetimi", "Yönetim.BAP Yönetimi", 5009),
            'ana_sayfa_ayarlari': ("Ana Sayfa Ayarları Yönetimi", "Yönetim.BAP Yönetimi",5010)
        },
        'firma_yonetimi': {
            'firma_listesi_goruntuleme': ("Firma Listesi Görümtüleme", "Yönetim.Firma Yönetimi", 5011),
            'firma_goruntuleme': ("Firma Görüntüleme", "Yönetim.Firma Yönetimi", 5012),
            'firma_guncelleme': ("Firma Güncelleme", "Yönetim.Firma Yönetimi", 5013),
            'firma_onaylama': ("Firma Onaylama", "Yönetim.Firma Yönetimi", 5014)
        },
        'personel_yonetimi': {
            'akademik_personel_listesi_goruntuleme': (
            "Akademik Personel Listesi Görüntüleme", "Yönetim.Personel Yönetimi", 5015),

            'akademik_personel_silme': ("Akademik Personel Silme", "Yönetim.Personel Yönetimi", 5016),
            'personel_durum_atama': ("Personel Durum Atama", "Yönetim.Personel Yönetimi", 5017),
            'idari_personel_listesi_goruntuleme': (
                "İdari Personel Listesi Görüntüleme", "Yönetim.Personel Yönetimi", 5020),
            'idari_personel_silme': ("İdari Personel Silme", "Yönetim.Personel Yönetimi", 5021),
        },
        'yetki_yonetimi': {
            'rol_atama': ("Rol Atama", "Yönetim.Rol Yönetimi", 5018),
            'rol_yetkilendirme': ("Rol Yetkilendirme", "Yönetim.Rol Yönetimi", 5019)
        }
    },
    'ebys': {
        'ebys_evrak_gonderimi': ("EBYS Evrak Gönderimi", "EBYS.EBYS Evrak Gönderimi", 6000),
        'ebys_takip_listesi_goruntuleme': ("EBYS Takip Listesi Görüntüleme", "EBYS.EBYS Takip", 6001),

    }
}
