"""Unit tests for PoolCollection."""

from unittest.mock import MagicMock

from pipe.core.collections.pools import PoolCollection
from pipe.core.collections.turns import TurnCollection

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.turn_factory import TurnFactory


class TestPoolCollectionAdd:
    """Tests for PoolCollection.add method."""

    def test_add_to_none_pool(self) -> None:
        """Test adding a turn when session.pools is None."""
        # Use MagicMock to bypass Session Pydantic validation for None pools
        session = MagicMock()
        session.pools = None
        turn = TurnFactory.create_user_task()

        PoolCollection.add(session, turn)

        assert isinstance(session.pools, TurnCollection)
        assert len(session.pools) == 1
        assert session.pools[0] == turn

    def test_add_to_existing_pool(self) -> None:
        """Test adding a turn when session.pools already exists."""
        initial_turn = TurnFactory.create_model_response()
        session = SessionFactory.create(pools=TurnCollection([initial_turn]))
        new_turn = TurnFactory.create_user_task()

        PoolCollection.add(session, new_turn)

        assert len(session.pools) == 2
        assert session.pools[0] == initial_turn
        assert session.pools[1] == new_turn


class TestPoolCollectionGetAndClear:
    """Tests for PoolCollection.get_and_clear method."""

    def test_get_and_clear_none_pool(self) -> None:
        """Test get_and_clear when session.pools is None."""
        session = MagicMock()
        session.pools = None

        result = PoolCollection.get_and_clear(session)

        assert result == []
        assert session.pools is None

    def test_get_and_clear_empty_pool(self) -> None:
        """Test get_and_clear when session.pools is an empty TurnCollection."""
        session = SessionFactory.create(pools=TurnCollection())

        result = PoolCollection.get_and_clear(session)

        assert result == []
        assert isinstance(session.pools, TurnCollection)
        assert len(session.pools) == 0

    def test_get_and_clear_with_turns(self) -> None:
        """Test get_and_clear when session.pools has turns."""
        turns = TurnFactory.create_batch(2)
        session = SessionFactory.create(pools=TurnCollection(turns))

        result = PoolCollection.get_and_clear(session)

        assert len(result) == 2
        assert list(result) == turns
        assert isinstance(session.pools, TurnCollection)
        assert len(session.pools) == 0
