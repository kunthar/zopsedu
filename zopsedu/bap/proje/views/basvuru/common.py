"""Proje Basvuru Kaydet ve Taslak için gerekli ortak methodlar tutulur"""
from copy import deepcopy

from flask_babel import gettext as _
from flask import flash, request
from wtforms import FormField
from sqlalchemy.orm import joinedload

from zopsedu.lib.db import DB
from zopsedu.models import EkDosya, ButceKalemi, ProjeTuru, ProjeCalisanlari, OgretimElemani, File, \
    ProjeBelgeleri, Ozgecmis, ProjeKalemi
from zopsedu.bap.proje.forms.basvuru.butce import ButceKalemiFormu, ProjeButceFormWizardForm
from zopsedu.bap.proje.forms.basvuru.basvuru import BAPProjeBasvuruFormu
from zopsedu.bap.models.helpers import ButceTercihleri, YardimciArastirmaciSecenekleri, \
    ProjeSuresiBirimi


def personel_proje_calisani_mi(proje_id, personel_id):
    """Personel id si verilen kisinin projecalisanlarina kayitli olup olmadigini kontrol eder."""
    calisan = DB.session.query(ProjeCalisanlari.id).filter(
        ProjeCalisanlari.personel_id == personel_id,
        ProjeCalisanlari.proje_id == proje_id).scalar()
    return calisan is not None


# pylint: disable=invalid-name
def get_proje_turu_with_related_field(proje_turu_id, guncel_mi=True):
    """
    Proje türünü related modelleri ile birlikte getiren query
    guncel_mi parametresi gecilirse guncel_mi true filtresi yapilacak
    """
    proje_turu_query = DB.session.query(ProjeTuru).options(
        joinedload(ProjeTuru.butce),
        joinedload(ProjeTuru.cikti),
        joinedload(ProjeTuru.personel_ayarlari),
        joinedload(ProjeTuru.ek_dosyalar).joinedload(EkDosya.belge),
        joinedload(ProjeTuru.butce_kalemleri).joinedload(ButceKalemi.gider_siniflandirma_kalemi)
    ).filter_by(id=proje_turu_id)
    if guncel_mi:
        proje_turu_query = proje_turu_query.filter_by(guncel_mi=guncel_mi)
    return proje_turu_query.first()


