"""Toplanti, Gundem, GundemSablonu modellerini iceren modul"""
from sqlalchemy import event
from sqlalchemy import Column, Integer, ForeignKey, Text, Enum, DateTime, Boolean
from sqlalchemy.sql import bindparam, func, select
from sqlalchemy.orm import relationship

from zopsedu.bap.models.helpers import GundemTipi, KararDurumu, ToplantiDurumu, SablonKategori
from zopsedu.lib.db import BASE_MODEL, ZopseduBase
from zopsedu.models.custom_types import JSONEncodedList


class BapGundem(ZopseduBase, BASE_MODEL):
    """
    Bap toplanti gündem modeli
    """

    __tablename__ = "bap_gundem"
    id = Column(Integer, primary_key=True)
    proje_id = Column(Integer, ForeignKey("proje.id"))
    toplanti_id = Column(Integer, ForeignKey("bap_toplanti.id"))
    sablon_id = Column(Integer, ForeignKey("gundem_sablon.id"))
    ek_dosya_id = Column(Integer, ForeignKey("file.id"))

    karar = Column(Text)
    aciklama = Column(Text)
    tipi = Column(Enum(GundemTipi))
    karar_durum = Column(Enum(KararDurumu), default=KararDurumu.degerlendirilmedi)
    gundem_sira_no = Column(Integer)

    yonetime_bilgi_notu = Column(Text)
    kisiye_ozel_not = Column(Text)

    proje = relationship("Proje")
    sablon = relationship("GundemSablon")
    toplanti = relationship("BapToplanti", lazy="joined")

    ek_dosya_r = relationship("File", lazy='joined')


@event.listens_for(BapGundem, 'before_update')
# pylint: disable=too-many-branches,too-many-locals,unused-argument
def bap_gundem_event_listener(mapper, connection, target):
    """
    Gündem update before listener. gundem_sira_no duzenlemek icin kullanilir. 3 durum söz konusu
    - Gundemi bir toplantiya atama
    - Atanmış bir gündemi toplantidan cıkarmak.
    - Atanmış bir gundemin gundem_sira_no sunu degistirmek
    """
    guncellenecek_gundemler = []
    bap_gundem = BapGundem.__table__
    eski_data_query = bap_gundem.select().where(bap_gundem.c.id == target.id)
    eski_data = connection.execute(eski_data_query).fetchone()

    toplanti_id = target.toplanti_id or eski_data["toplanti_id"]

    get_all_gundem_query = bap_gundem.select().where(
        bap_gundem.c.toplanti_id == bindparam("toplanti_id")).order_by(bap_gundem.c.gundem_sira_no)
    gundemler = connection.execute(get_all_gundem_query, toplanti_id=toplanti_id).fetchall()
    # toplanti gundemleri gundem_sira_no'sunun sirali olmasini kontrol edip sirali degilse duzeltir.
    if gundemler and len(gundemler) != gundemler[len(gundemler) - 1]["gundem_sira_no"]:
        update_list = []
        for i, _ in enumerate(gundemler):
            update_list.append({"gundem_id": gundemler[i]["id"],
                                "gundem_sira_no": i + 1})
        update_query = bap_gundem.update().where(bap_gundem.c.id == bindparam("gundem_id")). \
            values(gundem_sira_no=bindparam("gundem_sira_no"))
        connection.execute(update_query, update_list)
        eski_data = connection.execute(eski_data_query).fetchone()

    if target.toplanti_id != eski_data["toplanti_id"]:
        if target.toplanti_id is None:
            # toplanti gundemlerinden cikarilmis gundem
            update_query = bap_gundem.update().where(bap_gundem.c.id == bindparam("gundem_id")). \
                values(gundem_sira_no=bap_gundem.c.gundem_sira_no - 1)
            for i in range(target.gundem_sira_no, len(gundemler)):
                guncellenecek_gundemler.append({"gundem_id": gundemler[i].id})
            if guncellenecek_gundemler:
                connection.execute(update_query, guncellenecek_gundemler)
            target.gundem_sira_no = None
        else:
            # ilgili gundemi bir toplantiya atama islemi esnasinda
            select_max = select([func.max(bap_gundem.c.gundem_sira_no)]). \
                where(bap_gundem.c.toplanti_id == target.toplanti_id)
            max_gundem_sira_no = connection.execute(select_max).fetchone()[0]
            target.gundem_sira_no = (max_gundem_sira_no if max_gundem_sira_no else 0) + 1
            if eski_data["toplanti_id"]:
                eski_toplanti_gundemleri = connection.execute(
                    get_all_gundem_query,
                    toplanti_id=eski_data["toplanti_id"]
                ).fetchall()
                # ilgili gundemi bir toplantidan baska bir toplantiya atama islemi
                update_query = bap_gundem.update().where(
                    bap_gundem.c.id == bindparam("gundem_id")).values(
                        gundem_sira_no=bap_gundem.c.gundem_sira_no - 1)
                for i in range(eski_data["gundem_sira_no"], len(eski_toplanti_gundemleri)):
                    guncellenecek_gundemler.append({"gundem_id": eski_toplanti_gundemleri[i].id})
                if guncellenecek_gundemler:
                    connection.execute(update_query, guncellenecek_gundemler)
    elif "gundem_sira_no" not in target._sa_instance_state.unmodified:  # pylint: disable=protected-access
        # atanmis bir gundemin gundem_sira_no degisikligi
        eski_gundem_sira_no = eski_data["gundem_sira_no"]
        yeni_gundem_sira_no = target.gundem_sira_no
        if eski_gundem_sira_no > yeni_gundem_sira_no:
            update_query = bap_gundem.update().where(bap_gundem.c.id == bindparam("gundem_id")).\
                values(gundem_sira_no=bap_gundem.c.gundem_sira_no + 1)
            for i in range(yeni_gundem_sira_no, eski_gundem_sira_no):
                guncellenecek_gundemler.append({"gundem_id": gundemler[i - 1].id})
        else:
            update_query = bap_gundem.update().where(bap_gundem.c.id == bindparam("gundem_id")).\
                values(gundem_sira_no=bap_gundem.c.gundem_sira_no - 1)
            for i in range(eski_gundem_sira_no, yeni_gundem_sira_no):
                guncellenecek_gundemler.append({"gundem_id": gundemler[i].id})

        if guncellenecek_gundemler:
            connection.execute(update_query, guncellenecek_gundemler)


