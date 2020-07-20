from datetime import datetime

from zopsedu.bap.anasayfa.forms.anaysayfa import AnasayfaFormu
from zopsedu.icerik.model import Icerik, IcerikTipi, IcerikBirimTipi
from zopsedu.lib.db import DB


def get_anasayfa_formlar():
    arama_formu = AnasayfaFormu()
    return arama_formu


def get_satinalma_duyurular():
    on_sayfa_satinalma_duyurulari = DB.session.query(Icerik).filter(
        Icerik.aktif_mi == True,
        Icerik.tipi == IcerikTipi.satinalma,
        Icerik.birim_tipi == IcerikBirimTipi.bap).filter(
        Icerik.baslangic_tarihi < datetime.now(),
        Icerik.bitis_tarihi > datetime.now()).limit(15).all()
    return on_sayfa_satinalma_duyurulari


def get_bap_duyurular():
    bap_on_sayfa_duyurululari = DB.session.query(Icerik).filter(
        Icerik.aktif_mi == True,
        Icerik.on_sayfa_gorunurlugu == True,
        Icerik.tipi == IcerikTipi.duyuru,
        Icerik.birim_tipi == IcerikBirimTipi.bap).filter(
        Icerik.baslangic_tarihi < datetime.now(),
        Icerik.bitis_tarihi > datetime.now()).limit(15).all()
    return bap_on_sayfa_duyurululari
