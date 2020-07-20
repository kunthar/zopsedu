"""Proje Dashboard view classları"""
from decimal import Decimal

from flask import render_template, request, jsonify, abort
from flask_allows import Or
from flask_classful import FlaskView, route
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, lazyload

from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.auth.permissions import permission_dict
from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi
from zopsedu.bap.satinalma.lib.satinalma_islemleri_get import satinalma_management_methods_get
from zopsedu.bap.satinalma.lib.satinalma_islemleri_post import satinalma_management_methods_post
from zopsedu.bap.satinalma.views.commons import get_satinalma_with_related_fields
from zopsedu.lib.db import DB
from zopsedu.lib.error_logger import CustomErrorHandler
from zopsedu.lib.satinalma_state_dispatcher import SatinalmaStateDispatcher
from zopsedu.models import AppAction, AppState
from zopsedu.models.helpers import StateTypes, ActionTypes


class SatinalmaDashboardView(FlaskView):
    """
    Satinalma Ozet
    """

    @staticmethod
    @login_required
    @auth.requires(Permission(*permission_dict["bap"]["satinalma"]["satinalma_ozeti_goruntuleme"]),
                   Or(Role('BAP Yetkilisi'), Role('BAP Admin')))
    @route("<int:satinalma_id>/ozet", methods=["GET", "POST"], endpoint="satinalma_dashboard")
    def satinalma_ozet(satinalma_id):
        """
        Satınalma özeti bilgilerine ulaşmak için kullanılır
        Args:
            satinalma_id(int): satinalma id si

        Returns:
        """

        try:
            satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

            satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                            action_type=ActionTypes.satinalma,
                                                            entity_type=ProjeSatinAlmaTalebi,
                                                            entity=satinalma)

            satinalma_durum = satinalma_dispatcher.current_state_info()

            possible_next_states = satinalma_dispatcher.possible_next_states_info()

            possible_actions = satinalma_dispatcher.possible_actions()

            proje = DB.session.query(Proje).options(
                joinedload(Proje.proje_kalemleri).lazyload("*")).filter(
                Proje.id == satinalma.proje_id).first()

            actions_info = DB.session.query(AppAction).filter(
                AppAction.action_code.in_(possible_actions.possible_actions)).all()

            states_info = DB.session.query(AppState). \
                filter(AppState.state_code.in_(possible_next_states.possible_states)).all()

            toplam_butce = Decimal("0.00")
            rezerv_butce = Decimal("0.00")
            kullanilan_butce = Decimal("0.00")
            for proje_kalemi in proje.proje_kalemleri:
                toplam_butce += proje_kalemi.toplam_butce
                rezerv_butce += proje_kalemi.rezerv_butce
                kullanilan_butce += proje_kalemi.kullanilan_butce

            kullanilabilir_butce = toplam_butce - rezerv_butce - kullanilan_butce
            kullanilabilir_butce = kullanilabilir_butce.quantize(Decimal(".01"))

            satinalma_durumlari = DB.session.query(
                AppState.state_code.label("state_code"),
                AppState.description.label("state_description"),
                AppState.current_app_state.label("current_app_state"),
            ).filter(
                AppState.state_type == StateTypes.satinalma
            ).options(lazyload("*")).order_by(AppState.id).all()

            satinalma_islemleri = DB.session.query(
                AppAction.action_code.label("action_code"),
                AppAction.description.label("action_description"),
            ).filter(
                AppAction.action_type == ActionTypes.satinalma
            ).order_by(
                AppAction.id
            ).all()

        except SQLAlchemyError as exc:
            CustomErrorHandler.error_handler(hata="Satınalma dashboard ekranı yüklenirken database sorgularında sorun oluştu "
                                                  "Hata: {}, User id: {}, Satınalma id: {}".format(
                                                 exc, current_user.id, satinalma_id))

            return abort(500)

        return render_template("satinalma_dashboard/satinalma_ozeti.html",
                               satinalma=satinalma,
                               satinalma_id=satinalma_id,
                               actions_info=actions_info,
                               states_info=states_info,
                               satinalma_durum=satinalma_durum,
                               proje=proje,
                               kullanilabilir_butce=kullanilabilir_butce,
                               kullanilan_butce=kullanilan_butce,
                               rezerv_butce=rezerv_butce,
                               toplam_butce=toplam_butce,
                               satinalma_islemleri=satinalma_islemleri,
                               satinalma_durumlari=satinalma_durumlari)

    @staticmethod
    @login_required
    @auth.requires(Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route("/dashboard/<int:satinalma_id>/", methods=["POST"], endpoint="satinalma_durum_degistir")
    def satinalma_durum_degistir(satinalma_id):
        action_code = request.get_json()['action_code']

        template = satinalma_management_methods_get[action_code](satinalma_id=satinalma_id,
                                                                 action_code=action_code)
        return jsonify(status="success", template=template)

    @staticmethod
    @login_required
    @auth.requires(Or(Role("BAP Admin"), Role("BAP Yetkilisi")))
    @route("/<int:satinalma_id>", methods=["POST"], endpoint="satinalma_durum_kaydet")
    def satinalma_durum_kaydet(satinalma_id):

        request_json = request.get_json()
        form = request_json['form']
        action_code = request_json['action_code']

        try:
            # todo: donen deger unpack edilip template aktarilir. duruma gore render edilmis
            # template veya template ile birlikte bir hata mesaji gelir.hata mesaji gelirse
            # template (rendered_template, hata_mesaji) seklinde bir tuple olur. hata mesaji yoksa
            # template type "str" dir.
            # todo: daha guzel bir cozum bulunması gerekiyor. monkey patch !!!!
            template = satinalma_management_methods_post[action_code](
                satinalma_id=satinalma_id,
                action_code=action_code,
                form=form)
            if not template:
                return jsonify(status="success")

            if type(template) is str:
                return jsonify(status="error",
                               template=template,
                               action_code=action_code,
                               hata_mesaji=""), 400
            return jsonify(status="error",
                           template=template[0],
                           action_code=action_code,
                           hata_mesaji=template[1] if len(template) > 1 else ""), 400

        except Exception as exc:
            DB.session.rollback()
            CustomErrorHandler.error_handler(hata="Satinalma ile ilgili işlem yapılırken bir hata oluştu"
                                                  "Satinalma:{}, User:{}, Hata:{}".format(
                                                 satinalma_id, current_user.username, exc))

            return jsonify(status="error", template=None), 500
