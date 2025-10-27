import unittest

from pipe.core.collections.prompts.turn_collection import PromptTurnCollection
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn


class TestPromptTurnCollection(unittest.TestCase):
    def test_get_turns_returns_all_turns(self):
        """
        Tests that get_turns correctly returns all turn data.
        (Current implementation does not yet filter by token count).
        """
        turns = [
            UserTaskTurn(
                type="user_task", instruction="Hello", timestamp="2023-01-01T12:00:00Z"
            ),
            ModelResponseTurn(
                type="model_response",
                content="Hi there!",
                timestamp="2023-01-01T12:01:00Z",
            ),
        ]

        collection = PromptTurnCollection(turns)
        prompt_turns = collection.get_turns()

        self.assertEqual(len(prompt_turns), 2)
        self.assertEqual(prompt_turns[0]["instruction"], "Hello")
        self.assertEqual(prompt_turns[1]["content"], "Hi there!")

    def test_get_turns_with_empty_list(self):
        """
        Tests that get_turns returns an empty list when initialized with an empty list.
        """
        collection = PromptTurnCollection([])
        prompt_turns = collection.get_turns()
        self.assertEqual(len(prompt_turns), 0)


if __name__ == "__main__":
    unittest.main()