def proje_turu_to_dict(proje_turu):
    """
    Proje türü instance ini dict e cevirir
    Args:
        proje_turu: proje türü objesi

    Returns:
        proje_turu_dict(): proje türü dict

    """
    personel_ayarlari_dict = {}
    butce_dict = {}

    proje_turu_dict = proje_turu.to_dict()
    if proje_turu.butce:
        butce_dict = proje_turu.butce.to_dict()
        butce_dict.pop("id")
        butce_dict.pop("proje_turu_id")

    if proje_turu.personel_ayarlari:
        personel_ayarlari_dict = proje_turu.personel_ayarlari.to_dict()
        personel_ayarlari_dict.pop("id")
        personel_ayarlari_dict.pop("proje_turu_id")

    ek_dosyalar = []
    for ek_dosya in proje_turu.ek_dosyalar:
        ek_dosyalar.append({
            "ek_dosya_id": ek_dosya.id,
            "zorunlu_mu": ek_dosya.zorunlu_mu,
            "proje_icerik_dosyasi_mi": ek_dosya.proje_icerik_dosyasi_mi,
            "belgenin_ciktisi_alinacak_mi": ek_dosya.belgenin_ciktisi_alinacak_mi,
            "belge": {
                "adi": ek_dosya.belge.adi,
                "aciklama": ek_dosya.belge.aciklama,
                "turler": ek_dosya.belge.turler,
                "file_id": ek_dosya.belge.file_id
            }
        })
    butce_kalemleri = []
    for butce_kalemi in proje_turu.butce_kalemleri:
        butce_kalemleri.append(
            {"butce_kalemi_id": butce_kalemi.id,
             "gider_siniflandirma_id": butce_kalemi.gider_siniflandirma_id,
             "butce_kalemi_adi": "{} {}".format(
                 butce_kalemi.gider_siniflandirma_kalemi.kodu,
                 butce_kalemi.gider_siniflandirma_kalemi.aciklama),
             "butce_alt_limiti": butce_kalemi.butce_alt_limiti,
             "butce_ust_limiti": butce_kalemi.butce_ust_limiti})
    proje_turu_dict.update(butce_dict)
    proje_turu_dict.update(personel_ayarlari_dict)
    proje_turu_dict['ek_dosyalar'] = ek_dosyalar
    proje_turu_dict['butce_kalemleri'] = butce_kalemleri
    return proje_turu_dict


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def basvuru_formu_restriction(proje_turu_dict, initial_form_data=None, **kwargs):
    """
    proje basvuru formunu proje türüne göre filtreler
    Args:
        proje_turu_dict: proje türü data
        initial_form_data:

    Returns:

    """

    class ModifiedBAPProjeBasvuruFormu(BAPProjeBasvuruFormu):
        """
        ProjeBasvuruFormunu modifiye edebilmemiz icin olusturulmus subclasss
        """
        pass

    class ModifiedButce(ProjeButceFormWizardForm):
        """
        ProjeButceFormunu modifiye debilmemiz icin olusturulmus subclass
        """
        pass

    # butce tercihlerinin ayarlandigi bolum
    proje_turu_id = proje_turu_dict.get("id")
    butce_form_data = {}
    if proje_turu_dict.get('butce_tercihi') == ButceTercihleri.butce_ile_ilgili_islem_yapmasin:
        form = ModifiedBAPProjeBasvuruFormu(formdata=initial_form_data,
                                            proje_turu=proje_turu_id)
    else:
        for butce_tercihi in proje_turu_dict.get("butce_kalemleri"):
            setattr(ModifiedButce,
                    "butce_tercihi" + str(butce_tercihi.get("gider_siniflandirma_id")),
                    FormField(ButceKalemiFormu))
            butce_form_data["butce_tercihi" + str(
                butce_tercihi.get("gider_siniflandirma_id"))] = butce_tercihi
        ModifiedBAPProjeBasvuruFormu.butce = FormField(ModifiedButce)
        form = ModifiedBAPProjeBasvuruFormu()

    if not kwargs.get("butce"):
        kwargs.update({"butce": butce_form_data})
    form.process(formdata=initial_form_data,
                 proje_turu=proje_turu_id,
                 **kwargs)

    # personel tercihlerinin ayarlandiği bölüm
    personel_secenegi = proje_turu_dict.get('yardimci_arastirmaci_secenekleri')
    personel_bilgi_copy = deepcopy(form.proje_personeli.form.form_description)

    # proje personelleri ekleme ekranı için bilgilendirme mesajları
    if proje_turu_dict.get('ozgecmis_yuklenmesi_zorunlu_mu'):
        personel_bilgi_copy.append(_("Başvuru esnasında özgeçmiş yüklemeniz zorunludur."))
    if proje_turu_dict.get('dosya_olarak_ozgecmis_yuklenebilir_mi'):
        personel_bilgi_copy.append(_("Dosya olarak özgeçmiş yükleyebilirsiniz."))
    else:
        del form.proje_personeli.form.yurutucu.form.ozgecmis_file_id
        del form.proje_personeli.form.arastirmaci.form.ozgecmis_file_id
        del form.proje_personeli.form.harici_arastirmaci.form.ozgecmis_file_id
        del form.proje_personeli.form.bursiyer.form.ozgecmis_file_id
    if proje_turu_dict.get('banka_bilgilerini_girmek_zorunlu_mu'):
        personel_bilgi_copy.append(_(
            "Proje personelleri için başvuru esnasında banka bilgilerini girmeniz zorunludur."))

    # personel tercihlerinin ayarlandiği bölüm
    if personel_secenegi == YardimciArastirmaciSecenekleri.sadece_proje_yurutucusu:
        personel_bilgi_copy.append(_("Proje personeli olarak sadece yürütücü ekleyebilirsiniz."))
        del form.proje_personeli.form.arastirmaci
        del form.proje_personeli.form.harici_arastirmaci
        del form.proje_personeli.form.bursiyer
    elif personel_secenegi == YardimciArastirmaciSecenekleri.sadece_danisman_ve_tez_ogrencisi:
        personel_bilgi_copy.append(_("Proje personeli olarak danışman ve tez "
                                     "öğrencisi(bursiyer) ekleyebilirsiniz."))
        del form.proje_personeli.form.harici_arastirmaci
    elif personel_secenegi == YardimciArastirmaciSecenekleri.sinirsiz_yardimci_arastirmaci:
        personel_bilgi_copy.append(_("Projenize istediğiniz sayıda Araştırmacı, Üniversite Dışı "
                                     "Araştırmacı ve Bursiyer Ekleyebilirsiniz."))
    elif personel_secenegi == YardimciArastirmaciSecenekleri.sinirli:
        alt_limit = proje_turu_dict.get("yardimci_arastirmaci_alt_limiti")
        ust_limit = proje_turu_dict.get("yardimci_arastirmaci_ust_limiti")
        personel_bilgi_copy.append(_("En fazla {}, en az {} yardımcı araştırmacı "
                                     "ekleyebilirsiniz.".format(ust_limit, alt_limit)))

    form.proje_personeli.form.form_description = personel_bilgi_copy

    tabs_copy = deepcopy(form.diger.tabs)
    if not proje_turu_dict.get('hakem_onerilsin_mi'):
        if 'hakem-onerileri' in form.diger.tabs:
            del tabs_copy['hakem-onerileri']
            form.diger.form.tabs = tabs_copy
        if hasattr(form.diger, 'proje_hakem'):
            del form.diger.form.proje_hakem
    else:
        if hasattr(form.diger, 'proje_hakem') and form.diger.proje_hakem is not None:
            form.diger.proje_hakem.form_alert = form.diger.proje_hakem.form_alert.format(
                hakem_sayi=proje_turu_dict.get('basvuru_hakem_oneri_sayisi'))

    if not proje_turu_dict.get('proje_yurutucusu_ek_dosyalar_ekleyebilir_mi'):
        if 'diger-dosyalar' in form.diger.tabs:
            del tabs_copy['diger-dosyalar']
            form.diger.form.tabs = tabs_copy
        if hasattr(form.diger, 'proje_diger'):
            del form.diger.form.proje_diger

    initial_ek_dosya = kwargs["diger"].get("ek_dosyalar") if kwargs.get("diger") else None
    if not initial_form_data and not initial_ek_dosya:
        for ek_dosya in proje_turu_dict.get("ek_dosyalar"):
            ek_dosya_data = {
                "ek_dosya_ad": ek_dosya["belge"]["adi"],
                "ek_dosya_aciklama": ek_dosya["belge"]["aciklama"],
                "ek_dosya_zorunlu_mu": ek_dosya["zorunlu_mu"],
                "ek_dosya_id": ek_dosya["belge"]["file_id"],
                "proje_turu_ek_dosya_id": ek_dosya["ek_dosya_id"],
            }
            form.diger.ek_dosyalar.append_entry(ek_dosya_data)
    if initial_form_data and proje_turu_dict.get("ek_dosyalar", None):
        for ek_dosya in proje_turu_dict.get("ek_dosyalar"):
            for form_ek_dosya in form.diger.ek_dosyalar:
                if ek_dosya.get("ek_dosya_id") == form_ek_dosya.proje_turu_ek_dosya_id.data:
                    form_ek_dosya.ek_dosya_zorunlu_mu.data = ek_dosya.get("zorunlu_mu")

    return form