class BapToplanti(ZopseduBase, BASE_MODEL):
    """
    Bap toplanti modeli
    """
    __tablename__ = "bap_toplanti"
    id = Column(Integer, primary_key=True)

    toplanti_tarihi = Column(DateTime)
    toplanti_durumu = Column(Enum(ToplantiDurumu))
    ekleyen_id = Column(Integer, ForeignKey("users.id"))
    sonuclandi_mi = Column(Boolean, default=False)

    ekleyen = relationship("User", uselist=False)
    katilimcilar = relationship("ToplantiKatilimci", cascade="all, delete-orphan",
                                passive_deletes=True, uselist=False)
    gundemler = relationship("BapGundem", order_by="BapGundem.gundem_sira_no")


class GundemSablon(ZopseduBase, BASE_MODEL):
    """
    Gündem sablonlarinin tutuldugu model
    """
    __tablename__ = "gundem_sablon"
    id = Column(Integer, primary_key=True)

    # sablon basligi
    sablon_tipi = Column(Enum(GundemTipi))
    kategori = Column(Enum(SablonKategori))

    aciklama = Column(Text)
    karar = Column(Text)


class ToplantiKatilimci(ZopseduBase, BASE_MODEL):
    """
    Toplanti Katilimcilarinin tutuldugu model
    """
    __tablename__ = "toplanti_katilimci"

    id = Column(Integer, primary_key=True)

    toplanti_id = Column(Integer, ForeignKey("bap_toplanti.id", ondelete='CASCADE'))

    # toplanti katilimcilari listesi idari personel id listesinden olusur
    katilimcilar = Column(JSONEncodedList)
