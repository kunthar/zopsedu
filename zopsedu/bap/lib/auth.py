"""BAP icin ozel auth kurallari modulu"""

# pylint: disable=no-init
from flask import request as req
from flask import current_app
from flask_allows import Requirement
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from zopsedu.auth.models.auth import User
from zopsedu.bap.models.firma import BapFirma
from zopsedu.common.kullanici_profil.models import Ozgecmis
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.models import Proje, OgretimElemani, Personel, ProjeHakemleri
from zopsedu.bap.models.proje_detay import ProjeHakemDavetDurumlari
from zopsedu.personel.models.hakem import Hakem
from zopsedu.bap.models.helpers import ProjeBasvuruDurumu


class ProjeYurutucusu(Requirement):
    """ProjeRapor view izin classı"""

    # pylint: disable=redefined-outer-name
    def fulfill(self, user, request=None):
        """`proje_id` ile belirtilen proje yurutucusunun, `current_user` olmasi beklenir"""
        try:
            proje_id = req.view_args['proje_id']
            proje = DB.session.query(Proje).filter_by(id=proje_id).one()
            yurutucu = DB.session.query(OgretimElemani).filter_by(id=proje.yurutucu).one()
            personel = DB.session.query(Personel).filter_by(id=yurutucu.personel_id).options(
                joinedload(Personel.person)).one()
        except NoResultFound:
            return False

        return user.person.id == personel.person.id
        # pylint: enable=redefined-outer-name


class AtanmisHakem(Requirement):
    """Hakem Proje Degerlendirme viewlari icin izin classi"""

    # pylint: disable=redefined-outer-name
    def fulfill(self, user, request=None):
        proje_id = req.view_args['proje_id']
        hakem = DB.session.query(Hakem).filter(Hakem.person_id == user.person.id).first()
        if not hakem:
            return False
        hakem_id = hakem.id
        return bool(DB.session.query(ProjeHakemleri).filter(
            ProjeHakemleri.proje_id == proje_id,
            ProjeHakemleri.hakem_id == hakem_id,
            or_(ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.kabul_edildi,
                ProjeHakemleri.davet_durumu == ProjeHakemDavetDurumlari.gonderildi)
        ).all())


class TamamlanmamisProjeBasvurusu(Requirement):
    """
    Proje basvurusunun tamamlanmamış olma durumunu ifade eden requirement
    Taslak veya revizyon durumunda olma halini belirtir
    """

    # pylint: disable=redefined-outer-name
    def fulfill(self, user, request=None):
        proje_id = req.view_args['proje_id']
        try:
            proje = DB.session.query(Proje.id,
                                     Proje.proje_basvuru_durumu,
                                     Proje.user_id).filter_by(id=proje_id).one()
            if proje.proje_basvuru_durumu == ProjeBasvuruDurumu.tamamlandi:
                return False
        except SQLAlchemyError as exc:
            CustomErrorHandler.error_handler(
                hata="Proje id ve user id ile projeyi get yaparken bir hata oluştur"
                     ". Hata: {}, Proje Id: {}, User Id: {}".format(exc,
                                                                    proje_id,
                                                                    user.id))
            return False
        return True


class OzgecmisKaydetme(Requirement):
    """Ozgecmisin sahibini ifade eden requirement"""

    # pylint: disable=redefined-outer-name
    def fulfill(self, user, request=None):

        try:
            ozgecmis = DB.session.query(Ozgecmis).filter(Ozgecmis.user_id == user.id).one()
        except SQLAlchemyError as exc:
            _ozgecmis = Ozgecmis(user_id=user.id)
            DB.session.add(_ozgecmis)
            DB.session.commit()
            return True
        return ozgecmis.user_id == user.id


class FirmaYetkilisi(Requirement):
    """FirmaYetkilisi firma guncelleme view izin classı"""

    # pylint: disable=redefined-outer-name
    def fulfill(self, user, request=None):
        """`firma_id` ile belirtilen firmanin yetkilisi, `current_user` olmasi beklenir"""
        try:
            firma_id = req.view_args['firma_id']
            firma = DB.session.query(BapFirma).filter_by(id=firma_id).one()
            firma_yetkilisi = DB.session.query(User).filter_by(id=firma.user_id).one()
        except Exception:
            return False

        return user.id == firma_yetkilisi.id