def yurutucu_kaydet(proje_id, proje_tur_dict, yurutucu, yurutucu_ogretim_gorevlisi_id,
                    taslak_mi=False):
    """
    Proje yürütücüsü kaydeder
    Args:
        taslak_mi:
        proje_id: proje id
        proje_tur_dict: proje türü dict
        yurutucu: kaydedilecek yurutucunun form bilgilerini getirir
        yurutucu_ogretim_gorevlisi_id: proje yurutucusunun ogretim gorevlisi id

    """
    yurutucu_file_id = yurutucu.ozgecmis_file_id.data if yurutucu.ozgecmis_file_id else None
    if not taslak_mi:

        if proje_tur_dict.get("ozgecmis_yuklenmesi_zorunlu_mu"):
            if yurutucu_file_id is None and not yurutucu.ozgecmis_text.data:
                flash(_("Yürütücü İçin Özgeçmiş Yüklemeniz Zorunludur"), "error")
        if proje_tur_dict.get(
                "banka_bilgilerini_girmek_zorunlu_mu ") and not yurutucu.banka_bilgisi.data:
            flash(_("Yürütücü İçin Banka Bilgileri Girilmesi Zorunludur"), "error")

    yurutucu_ogretim_gorevlisi = DB.session.query(OgretimElemani.personel_id).filter_by(
        id=yurutucu_ogretim_gorevlisi_id).one()
    calisan_kayitli_mi = DB.session.query(ProjeCalisanlari.id).filter(
        ProjeCalisanlari.person_id == yurutucu_ogretim_gorevlisi.personel_id,
        ProjeCalisanlari.proje_id == proje_id).scalar()

    if calisan_kayitli_mi:
        flash(_("Yürütücü olarak kaydetmeye çalıştığınız kişi zaten proje çalışanı. Ekleyeblmek "
                "için var olan çalışanı kaldırınız."), "error")
    else:
        calisan_ozgecmis = Ozgecmis(tecrube=yurutucu.ozgecmis_text.data,
                                    file_id=yurutucu_file_id)
        DB.session.add(calisan_ozgecmis)
        DB.session.flush()

        proje_yurutucusu = ProjeCalisanlari(
            proje_id=proje_id,
            personel_id=yurutucu_ogretim_gorevlisi.personel_id,
            projeye_katkisi=yurutucu.projeye_katkisi.data,
            projedeki_gorevi=yurutucu.projedeki_gorevi.data,
            projeye_bilimsel_katkisi=yurutucu.projeye_bilimsel_katkisi.data,
            ozgecmis_id=calisan_ozgecmis.id,
            banka_bilgisi=yurutucu.banka_bilgisi.data,
            universite_disindan_mi=False)
        DB.session.add(proje_yurutucusu)
        DB.session.flush()


