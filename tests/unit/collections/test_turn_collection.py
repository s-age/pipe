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

        modified = mock_session.turns.expire_old_tool_responses()

        self.assertTrue(modified)
        self.assertEqual(len(mock_session.turns), 6)
        self.assertEqual(
            mock_session.turns[1].response["message"],
            "This tool response has expired to save tokens.",
        )
        self.assertEqual(mock_session.turns[5].response["message"], "recent")

    def test_expire_old_tool_responses_no_change_due_to_threshold(self):
        """
        Tests that the method returns False when no turns are expired because
        the number of user_tasks is below the threshold.
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
            ]
        )

        modified = mock_session.turns.expire_old_tool_responses()
        self.assertFalse(modified)
        self.assertEqual(mock_session.turns[1].response["message"], "old")

    def test_expire_old_tool_responses_empty_collection(self):
        """
        Tests that the method returns False for an empty collection.
        """
        turns = TurnCollection()
        modified = turns.expire_old_tool_responses()
        self.assertFalse(modified)

    def test_get_for_prompt_limits_tool_responses(self):
        """
        Tests that get_for_prompt correctly limits the number of tool responses.
        """
        turns = TurnCollection(
            [
                ToolResponseTurn(
                    type="tool_response", name="t1", response={}, timestamp="1"
                ),
                ToolResponseTurn(
                    type="tool_response", name="t2", response={}, timestamp="2"
                ),
                ToolResponseTurn(
                    type="tool_response", name="t3", response={}, timestamp="3"
                ),
                ToolResponseTurn(
                    type="tool_response", name="t4", response={}, timestamp="4"
                ),
                UserTaskTurn(type="user_task", instruction="last", timestamp="5"),
            ]
        )

        # Default limit is 3
        prompt_turns = list(turns.get_for_prompt())

        # Should get t4, t3, t2 in reverse order of yield
        self.assertEqual(len(prompt_turns), 3)
        self.assertEqual(prompt_turns[0].name, "t4")
        self.assertEqual(prompt_turns[1].name, "t3")
        self.assertEqual(prompt_turns[2].name, "t2")

    def test_get_for_prompt_excludes_last_turn(self):
        """
        Tests that get_for_prompt excludes the last turn (current task).
        """
        turns = TurnCollection(
            [
                UserTaskTurn(type="user_task", instruction="first", timestamp="1"),
                UserTaskTurn(type="user_task", instruction="last", timestamp="2"),
            ]
        )

        prompt_turns = list(turns.get_for_prompt())

        self.assertEqual(len(prompt_turns), 1)
        self.assertEqual(prompt_turns[0].instruction, "first")

    def test_pydantic_json_schema(self):
        """
        Tests the __get_pydantic_json_schema__ method for correct schema generation.
        """
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            turns: TurnCollection = Field(default_factory=TurnCollection)

        schema = TestModel.model_json_schema()

        defs_key = "$defs" if "$defs" in schema else "definitions"
        self.assertIn(defs_key, schema)
        # Pydantic v2 generates schemas for each subtype in the union,
        # not the union type itself.
        self.assertIn("UserTaskTurn", schema[defs_key])
        self.assertIn("ModelResponseTurn", schema[defs_key])

        props = schema["properties"]
        self.assertIn("turns", props)
        self.assertEqual(props["turns"]["type"], "array")

        items_schema = props["turns"]["items"]
        self.assertIn("oneOf", items_schema)

        # Check that at least one of the refs is correct
        one_of_refs = [item["$ref"] for item in items_schema["oneOf"]]
        self.assertIn(f"#/{defs_key}/UserTaskTurn", one_of_refs)

    def test_expire_old_tool_responses_no_change_due_to_status(self):
        """
        Tests that no turns are expired if their status is not 'succeeded'.
        """
        turns = TurnCollection(
            [
                UserTaskTurn(type="user_task", instruction="1", timestamp="1"),
                ToolResponseTurn(
                    type="tool_response",
                    name="t",
                    response={"status": "failed"},
                    timestamp="2",
                ),
                UserTaskTurn(type="user_task", instruction="2", timestamp="3"),
                UserTaskTurn(type="user_task", instruction="3", timestamp="4"),
                UserTaskTurn(type="user_task", instruction="4", timestamp="5"),
            ]
        )
        modified = turns.expire_old_tool_responses()
        self.assertFalse(modified)


if __name__ == "__main__":
    unittest.main()
