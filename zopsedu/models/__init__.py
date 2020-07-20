"""Zopsedu data modelleri icin kisa yol modulu"""
# genel modeller
from zopsedu.models.query_helper import QueryHelper
from zopsedu.models.sablon import Sablon, SablonTipi
from zopsedu.models.file import File
from zopsedu.models.taslak import Taslak
from zopsedu.models.adres import Adres
from zopsedu.models.person import Person
from zopsedu.models.form import Form
from zopsedu.models.birim import Birim
from zopsedu.models.helpers import WTFormEnum
from zopsedu.models.activity_log import AktiviteKaydi, CrudKaydi
from zopsedu.models.app_log import AppLog
from zopsedu.models.ayarlar import SiteAyarlari, GenelAyarlar
from zopsedu.models.odeme_bilgileri import OdemeBilgileri
from zopsedu.models.app_state import AppState
from zopsedu.models.app_state_tracker import AppStateTracker
from zopsedu.models.app_demand import AppDemand
from zopsedu.models.app_action import AppAction
from zopsedu.models.vergi_daireleri import VergiDairesi
# auth modelleri
from zopsedu.auth.models.auth import User
from zopsedu.auth.models.auth import Role, UserRole, RolePermission, RolePermissionRestriction
from zopsedu.auth.models.auth import UserRolePermissionRestriction, Permission

#ebys modelleri
from zopsedu.ebys.models.ebys import EbysTakip

# mesaj modeli
from zopsedu.common.mesaj.models import Mesaj, MesajEk

# ozgecmis modeli
from zopsedu.common.kullanici_profil.models import Ozgecmis

# personel modelleri
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.hakem import Hakem, HakemOneri
from zopsedu.personel.models.ogretim_elemani import OgretimElemani
from zopsedu.personel.models.harici_ogretim_elemani import HariciOgretimElemani
from zopsedu.personel.models.idari_personel import  BapIdariPersonel
from zopsedu.personel.models.unvan import HitapUnvan

# bap modelleri
from zopsedu.bap.models.proje import Proje, EskiProje
from zopsedu.bap.models.proje_rapor import ProjeRapor
from zopsedu.bap.models.proje_turu import ProjeTuru, PersonelAyarlari
from zopsedu.bap.models.proje_turu import Butce, Cikti, EkDosya
from zopsedu.bap.models.proje_turu import ButceKalemi, SabitButceKalemi
from zopsedu.bap.models.belge import BAPBelge
from zopsedu.bap.models.proje_detay import ProjeDetay, ProjeBelgeleri, ProjeCalisanlari, \
    ProjeDegerlendirmeleri, ProjeHakemleri
from zopsedu.bap.models.proje_mesajlari import ProjeMesaj
from zopsedu.bap.models.proje_destekleyen_kurulus import ProjeDestekleyenKurulus
from zopsedu.bap.models.toplanti import BapGundem, BapToplanti, GundemSablon, ToplantiKatilimci
from zopsedu.bap.models.analitik_kodlar import GelirSiniflandirma, GiderSiniflandirma
from zopsedu.bap.models.finansman_tipi_siniflandirma import FinansmanTipi
from zopsedu.bap.models.kurumsal_siniflandirma import KurumsalSiniflandirma
from zopsedu.bap.models.fonksiyonel_kodlar import FonksiyonelKodlar
from zopsedu.bap.models.proje_not import ProjeNot
from zopsedu.bap.models.tasinir_kodlar import TasinirKodlar
from zopsedu.bap.models.detayli_hesap_planlari import DetayliHesapPlanlari

# proje satinalma modelleri
from zopsedu.bap.models.gelir_kasasi import GelirKasasi, ButceGirdi
from zopsedu.bap.models.firma_teklif import FirmaSatinalmaTeklif, FirmaTeklifKalemi, FirmaTeklifDosya
from zopsedu.bap.models.proje_kalemleri import ProjeKalemi
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi, TalepKalemleri
from zopsedu.bap.models.muhasebe_fisi import MuhasebeFisi, MuhasebeFisMaddesi
from zopsedu.bap.models.proje_turu import SabitButceKalemi, ButceKalemi
from zopsedu.bap.models.siparis_takip import SiparisTakip

# ogrenci modelleri
from zopsedu.ogrenci.models.ogrenci import Ogrenci

# icerik modelleri
from zopsedu.icerik.model import Icerik, IcerikEkDosya

# firma modeli
from zopsedu.bap.models.firma import BapFirma
from zopsedu.bap.models.firma_mesaj import FirmaMesaj

# yoksis modellerini import eder
from zopsedu.akademik_performans.models import *