def proje_diger_dosya_kaydet(user_id, proje_id, proje_diger, proje_belgeleri, ):
    """Proje başvurusu diger dosyalari kaydeden method"""
    var_olan_dosyalar = []
    for dosya in proje_diger.dosyalar:
        for kayitli_diger_dosya in proje_belgeleri:
            if dosya.proje_belge_id.data == kayitli_diger_dosya.id:
                yeni_dosya = request.files.get(dosya.dosya_id.name, None)
                if yeni_dosya:
                    file = File(content=yeni_dosya,
                                user_id=user_id)
                    DB.session.add(file)
                    DB.session.flush()
                    kayitli_diger_dosya.belge_id = file.id
                kayitli_diger_dosya.baslik = dosya.ad.data
                kayitli_diger_dosya.aciklama = dosya.aciklama.data
                var_olan_dosyalar.append(kayitli_diger_dosya.id)
                break
        else:
            yeni_dosya = request.files.get(dosya.dosya_id.name, None)
            if yeni_dosya:
                file = File(content=yeni_dosya,
                            user_id=user_id)
                DB.session.add(file)
                DB.session.flush()
                proje_belgesi = ProjeBelgeleri(proje_id=proje_id,
                                               belge_id=file.id,
                                               baslik=dosya.ad.data,
                                               aciklama=dosya.aciklama.data)
                DB.session.add(proje_belgesi)
                DB.session.flush()
                var_olan_dosyalar.append(proje_belgesi.id)
    return var_olan_dosyalar


def proje_ek_dosyalar_kaydet(user_id, proje_id, form_ek_dosyalar, proje_belgeleri, taslak_mi):
    """Proje başvurusu ek dosyalarını kaydeden method"""
    for ek_dosya in form_ek_dosyalar:
        if ek_dosya.proje_turu_ek_dosya_id.data:
            for kayitli_ek_dosya in proje_belgeleri:
                if kayitli_ek_dosya.proje_turu_ek_dosya_id == \
                        ek_dosya.proje_turu_ek_dosya_id.data:
                    yeni_dosya = request.files.get(ek_dosya.yeni_dosya.name, None)
                    if yeni_dosya:
                        file = File(content=yeni_dosya,
                                    user_id=user_id)
                        DB.session.add(file)
                        DB.session.flush()
                        kayitli_ek_dosya.belge_id = file.id
                        ek_dosya.yeni_dosya.id = file.id
                    kayitli_ek_dosya.aciklama = ek_dosya.yeni_dosya_aciklama.data
                    break
            else:
                yeni_dosya = request.files.get(ek_dosya.yeni_dosya.name, None)
                if yeni_dosya:
                    file = File(content=yeni_dosya,
                                user_id=user_id)
                    DB.session.add(file)
                    DB.session.flush()
                    proje_belge = ProjeBelgeleri(
                        aciklama=ek_dosya.yeni_dosya_aciklama.data,
                        proje_id=proje_id,
                        belge_id=file.id,
                        proje_turu_ek_dosya_id=ek_dosya.proje_turu_ek_dosya_id.data
                    )
                    DB.session.add(proje_belge)
                elif ek_dosya.ek_dosya_zorunlu_mu.data and not taslak_mi:
                    flash(_("Zorunlu ek dosyaları yüklemeniz gerekmektedir."), "error")


