"""Yoksis view methodlarini icerir"""
from flask import render_template, redirect, url_for, current_app
from flask_classful import FlaskView, route
from sqlalchemy.orm import lazyload, contains_eager

from zopsedu.auth.models.auth import User
from zopsedu.lib.db import DB
from zopsedu.models import Person, OgretimElemani, Personel, Birim
from zopsedu.personel.models.unvan import HitapUnvan


class YoksisView(FlaskView):
    """Yoksis akademisyen bilgileri ile alakali view methodlari"""
    excluded_methods = [
        "get_base_query",
        "invalid_email_adress_strategy"
    ]

    @staticmethod
    def get_base_query(email):
        """
        Akademik personel ozgecmis bilgileri sayfalarinda kullanilmak uzere getirilecek temel queryi
        icerir.
        Gelen email prefixine gore ozgecmis bilgileri olan ilgili emaile sahip ogretim elemanini
        filtreler
        :return: BaseQuery object
        """
        ogretim_elemani_query = DB.session.query(
            OgretimElemani,
            Person.ad.label("ou_ad"),
            Person.soyad.label("ou_soyad"),
            Birim.uzun_ad.label("birim"),
            User.avatar.label("avatar"),
            HitapUnvan.ad.label("ou_hitap_unvan_ad"),
        ).join(
            Personel, OgretimElemani.personel_id == Personel.id
        ).join(
            Birim, Birim.id == Personel.birim
        ).join(
            Person, Personel.person_id == Person.id
        ).join(
            User, Person.user_id == User.id
        ).join(
            HitapUnvan, HitapUnvan.id == OgretimElemani.unvan
        ).options(
            lazyload(OgretimElemani.hitap_unvan),
            lazyload(OgretimElemani.personel),
            lazyload(OgretimElemani.person),
        ).filter(
            Person.birincil_eposta.ilike("{}@%".format(email)),
            OgretimElemani.yok_ozgecmis_bilgileri_var_mi == True
        )
        return ogretim_elemani_query

    @staticmethod
    def invalid_email_adress_strategy():
        return redirect(url_for("anasayfa.BapAnasayfaView:bap_anasayfa"))

    def get_personel_data(self, ogretim_elemani_verileri):
        return {
            "personel_ad_soyad": "{} {} {}".format(ogretim_elemani_verileri[0].ou_hitap_unvan_ad,
                                                   ogretim_elemani_verileri[0].ou_ad,
                                                   ogretim_elemani_verileri[0].ou_soyad),
            "birim": ogretim_elemani_verileri[0].birim,
            "avatar": current_app.wsgi_app.url_for(ogretim_elemani_verileri[0].avatar) if
            ogretim_elemani_verileri[0].avatar else None

        }

    @route('/<string:email>/egitim-bilgileri', methods=['GET'])
    def get_egitim_bilgileri(self, email):
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.join(
            OgretimElemani.akademik_gorevler
        ).join(
            OgretimElemani.ogrenim_bilgileri
        ).options(
            # contains_eager(OgretimElemani.akademik_gorevler),
            contains_eager(OgretimElemani.ogrenim_bilgileri)
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        ogrenim_verisi = {
            "ogrenim_bilgisi": [],
            "tezleri": []
        }
        for ogrenim_bilgisi in ogretim_elemani_verileri[0][0].ogrenim_bilgileri:
            tarih = "{} - {}".format(ogrenim_bilgisi.BASTAR1, ogrenim_bilgisi.BITTAR1)
            ogrenim_verisi["ogrenim_bilgisi"].append(
                "{}".format(", ".join(filter(None, [ogrenim_bilgisi.PROGRAM_ADI,
                                                    ogrenim_bilgisi.UNV_BIRIM_ADI,
                                                    ogrenim_bilgisi.AKADEMIK_BIRIM_ADI, tarih])))
            )
            ogrenim_verisi["tezleri"].append(
                "{}".format(", ".join(filter(None,
                                             [ogrenim_bilgisi.PROGRAM_ADI, ogrenim_bilgisi.TEZ_ADI,
                                              ogrenim_bilgisi.UNV_BIRIM_ADI,
                                              ogrenim_bilgisi.AKADEMIK_BIRIM_ADI,
                                              ogrenim_bilgisi.TEZ_BIT_TAR])))
            )

        data = self.get_personel_data(ogretim_elemani_verileri)
        data.update(ogrenim_verisi)

        return render_template("ozgecmis_sayfalari/egitim_bilgileri.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)

    @route('/<string:email>/mesleki-deneyim', methods=['GET'])
    def get_mesleki_deneyim(self, email):
        # todo: verdigi dersler ve juri uyelikleri eklenecek
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.outerjoin(
            OgretimElemani.akademik_gorevler
        ).outerjoin(
            OgretimElemani.yonettigi_tezler
        ).outerjoin(
            OgretimElemani.idari_gorevleri
        ).outerjoin(
            OgretimElemani.dersleri
        ).outerjoin(
            OgretimElemani.uni_disi_deneyimleri
        ).options(
            contains_eager(OgretimElemani.akademik_gorevler),
            contains_eager(OgretimElemani.yonettigi_tezler),
            contains_eager(OgretimElemani.idari_gorevleri),
            contains_eager(OgretimElemani.dersleri),
            contains_eager(OgretimElemani.uni_disi_deneyimleri),
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        mesleki_deneyim_verisi = {
            "akademik_unvanlar_gorevler": [],
            "yonettigi_tezleri": [],
            "idari_gorevler": [],
            "dersler": [],
            "uni_disi_deneyimler": []
        }
        for yonettigi_tez in ogretim_elemani_verileri[0][0].yonettigi_tezler:
            tez_sahibi = "{} {}".format(yonettigi_tez.YAZAR_ADI, yonettigi_tez.YAZAR_SOYADI)
            mesleki_deneyim_verisi["yonettigi_tezleri"].append(
                "{}".format(", ".join(filter(None, [yonettigi_tez.TUR_ADI,
                                                    tez_sahibi,
                                                    yonettigi_tez.TEZ_ADI,
                                                    yonettigi_tez.UNIVERSITE_AD,
                                                    yonettigi_tez.ENSTITU_AD,
                                                    yonettigi_tez.ABD_AD,
                                                    yonettigi_tez.YIL])))
            )

        for idari_gorev in ogretim_elemani_verileri[0][0].idari_gorevleri:
            tarih = "{} - {}".format(idari_gorev.BAS_TAR,
                                     idari_gorev.BIT_TAR if idari_gorev.BIT_TAR else "Devam Ediyor")
            mesleki_deneyim_verisi["idari_gorevler"].append(
                "{}".format(", ".join(filter(None, [idari_gorev.GOREV_ADI,
                                                    idari_gorev.UNV_BIRIM_ADI,
                                                    idari_gorev.FAKULTEMYOENST,
                                                    tarih])))
            )

        for akademik_gorev in ogretim_elemani_verileri[0][0].akademik_gorevler:
            tarih = "{} - {}".format(akademik_gorev.BASTAR1,
                                     akademik_gorev.BITTAR1 if akademik_gorev.BITTAR1 else "Devam Ediyor")
            mesleki_deneyim_verisi["akademik_unvanlar_gorevler"].append(
                "{}".format(", ".join(filter(None, [akademik_gorev.KADRO_UNVAN_ADI,
                                                    akademik_gorev.UNIV_BIRIM_ADI,
                                                    akademik_gorev.FAKULTEBILGISI,
                                                    tarih])))
            )

        for uni_disi_deneyim in ogretim_elemani_verileri[0][0].uni_disi_deneyimleri:
            tarih = "{} - {}".format(uni_disi_deneyim.BAS_TAR if uni_disi_deneyim.BAS_TAR else "",
                                     uni_disi_deneyim.BIT_TAR if uni_disi_deneyim.BIT_TAR else "")
            mesleki_deneyim_verisi["uni_disi_deneyimler"].append(
                "{}".format(", ".join(filter(None, [uni_disi_deneyim.GOREV_ADI,
                                                    uni_disi_deneyim.KURULUS_ADI,
                                                    uni_disi_deneyim.IS_TANIMI,
                                                    uni_disi_deneyim.ISYERI_TUR_AD,
                                                    tarih])))
            )

        for ders in ogretim_elemani_verileri[0][0].dersleri:
            mesleki_deneyim_verisi["dersler"].append(
                "{}".format(", ".join(filter(None, [ders.DERS_ADI,
                                                    ders.OGRENIM_ADI,
                                                    ders.AKADEMIK_YIL,
                                                    ders.DIL_ADI,
                                                    ])))
            )

        for akademik_gorev in ogretim_elemani_verileri[0][0].akademik_gorevler:
            tarih = "{} - {}".format(akademik_gorev.BASTAR1,
                                     akademik_gorev.BITTAR1 if akademik_gorev.BITTAR1 else "Devam Ediyor")
            mesleki_deneyim_verisi["akademik_unvanlar_gorevler"].append(
                "{}".format(", ".join(filter(None, [akademik_gorev.KADRO_UNVAN_ADI,
                                                    akademik_gorev.UNIV_BIRIM_ADI,
                                                    akademik_gorev.FAKULTEBILGISI,
                                                    tarih])))
            )

        data = self.get_personel_data(ogretim_elemani_verileri)
        data.update(mesleki_deneyim_verisi)

        return render_template("ozgecmis_sayfalari/mesleki_deneyim.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)

    @route('/<string:email>/basarilar', methods=['GET'])
    def get_basari_taninirlik(self, email):
        # todo: google arastirmaci indexleri eklenecek
        # todo: veri gelince atiflar eklenecek
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.outerjoin(
            OgretimElemani.odulleri
        ).outerjoin(
            OgretimElemani.arasirma_sertifika_bilgileri
        ).options(
            contains_eager(OgretimElemani.odulleri),
            contains_eager(OgretimElemani.arasirma_sertifika_bilgileri)
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        ogrenim_verisi = {
            "odulleri": [],
            "sertifika_calistay_kurs": []
        }
        for odul in ogretim_elemani_verileri[0][0].odulleri:
            ogrenim_verisi["odulleri"].append(
                "{}".format(", ".join(filter(None, [odul.ODUL_ADI,
                                                    odul.KURULUS_ADI,
                                                    odul.ISYERI_TURU_ADI,
                                                    odul.ULKE_AD,
                                                    odul.ODUL_TARIH,
                                                    ])))
            )

        for arastirma_sertifika in ogretim_elemani_verileri[0][0].arasirma_sertifika_bilgileri:
            ogrenim_verisi["sertifika_calistay_kurs"].append(
                "{}".format(", ".join(filter(None, [arastirma_sertifika.ADI,
                                                    arastirma_sertifika.ICERIK,
                                                    arastirma_sertifika.TUR_ADI,
                                                    arastirma_sertifika.KAPSAM_AD,
                                                    arastirma_sertifika.YER,
                                                    arastirma_sertifika.ULKE_SEHIR
                                                    ])))
            )

        data = self.get_personel_data(ogretim_elemani_verileri)
        data.update(ogrenim_verisi)

        return render_template("ozgecmis_sayfalari/basari_taninirlik.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)

    @route('/<string:email>/proje-patent', methods=['GET'])
    def get_proje_patent(self, email):
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.join(
            OgretimElemani.projeleri
        ).join(
            OgretimElemani.patentleri
        ).options(
            contains_eager(OgretimElemani.projeleri),
            contains_eager(OgretimElemani.patentleri),
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        mesleki_deneyim_verisi = {
            "projeler": [],
            "patentler": [],
        }
        for proje in ogretim_elemani_verileri[0][0].projeleri:
            tarih = "{} - {}".format(proje.BAS_TAR if proje.BAS_TAR else "",
                                     proje.BIT_TAR if proje.BIT_TAR else "")
            mesleki_deneyim_verisi["projeler"].append(
                "{}".format(", ".join(filter(None, [proje.PROJE_AD,
                                                    proje.PROJE_TURU_AD,
                                                    proje.PROJE_KONUMU_AD,
                                                    proje.KAPSAM_AD,
                                                    proje.PROJE_DURUMU_AD,
                                                    tarih])))
            )

        for patent in ogretim_elemani_verileri[0][0].patentleri:
            mesleki_deneyim_verisi["patentler"].append(
                "{}".format(", ".join(filter(None, [patent.PATENT_ADI,
                                                    patent.PATENT_NO,
                                                    patent.BASVURU_SAHIPLERI,
                                                    patent.BULUS_SAHIPLERI,
                                                    patent.DOSYA_TIPI,
                                                    patent.KATEGORI,
                                                    patent.KAPSAM])))
            )

        data = self.get_personel_data(ogretim_elemani_verileri)
        data.update(mesleki_deneyim_verisi)

        return render_template("ozgecmis_sayfalari/proje_patent.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)

    @route('/<string:email>/kimlik-iletisim', methods=['GET'])
    def get_kimlik_iletisim(self, email):
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.add_columns(
            Person.birincil_eposta.label("birincil_eposta"),
            Person.ikincil_eposta.label("ikincil_eposta"),
            Personel.oda_tel_no.label("oda_tel_no"),
            Personel.oda_no.label("oda_no"),
            Personel.web_sitesi.label("web_sitesi"),
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        data = {
            "unvan": ogretim_elemani_verileri[0].ou_hitap_unvan_ad,
            "oda_no": ogretim_elemani_verileri[0].oda_no,
            "birincil_eposta": ogretim_elemani_verileri[0].birincil_eposta,
            "ikincil_eposta": ogretim_elemani_verileri[0].ikincil_eposta,
            "oda_tel_no": ogretim_elemani_verileri[0].oda_tel_no,
            "web_sitesi": ogretim_elemani_verileri[0].web_sitesi,
            "personel_ad_soyad": "{} {} {}".format(ogretim_elemani_verileri[0].ou_hitap_unvan_ad,
                                                   ogretim_elemani_verileri[0].ou_ad,
                                                   ogretim_elemani_verileri[0].ou_soyad),
            "birim": ogretim_elemani_verileri[0].birim,
            "avatar": current_app.wsgi_app.url_for(ogretim_elemani_verileri[0].avatar) if
            ogretim_elemani_verileri[0].avatar else None

        }

        return render_template("ozgecmis_sayfalari/kimlik_bilgileri_iletisim.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)

    @route('/<string:email>/makale-kitap-bildiri', methods=['GET'])
    def get_yayin_bildiri_makele(self, email):
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.outerjoin(
            OgretimElemani.makaleleri
        ).outerjoin(
            OgretimElemani.bildirileri
        ).outerjoin(
            OgretimElemani.kitaplari
        ).options(
            contains_eager(OgretimElemani.makaleleri),
            contains_eager(OgretimElemani.bildirileri),
            contains_eager(OgretimElemani.kitaplari),
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        makale_bildiri_kitap_verisi = {
            "makale_sci": [],
            "makale_diger": [],
            "kitaplari": [],
            "bildirileri": []
        }
        for makale in ogretim_elemani_verileri[0][0].makaleleri:
            makale_sayfa_sayilari = "{} {} {}".format(
                "{}{}".format("vol.", makale.CILT) if makale.CILT else "",
                "{}{}".format("no.", makale.SAYI) if makale.SAYI else "",
                "p.{}-{}".format(makale.ILK_SAYFA if makale.ILK_SAYFA else " ",
                                 makale.SON_SAYFA if makale.SON_SAYFA else " "),
            )
            doi_link = ""
            link = ""
            if makale.DOI:
                doi_link = "<a href='{}{}' style='color: darkred;'>(DOI)</a>".format(
                    "https://doi.org/", makale.DOI)
            if makale.ERISIM_LINKI:
                link = "<a href='{}' style='color: orangered;'>(Link)</a>".format(
                    makale.ERISIM_LINKI)
            makale_verisi = ("{}".format(", ".join(filter(None, [makale.YAZAR_ADI,
                                                                 makale.MAKALE_ADI,
                                                                 makale.DERGI_ADI,
                                                                 makale_sayfa_sayilari,
                                                                 makale.YIL,
                                                                 makale.KAPSAM_AD,
                                                                 makale.HAKEM_TUR_AD,
                                                                 makale.ENDEKS,
                                                                 makale.MAKALE_TURU_AD]))),
                             doi_link,
                             link
                             )
            # 40 --> SCI, 6 --> SCI-Expanded
            # todo: AHCI indexi eklenmesi lazim veri bulunmadigi icin eklenemedi
            if makale.ENDEKS_ID == "40" or makale.ENDEKS_ID == "6":
                makale_bildiri_kitap_verisi["makale_sci"].append(makale_verisi)
            else:
                makale_bildiri_kitap_verisi["makale_diger"].append(makale_verisi)

        for bildiri in ogretim_elemani_verileri[0][0].bildirileri:
            etkinlik_tarih = "{} - {}".format(bildiri.ETKINLIK_BAS_TARIHI,
                                              bildiri.ETKINLIK_BIT_TARIHI)
            makale_bildiri_kitap_verisi["bildirileri"].append(
                "{}".format(", ".join(filter(None, [bildiri.YAZAR_ADI,
                                                    bildiri.BILDIRI_ADI,
                                                    bildiri.ETKINLIK_ADI,
                                                    etkinlik_tarih,
                                                    bildiri.KAPSAM_AD,
                                                    bildiri.SEHIR,
                                                    bildiri.ULKE_ADI])))
            )

        # todo: veri olunca kitap bolumu duzenlenecek.
        for kitap in ogretim_elemani_verileri[0][0].kitaplari:
            makale_bildiri_kitap_verisi["kitaplari"].append(
                "{}".format(", ".join(filter(None, [kitap.YAZAR_ADI,
                                                    kitap.KITAP_ADI,
                                                    kitap.YAYIN_EVI,
                                                    kitap.EDITOR_ADI,
                                                    kitap.KACINCI_BASIM,
                                                    kitap.SAYFA_SAYISI,
                                                    kitap.YIL,
                                                    kitap.ISBN])))
            )

        data = self.get_personel_data(ogretim_elemani_verileri)
        data.update(makale_bildiri_kitap_verisi)

        return render_template("ozgecmis_sayfalari/yayinlar_eserler.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)

    @route('/<string:email>/bilimsel-faaliyet', methods=['GET'])
    def get_bilimsel_faaliyetler(self, email):
        query = self.get_base_query(email)

        ogretim_elemani_verileri = query.outerjoin(
            OgretimElemani.hakemlikleri
        ).outerjoin(
            OgretimElemani.uyelikleri
        ).outerjoin(
            OgretimElemani.editorlukleri
        ).options(
            contains_eager(OgretimElemani.hakemlikleri),
            contains_eager(OgretimElemani.uyelikleri),
            contains_eager(OgretimElemani.editorlukleri),
        ).all()

        if not ogretim_elemani_verileri:
            return self.invalid_email_adress_strategy()

        bilimsel_faaliyetler = {
            "editorlukleri": [],
            "uyelikleri": [],
            "hakemlikleri": [],
        }

        for hakemlik in ogretim_elemani_verileri[0][0].hakemlikleri:
            bilimsel_faaliyetler["hakemlikleri"].append(
                "{}".format(", ".join(filter(None, [hakemlik.YAYIN_YERI,
                                                    hakemlik.HAKEMLIK_TURU_AD,
                                                    hakemlik.ENDEKS,
                                                    hakemlik.KAPSAM_AD,
                                                    hakemlik.SEHIR,
                                                    hakemlik.ULKE_ADI,
                                                    hakemlik.YIL])))
            )

        for editorluk in ogretim_elemani_verileri[0][0].editorlukleri:
            doi_link = ""
            link = ""
            if editorluk.DOI:
                doi_link = "<a href='{}{}' style='color: darkred;'>(DOI)</a>".format(
                    "https://doi.org/", editorluk.DOI)
            if editorluk.ERISIM_LINKI:
                link = "<a href='{}' style='color: orangered;'>(Link)</a>".format(
                    editorluk.ERISIM_LINKI)
            tarih = "{} - {}".format(editorluk.BAS_TARIH if editorluk.BAS_TARIH else "",
                                     editorluk.BIT_TARIH if editorluk.BIT_TARIH else "")
            bilimsel_faaliyetler["editorlukleri"].append(
                ("{}".format(", ".join(filter(None, [editorluk.YAYIN_ADI,
                                                     editorluk.EDITORLUK_TUR_AD,
                                                     editorluk.EDITOR_GOREV_AD,
                                                     editorluk.SEHIR,
                                                     editorluk.ULKE,
                                                     tarih]))),
                 doi_link,
                 link)
            )

        for uyelik in ogretim_elemani_verileri[0][0].uyelikleri:
            tarih = "{} - {}".format(uyelik.BAS_TAR if uyelik.BAS_TAR else "",
                                     uyelik.BIT_TAR if uyelik.BIT_TAR else "")
            bilimsel_faaliyetler["uyelikleri"].append(
                "{}".format(", ".join(filter(None, [uyelik.KURULUS_ADI,
                                                    uyelik.UYELIK_DURUMU_AD,
                                                    uyelik.KURULUS_TURU_AD,
                                                    tarih])))
            )

        data = self.get_personel_data(ogretim_elemani_verileri)
        data.update(bilimsel_faaliyetler)

        return render_template("ozgecmis_sayfalari/bilimsel_faaliyetler.html",
                               ozgecmis_bilgileri=data,
                               email_prefix=email)
