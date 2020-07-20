from sqlalchemy import desc

from zopsedu.bap.models.proje import Proje
from zopsedu.bap.models.proje_satinalma_talepleri import ProjeSatinAlmaTalebi
from zopsedu.lib.db import DB
from zopsedu.lib.satinalma_state_dispatcher import SatinalmaStateDispatcher
from zopsedu.models import AppState, AppAction, SablonTipi, Sablon
from zopsedu.models.helpers import StateTypes, ActionTypes


def get_satinalma_with_related_fields(satinalma_id):
    """
    Satinalma ile satinalma ve iliskili alanlari veritabanindan getiren method
    Args:
        satinalma (int): satinalma id

    Returns:
        satinalma instance

    """
    satinalma = DB.session.query(ProjeSatinAlmaTalebi).join(Proje, Proje.id == ProjeSatinAlmaTalebi.proje_id).filter(
        ProjeSatinAlmaTalebi.id == satinalma_id).first()

    return satinalma


def get_satinalma_next_states_info(satinalma_id):
    satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

    satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                    action_type=ActionTypes.satinalma,
                                                    entity_type=ProjeSatinAlmaTalebi,
                                                    entity=satinalma)

    possible_next_states = satinalma_dispatcher.possible_next_states_info()

    states_info = DB.session.query(AppState). \
        filter(AppState.state_code.in_(possible_next_states.possible_states)).all()

    return states_info


def get_satinalma_actions_info(satinalma_id):
    satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)
    satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                    action_type=ActionTypes.satinalma,
                                                    entity_type=ProjeSatinAlmaTalebi,
                                                    entity=satinalma)

    possible_actions = satinalma_dispatcher.possible_actions()

    actions_info = DB.session.query(AppAction).filter(
        AppAction.action_code.in_(possible_actions.possible_actions)).all()

    return actions_info


def get_templates_info(satinalma_id):
    satinalma = get_satinalma_with_related_fields(satinalma_id=satinalma_id)

    satinalma_dispatcher = SatinalmaStateDispatcher(state_type=StateTypes.satinalma,
                                                    action_type=ActionTypes.satinalma,
                                                    entity_type=ProjeSatinAlmaTalebi,
                                                    entity=satinalma)

    possible_templates = satinalma_dispatcher.possible_template_types()

    sablon = DB.session.query(Sablon).order_by(desc(Sablon.created_at)).subquery('sablon')

    templates_info = DB.session.query(sablon).filter(
        sablon.c.sablon_tipi_id.in_(possible_templates),
                         sablon.c.kullanilabilir_mi == True,
                         sablon.c.query_id != None).distinct(sablon.c.sablon_tipi_id).all()

    return templates_info