def butce_kaydet(proje_id, butce_form_data):
    """
    Butce kaydini gerceklestiren metot
    Proje basvuru formundan gelen verileri proje_kalemleri tablosuna ekler
    onerilen_yil_1, 2, 3  toplamindan ilgili kalemin onerilen_butcesi bulunur.
    Projeye eklenen proje_kalemlerinin onerilen_butce leri toplamindan proje telif edilen
    butcesi olusturulur

    :param proje_id: basvuru yapilan projenin id si
    :param butce_form_data: proje basvuru formu butce bolumu
    :return: proje kalemlerinin onerilen_butcelerinin toplamindan olusan proje_butcesi
    """
    toplam_proje_butcesi = 0
    hata_listesi = []
    for _, value in butce_form_data.items():
        kalem_butcesi, hata = kalem_alimlari_kaydet(value["alimlar"],
                                                    proje_id,
                                                    value["butce_kalemi_id"],
                                                    value["butce_kalemi_adi"],
                                                    value["butce_alt_limiti"],
                                                    value["butce_ust_limiti"],
                                                    )
        toplam_proje_butcesi += kalem_butcesi
        if hata:
            hata_listesi.append(hata)

    return toplam_proje_butcesi, hata_listesi


def kalem_alimlari_kaydet(alimlar, proje_id, butce_kalemi_id,
                          butce_kalem_adi, kalem_alt_limiti, kalem_ust_limiti):
    """
    Proje butce kalemine ait alimlari kaydeder. Alimlarin toplam tutarini ve varsa hata doner

    :param alimlar: proje butce kalemine ait alimlar
    :param proje_id: ilgili proje id si
    :param butce_kalemi_id: butce kalemi id
    :param butce_kalem_adi: ilgili butce kaleminin adi
    :param kalem_alt_limiti: proje butce kalemine ait alt limit
    :param kalem_ust_limiti: proje butce kalemine ait ust limit
    :return: alimlarin toplam tutari, hata
    """
    toplam_kalem_butcesi = 0
    hata = ""
    for alim in alimlar:
        onerilen_butce = 0
        if alim.get("ad"):
            # DB.session.add(ProjeButce(proje_id=proje_id, butce_kalemi_id=bk_id, **alim))
            if alim["onerilen_yil_1"]:
                onerilen_butce += alim["onerilen_yil_1"]
            if alim["onerilen_yil_2"]:
                onerilen_butce += alim["onerilen_yil_2"]
            if alim["onerilen_yil_3"]:
                onerilen_butce += alim["onerilen_yil_3"]
            # onerilen_butce = alim["onerilen_yil_1"] + alim["onerilen_yil_2"] + alim[
            #     "onerilen_yil_3"]
            proje_kalemi = ProjeKalemi(proje_id=proje_id,
                                       proje_turu_butce_kalem_id=butce_kalemi_id,
                                       onerilen_butce=onerilen_butce,
                                       **alim)
            DB.session.add(proje_kalemi)
            toplam_kalem_butcesi += onerilen_butce
    if not (kalem_ust_limiti >= toplam_kalem_butcesi >= kalem_alt_limiti):
        hata = _("{} bütçe kalemine ait toplam alımlar tutarı {} - {} arasında olmalıdır".format(
            butce_kalem_adi, kalem_alt_limiti, kalem_ust_limiti
        ))

    return toplam_kalem_butcesi, hata


