from datetime import datetime, timedelta

from zopsedu.lib.db import DB
from zopsedu.lib.job_helpers.email_helpers import email_scheduler
from zopsedu.models import AppState, AppAction


class StateDispatcher:
    """
    entity_type: Class adıdır (Proje,Satinalma.vs..)
    entity: Instance adıdır
    """

    def __init__(self, state_type=None, action_type=None, entity_type=None, entity=None):
        self.state_type = state_type
        self.action_type = action_type
        self.entity_type = entity_type
        self.entity = entity

    def current_state_info(self):
        return DB.session.query(AppState).join(self.entity_type, self.entity_type.id == self.entity.id).filter(
            AppState.id == self.entity.durum_id, AppState.state_type == self.state_type).first()

    def possible_next_states_info(self):
        return DB.session.query(AppState.possible_states.label("possible_states")).filter(
            AppState.id == self.entity.durum_id,
            AppState.state_type == self.state_type).first()

    def possible_actions(self):
        return DB.session.query(AppState.possible_actions.label("possible_actions")).filter(
            AppState.id == self.entity.durum_id,
            AppState.state_type == self.action_type).first()

    def possible_template_types(self):
        return DB.session.query(AppState.possible_template_types).filter(
            AppState.id == self.entity.durum_id,
            AppState.state_type == self.action_type).first()[0]

    def do_action_checker(self, next_app_action_code):
        possible_actions = self.possible_actions()

        for action in possible_actions.possible_actions:
            if next_app_action_code == action:
                action_info = DB.session.query(AppAction.id.label("app_action_id"),
                                               AppAction.description.label("app_action_description")). \
                    filter(AppAction.action_code == action,AppAction.action_type == self.action_type).first()

                return action_info

        return None

    def state_change_checker(self, next_app_state_code):

        possible_next_states = self.possible_next_states_info()

        for next_state in possible_next_states.possible_states:
            if next_app_state_code == next_state:
                next_state_info = DB.session.query(AppState.id.label("app_state_id"),
                                                   AppState.description.label("app_state_description")). \
                    filter(AppState.state_code == next_state, AppState.state_type==self.state_type).first()

                return next_state_info

        return None

    @staticmethod
    def email_gonder(receiver_person_id=None, receiver_email=None, proje=None, subject=None,
                     content_text=None,
                     greeting_name=None):
        """
        yurutucunun mail adresi person modelinden alinir. birincil epostasi yoksa ikincil
        epostasi kullanilir.
        """
        if not receiver_email:
            receiver_email = proje.proje_yurutucu.person.birincil_eposta or proje.proje_yurutucu.person.ikincil_eposta
        if not receiver_person_id:
            receiver_person_id = proje.proje_yurutucu.person.id
        if not greeting_name:
            greeting_name = "{} {}".format(proje.proje_yurutucu.person.ad,
                                           proje.proje_yurutucu.person.soyad)

        email_scheduler(recipients=[{"email": receiver_email,
                                     "person_id": receiver_person_id}],
                        proje_id=proje.id, subject=subject,
                        greeting_name=greeting_name, content_text=content_text,
                        scheduler_params={"trigger": "date",
                                          "run_date": datetime.now() + timedelta(seconds=10)})

