"""
Yök özgecmis servislerinin ve bu servislere iliskin tuketilecek parametrelerin tutuldugu modul

"""
from collections import namedtuple

YokOzgecmisServiceParameters = namedtuple("YokOzgecmisParameters", ["service_response_data_name",
                                                                    "model_name",
                                                                    "data_id_name"])

"""
    Dict icerisindeki key ler yok ozgecmis servis methodlarini temsil eder
    Dict value ise servisleri tüketirken kullanilacak parametleri temsil eder
    Ornegin 'getirAkademikGorevListesi' akademisyenin akademik gorev listesini donduren servis
    Bu servis responsunda verinin bulundugu parametrenin ismi 'AkademikGorevListesi'
    Verinin kaydedilecegi model ismi 'YoksisAkademikGorev'
    GOREV_ID ise gelen verirnin id sini temsil eder(Aynı veriyi tekrar kaydetmemek icin yapilmasi 
    gereken kontrol icin gerekli)
        
"""
YOK_OZGECMIS_SERVICE_PARAMETERS = {
    "getirAkademikGorevListesi": YokOzgecmisServiceParameters("AkademikGorevListesi",
                                                              "YoksisAkademikGorev",
                                                              "GOREV_ID"),
    "getTesvikBasvuruVarmiV1": YokOzgecmisServiceParameters("basvuruDurumu",
                                                            "YoksisTesvikBasvuru",
                                                            "BASVURU_ID"),
    "getTesvikFaaliyetBeyanV1": YokOzgecmisServiceParameters("tesvikBeyanListesi",
                                                             "YoksisTesvikBeyan",
                                                             "FB_ID"),
    "getArastirmaSertifkaBilgisiV1": YokOzgecmisServiceParameters("arastirmaListe",
                                                                  "YoksisArastirmaSertifikaBilgisi",
                                                                  "S_ID"),
    "getirUnvDisiDeneyimListesi": YokOzgecmisServiceParameters("deneyimListesi",
                                                               "YoksisUniDisiDeneyim",
                                                               "DENEYIM_ID"),
    "getirDersListesi": YokOzgecmisServiceParameters("dersListesi",
                                                     "YoksisDers",
                                                     "DERS_ID"),
    "getEditorlukBilgisiV1": YokOzgecmisServiceParameters("editorlukListe",
                                                          "YoksisEditorlukBilgisi",
                                                          "YAYIN_ID"),  # ilgili verinin id bu mu ?
    "getirIdariGorevListesi": YokOzgecmisServiceParameters("idariGorevListesi",
                                                           "YoksisIdariGorev",
                                                           "IDGOR_ID"),
    "getKitapBilgisiV1": YokOzgecmisServiceParameters("kitapListe",
                                                      "YoksisKitap",
                                                      "YAYIN_ID"),  # ilgili verinin id bu mu ?
    "getMakaleBilgisiV1": YokOzgecmisServiceParameters("makaleListe",
                                                       "YoksisMakale",
                                                       "YAYIN_ID"),  # ilgili verinin id bu mu ?
    "getOdulListesiV1": YokOzgecmisServiceParameters("odulListesi",
                                                     "YoksisOdul",
                                                     "ODUL_ID"),
    "getirOgrenimBilgisiListesi": YokOzgecmisServiceParameters("OgrenimBilgisiListesi",
                                                               "YoksisOgrenimBilgisi",
                                                               "ID"),
    "getPatentBilgisiV1": YokOzgecmisServiceParameters("patentListe",
                                                       "YoksisPatent",
                                                       "PATENT_ID"),
    "getirProjeListesi": YokOzgecmisServiceParameters("projeListesi",
                                                      "YoksisProje",
                                                      "PROJE_ID"),
    "getTasarimBilgisiV1": YokOzgecmisServiceParameters("tasarimListe",
                                                        "YoksisTasarimBilgisi",
                                                        "P_TASARIM_ID"),
    "getTemelAlanBilgisiV1": YokOzgecmisServiceParameters("temelAlanListe",
                                                          "YoksisTemelAlanBilgisi",
                                                          "T_UAK_ID"),
    "getirTezDanismanListesi": YokOzgecmisServiceParameters("tezDanismanListesi",
                                                            "YoksisYonetilenTez",
                                                            "KAYIT_ID"),  # ilgili verinin id bu mu ?
    "getirUyelikListesi": YokOzgecmisServiceParameters("uyelikListesi",
                                                       "YoksisUyelik",
                                                       "UYELIK_ID"),
    "getirYabanciDilListesi": YokOzgecmisServiceParameters("yabanciDilListesi",
                                                           "YoksisYabanciDil",
                                                           "Y_ID"),
    "getYazarListesiV1": YokOzgecmisServiceParameters("yazarlarListesi",
                                                      "YoksisYazar",
                                                      "Y_ID"),
    "getPersonelLinkV1": YokOzgecmisServiceParameters("personelLinkListe",
                                                      "YoksisBirlikteCalistigiKisi",
                                                      "ARASTIRMACI_ID"),  # Uniq field bulunamadi
    "getSanatsalFaalV1": YokOzgecmisServiceParameters("sanatsalFaalListe",
                                                      "YoksisSanatsalFaaliyet",
                                                      "S_ID"),
    "getHakemlikBilgisiV1": YokOzgecmisServiceParameters("hakemlikListe",
                                                         "YoksisHakemlikBilgisi",
                                                         "YAYIN_ID"),  # Uniq field bulunamadi
    "getBildiriBilgisiV1": YokOzgecmisServiceParameters("bildiriListe",
                                                        "YoksisBildiri",
                                                        "YAYIN_ID"),  # ilgili verinin id bu mu ?
    "getAtifSayilariV1": YokOzgecmisServiceParameters("atifSayiListesi",
                                                      "YoksisAtifSayisi",
                                                      "A_ID"),
}
