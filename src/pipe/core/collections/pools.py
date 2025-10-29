from __future__ import annotations

from pipe.core.collections.turns import TurnCollection
from pipe.core.models.session import Session
from pipe.core.models.turn import Turn


class PoolCollection:
    """
    Provides utility methods for managing the 'pools' attribute of a Session.
    This class is a container for static methods and does not hold state itself.
    """

    @staticmethod
    def add(session: Session, turn_data: Turn):
        """Adds a turn to the session's pool. Does not save."""
        if session.pools is None:
            session.pools = TurnCollection()
        session.pools.append(turn_data)

    @staticmethod
    def get_and_clear(session: Session) -> list[Turn]:
        """
        Retrieves all turns from the pool, clears the pool, and returns the turns.
        Does not save the session.
        """
        if not session.pools:
            return []

        pools_to_return = session.pools.copy()
        session.pools = TurnCollection()
        return pools_to_return