def get_proje_data(proje_turu_dict, proje, ):
    """
    Proje Modelindeki bilgileri alip forma uygun formata getirir
    :param proje_turu_dict: projenin bagli oldugu proje turu
    :param proje: Proje model instance
    :return: Proje formuna uygun formatta uretilmis form data
    """
    proje_dict = proje.to_dict()
    destekleyen_kurulus = proje.proje_destekleyen_kurulus.to_dict() if proje.proje_destekleyen_kurulus else {}
    yurutucu = {}
    yurutucu_calisan = DB.session.query(ProjeCalisanlari).filter_by(
        proje_id=proje.id,
        personel_id=proje.yurutucu).first()
    if yurutucu_calisan:
        yurutucu.update(yurutucu_calisan.to_dict())
        yurutucu.update({"yurutucu_id": proje.yurutucu})
    proje_diger_dosyalar = []
    proje_ek_dosyalar = []
    for belge in proje.proje_belgeleri:
        if not belge.proje_turu_ek_dosya_id:
            proje_diger_dosyalar.append({
                "ad": belge.baslik,
                "aciklama": belge.aciklama,
                "dosya_id": belge.belge_id,
                "proje_belge_id": belge.id
            })
        else:
            for ek_dosya in proje_turu_dict.get("ek_dosyalar"):
                if ek_dosya.get("ek_dosya_id") == belge.proje_turu_ek_dosya_id:
                    proje_ek_dosyalar.append({
                        "ek_dosya_ad": ek_dosya["belge"]["adi"],
                        "ek_dosya_aciklama": ek_dosya["belge"]["aciklama"],
                        "ek_dosya_zorunlu_mu": ek_dosya["zorunlu_mu"],
                        "ek_dosya_id": ek_dosya["belge"]["file_id"],
                        "proje_turu_ek_dosya_id": belge.proje_turu_ek_dosya_id,
                        "yeni_dosya_aciklama": belge.aciklama,
                        "yeni_dosya": belge.belge_id,

                    })
    butce_dict = {}
    for butce_kalemi in proje_turu_dict.get("butce_kalemleri"):
        alimlar = []
        yolluklar = []
        gider_siniflandirma_id = butce_kalemi["gider_siniflandirma_id"]

        for proje_kalemi in proje.proje_kalemleri:
            if proje_kalemi.proje_turu_butce_kalem_id == butce_kalemi["butce_kalemi_id"]:
                data = {
                    "ad": proje_kalemi.ad,
                    "aciklama": proje_kalemi.gerekce,
                    "birim": proje_kalemi.birim,
                    "onerilen_miktar": proje_kalemi.onerilen_miktar,
                    "onerilen_yil_1": proje_kalemi.onerilen_yil_1,
                    "onerilen_yil_2": proje_kalemi.onerilen_yil_2,
                    "onerilen_yil_3": proje_kalemi.onerilen_yil_3
                }
                alimlar.append(data)
        butce_dict.update({
            "butce_tercihi" + str(gider_siniflandirma_id): {
                "alimlar": alimlar,
                "yolluklar": yolluklar,
                "butce_kalemi_id": butce_kalemi["butce_kalemi_id"],
                "gider_siniflandirma_id": butce_kalemi["gider_siniflandirma_id"],
                "butce_kalemi_adi": butce_kalemi["butce_kalemi_adi"],
                "butce_alt_limiti": butce_kalemi["butce_alt_limiti"],
                "butce_ust_limiti": butce_kalemi["butce_ust_limiti"]
            }
        })
    form_data = {
        "genel_bilgiler": {
            "genel_bilgiler": proje_dict,
            "fakulte": proje_dict,
            "ozet_bilgiler": proje_dict,
            "onaylayan_yetkili": proje_dict,
            "destekleyen_kurulus": destekleyen_kurulus
        },
        "proje_personeli": {
            "yurutucu": yurutucu,
        },
        "diger": {
            "ek_dosyalar": proje_ek_dosyalar,
            "proje_diger": {"dosyalar": proje_diger_dosyalar},
        },
        "butce": butce_dict
    }
    return form_data


def month_year_to_day(sayisi, birimi):
    """
    Ay veya yıl girilen degerleri güne cevirir
    Ay 30 gun yıl 365 gun olark hesaplanir
    :return: gun sayisi
    """
    if birimi == ProjeSuresiBirimi.ay:
        return 30 * sayisi
    elif birimi == ProjeSuresiBirimi.yil:
        return 365 * sayisi
    return sayisi
