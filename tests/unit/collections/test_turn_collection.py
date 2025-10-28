import unittest
from unittest.mock import Mock

from pipe.core.collections.turns import TurnCollection
from pipe.core.models.turn import ToolResponseTurn, UserTaskTurn


class TestTurnCollection(unittest.TestCase):
    def test_expire_old_tool_responses_in_session(self):
        """
        Tests that the static method correctly expires old tool responses.
        """
        mock_session = Mock()
        mock_session.turns = TurnCollection(
            [
                UserTaskTurn(
                    type="user_task", instruction="1", timestamp="2025-01-01T00:00:00Z"
                ),
                ToolResponseTurn(
                    type="tool_response",
                    name="dummy_tool",
                    response={"status": "succeeded", "message": "old"},
                    timestamp="2025-01-01T00:01:00Z",
                ),
                UserTaskTurn(
                    type="user_task", instruction="2", timestamp="2025-01-02T00:00:00Z"
                ),
                UserTaskTurn(
                    type="user_task", instruction="3", timestamp="2025-01-03T00:00:00Z"
                ),
                UserTaskTurn(
                    type="user_task", instruction="4", timestamp="2025-01-04T00:00:00Z"
                ),
                ToolResponseTurn(
                    type="tool_response",
                    name="dummy_tool",
                    response={"status": "succeeded", "message": "recent"},
                    timestamp="2025-01-04T00:01:00Z",
                ),
            ]
        )

        modified = TurnCollection.expire_old_tool_responses(mock_session)

        self.assertTrue(modified)
        self.assertEqual(len(mock_session.turns), 6)
        self.assertEqual(
            mock_session.turns[1].response["message"],
            "This tool response has expired to save tokens.",
        )
        self.assertEqual(mock_session.turns[5].response["message"], "recent")

    def test_expire_old_tool_responses_no_change(self):
        """
        Tests that the method returns False when no turns are expired.
        """
        mock_session = Mock()
        mock_session.turns = TurnCollection(
            [
                UserTaskTurn(
                    type="user_task", instruction="1", timestamp="2025-01-01T00:00:00Z"
                ),
                UserTaskTurn(
                    type="user_task", instruction="2", timestamp="2025-01-02T00:00:00Z"
                ),
            ]
        )

        modified = TurnCollection.expire_old_tool_responses(mock_session)
        self.assertFalse(modified)


if __name__ == "__main__":
    unittest.main()
