"""State transition object"""
from sqlalchemy import or_
from zopsedu.lib.db import DB


class ProjectStateChecker(object):
    """
    State transition class
    """
    def __init__(self, university_id):
        """
        Args:
            university_id (int):
        """
        self.university_id = university_id
        self.state_table = {}

        self.load_state_transition_table()

    def is_available_for(self, current_state, next_state):
        """
        Determines if the `current_state` is avaliable to pass to `next_state` or not.
        Args:
            current_state (str):
            next_state (str):

        Returns:
            bool
        """
        return next_state in self.state_table[current_state]

    def get_possible_next_states(self, current_state):
        """
        Gives the possible next states for `current_state`
        Args:
            current_state (str):

        Returns:
            list
        """
        return self.state_table[current_state][:]

    def load_state_transition_table(self):
        """
        Loads the state transition table from the query result.

        query = DB.session.query(ProjeDurumGecis).filter(
            or_(
                ProjeDurumGecis.universite_id == 0,
                ProjeDurumGecis.universite_id == self.university_id
            )
        )

        for pdurum in query:
            if pdurum.universite_id > 0 or pdurum.durum not in self.state_table:
                self.state_table[pdurum.durum] = pdurum.olasi_sonraki_durum

        """