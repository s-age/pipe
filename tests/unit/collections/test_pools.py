import unittest
from unittest.mock import Mock

from pipe.core.collections.pools import PoolCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.turn import UserTaskTurn


class TestPoolCollection(unittest.TestCase):
    def test_add(self):
        """
        Tests that the static method add correctly adds a turn to the session's pool.
        """
        mock_session = Mock()
        mock_session.pools = TurnCollection()
        new_turn = UserTaskTurn(
            type="user_task", instruction="New pool task", timestamp="dummy_timestamp"
        )

        PoolCollection.add(mock_session, new_turn)

        self.assertEqual(len(mock_session.pools), 1)
        self.assertEqual(mock_session.pools[0], new_turn)

    def test_add_to_none_pool(self):
        """
        Tests that 'add' correctly initializes the pool if it is None.
        """
        mock_session = Mock()
        mock_session.pools = None
        new_turn = UserTaskTurn(
            type="user_task", instruction="New pool task", timestamp="dummy_timestamp"
        )

        PoolCollection.add(mock_session, new_turn)

        self.assertIsNotNone(mock_session.pools)
        # Explicitly cast to TurnCollection for mypy
        pools: TurnCollection = mock_session.pools
        self.assertEqual(len(pools), 1)
        self.assertEqual(pools[0], new_turn)

    def test_get_and_clear(self):
        """
        Tests that get_and_clear returns the pool's content and clears the pool.
        """
        mock_session = Mock()
        turn1 = UserTaskTurn(
            type="user_task", instruction="Task 1", timestamp="dummy_timestamp"
        )
        turn2 = UserTaskTurn(
            type="user_task", instruction="Task 2", timestamp="dummy_timestamp"
        )
        mock_session.pools = TurnCollection([turn1, turn2])

        returned_pools = PoolCollection.get_and_clear(mock_session)

        self.assertEqual(len(returned_pools), 2)
        self.assertEqual(returned_pools[0], turn1)
        self.assertEqual(len(mock_session.pools), 0)

    def test_get_and_clear_empty_pool(self):
        """
        Tests that get_and_clear returns an empty list for an empty pool.
        """
        mock_session = Mock()
        mock_session.pools = TurnCollection()

        returned_pools = PoolCollection.get_and_clear(mock_session)

        self.assertEqual(len(returned_pools), 0)
        self.assertEqual(len(mock_session.pools), 0)


if __name__ == "__main__":
    unittest.main()
