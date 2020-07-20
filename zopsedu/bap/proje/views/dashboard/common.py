"""Proje dashboard viewlari icin ortak methodlari icerir"""
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from zopsedu.bap.models.helpers import ProjeBasvuruDurumu
from zopsedu.bap.models.proje_detay import ProjeCalisanlari
from zopsedu.lib.db import DB
from zopsedu.lib.proje_state_dispatcher import ProjeStateDispacther
from zopsedu.models import Proje, OgretimElemani, Personel, AppState, AppAction


def get_proje_with_related_fields(proje_id):
    """
    Proje id ile proje ve iliskili alanlari veritabanindan getiren method
    Args:
        proje_id (int): proje id

    Returns:
        proje instance

    """
    proje = DB.session.query(Proje).options(
        joinedload(Proje.proje_proje_turu).load_only(
            "ad",
            "oneri_sablon_id",
            "hakem_degerlendirme_sablon_id",
            "hakem_ara_rapor_sablon_id",
            "ara_rapor_sablon_id",
            "sonuc_raporu_sablon_id",
            "hakem_sonuc_rapor_sablon_id"),
        joinedload(Proje.proje_yurutucu).load_only("id").joinedload(
            OgretimElemani.personel).load_only("id").joinedload(
            Personel.person).load_only("ad", "soyad"),
        joinedload(Proje.proje_calisanlari).joinedload(
            ProjeCalisanlari.personel
        ).joinedload(
            Personel.birimi),
        joinedload(Proje.proje_gerceklestirme_gorevlisi).load_only("id").joinedload(
            Personel.person).load_only("ad", "soyad"),
        joinedload(Proje.proje_muhasebe_yetkilisi).load_only("id").joinedload(
            Personel.person).load_only("ad", "soyad"),
        joinedload(Proje.proje_harcama_yetkilisi).load_only("id").joinedload(
            Personel.person).load_only("ad", "soyad"),
        joinedload(Proje.fakulte).load_only("uzun_ad"),
        joinedload(Proje.bolum).load_only("uzun_ad"),
        joinedload(Proje.ana_bilim_dali).load_only("uzun_ad"),
        joinedload(Proje.bilim_dali).load_only("uzun_ad"),
        joinedload(Proje.proje_raporlari),
        joinedload(Proje.proje_mesajlari)
    ).filter(Proje.id == proje_id, or_(Proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi,
                                       Proje.proje_basvuru_durumu ==ProjeBasvuruDurumu.revizyon_bekleniyor)).first()
    return proje


def get_next_states_info(proje_id):
    """
    proje_id si ile bir projenin icinde bulundugu state i bulup o durumun possible next
    state bilgisini döner
    :param proje_id: projenin id si
    :return: AppState
    """
    proje_durum = ProjeStateDispacther.current_state_info(proje_id=proje_id)

    possible_next_states = ProjeStateDispacther.possible_next_states_info(
        current_app_state_id=proje_durum.id)

    next_states_info = DB.session.query(AppState). \
        filter(AppState.state_code.in_(possible_next_states)).all()

    return next_states_info


def get_actions_info(proje_id):
    """
        proje_id si ile bir projenin state ine bakılarak o state in ilişkili oldukları action bilgisini döner.
        :param proje_id: projenin id si
        :return: AppAction

        """
    proje_durum = ProjeStateDispacther.current_state_info(proje_id=proje_id)

    possible_actions = ProjeStateDispacther.possible_actions(
        current_app_state_id=proje_durum.id)

    actions_info = DB.session.query(AppAction).filter(AppAction.action_code.in_(possible_actions)).all()

    return actions_info
