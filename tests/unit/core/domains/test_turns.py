from pipe.core.domains.turns import (
    ExpiredToolResponse,
    delete_turns,
    expire_old_tool_responses,
    get_turns_for_prompt,
)
from pipe.core.models.turn import ToolResponseTurn

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.turn_factory import TurnFactory


class TestDeleteTurns:
    """Tests for delete_turns function."""

    def test_delete_multiple_turns(self):
        """Test deleting multiple turns handles index shifts correctly."""
        session = SessionFactory.create_with_turns(turn_count=5)
        # Original turns: [0, 1, 2, 3, 4]
        # Delete indices 1 and 3
        delete_turns(session, [1, 3])

        assert len(session.turns) == 3
        # Indices 1 and 3 were deleted.
        # Original 0 remains at 0
        # Original 2 moves to 1
        # Original 4 moves to 2
        assert session.turns[0].instruction == "Instruction 0"
        assert session.turns[1].instruction == "Instruction 2"
        assert session.turns[2].instruction == "Instruction 4"

    def test_delete_turns_empty_indices(self):
        """Test delete_turns with empty indices list."""
        session = SessionFactory.create_with_turns(turn_count=3)
        delete_turns(session, [])
        assert len(session.turns) == 3

    def test_delete_turns_single_index(self):
        """Test delete_turns with a single index."""
        session = SessionFactory.create_with_turns(turn_count=3)
        delete_turns(session, [1])
        assert len(session.turns) == 2
        assert session.turns[0].instruction == "Instruction 0"
        assert session.turns[1].instruction == "Instruction 2"


class TestGetTurnsForPrompt:
    """Tests for get_turns_for_prompt function."""

    def test_get_turns_within_limit(self):
        """Test yielding turns when tool responses are within limit."""
        turns = [
            TurnFactory.create_user_task(instruction="Task 1"),
            TurnFactory.create_model_response(content="Response 1"),
            TurnFactory.create_tool_response(name="tool1"),
            TurnFactory.create_user_task(instruction="Task 2"),
        ]
        # Note: get_turns_for_prompt yields turns in reverse order because it iterates reversed(turns_collection)
        # Wait, the implementation is:
        # for turn in reversed(turns_collection):
        #     ...
        #     yield turn
        # So it yields from last to first.

        result = list(get_turns_for_prompt(turns, tool_response_limit=3))

        assert len(result) == 4
        assert result[0].instruction == "Task 2"
        assert result[1].name == "tool1"
        assert result[2].content == "Response 1"
        assert result[3].instruction == "Task 1"

    def test_get_turns_exceeding_limit(self):
        """Test filtering tool responses when they exceed the limit."""
        turns = [
            TurnFactory.create_tool_response(
                name="tool_old", timestamp="2025-01-01T00:00:00Z"
            ),
            TurnFactory.create_user_task(instruction="Task 1"),
            TurnFactory.create_tool_response(
                name="tool1", timestamp="2025-01-01T00:01:00Z"
            ),
            TurnFactory.create_tool_response(
                name="tool2", timestamp="2025-01-01T00:02:00Z"
            ),
            TurnFactory.create_tool_response(
                name="tool3", timestamp="2025-01-01T00:03:00Z"
            ),
            TurnFactory.create_user_task(instruction="Task 2"),
        ]
        # Limit is 2. Last 2 tool responses are tool3 and tool2.
        # tool1 and tool_old should be excluded.

        result = list(get_turns_for_prompt(turns, tool_response_limit=2))

        # Expected order (reverse): Task 2, tool3, tool2, Task 1
        assert len(result) == 4
        assert result[0].instruction == "Task 2"
        assert result[1].name == "tool3"
        assert result[2].name == "tool2"
        assert result[3].instruction == "Task 1"

        # Verify tool1 and tool_old are NOT in result
        names = [t.name for t in result if isinstance(t, ToolResponseTurn)]
        assert "tool1" not in names
        assert "tool_old" not in names


class TestExpireOldToolResponses:
    """Tests for expire_old_tool_responses function."""

    def test_expire_old_responses_success(self):
        """Test expiring tool responses older than the threshold user task."""
        # Threshold = 2. 2nd last user task is "Task 2" at 00:02:00.
        # tool_old (00:00:00) < 00:02:00 and status is "succeeded" -> Expire
        # tool_recent (00:02:30) > 00:02:00 -> Keep
        turns = [
            TurnFactory.create_tool_response(
                name="tool_old",
                status="succeeded",
                timestamp="2025-01-01T00:00:00Z",
            ),
            TurnFactory.create_user_task(
                instruction="Task 1", timestamp="2025-01-01T00:01:00Z"
            ),
            TurnFactory.create_user_task(
                instruction="Task 2", timestamp="2025-01-01T00:02:00Z"
            ),
            TurnFactory.create_tool_response(
                name="tool_recent",
                status="succeeded",
                timestamp="2025-01-01T00:02:30Z",
            ),
            TurnFactory.create_user_task(
                instruction="Task 3", timestamp="2025-01-01T00:03:00Z"
            ),
        ]
        from pipe.core.collections.turns import TurnCollection

        collection = TurnCollection(turns)

        modified = expire_old_tool_responses(collection, expiration_threshold=2)

        assert modified is True
        assert isinstance(collection[0].response, ExpiredToolResponse)
        assert collection[0].response.status == "succeeded"
        assert "expired" in collection[0].response.message

        assert collection[3].name == "tool_recent"
        assert not isinstance(collection[3].response, ExpiredToolResponse)
        assert collection[3].response.status == "succeeded"

    def test_expire_old_responses_no_user_tasks(self):
        """Test expire_old_tool_responses with no user tasks."""
        turns = [
            TurnFactory.create_tool_response(name="tool1"),
        ]
        from pipe.core.collections.turns import TurnCollection

        collection = TurnCollection(turns)
        assert expire_old_tool_responses(collection) is False

    def test_get_turns_for_prompt_no_tool_responses(self):
        """Test get_turns_for_prompt when there are no tool responses."""
        turns = [
            TurnFactory.create_user_task(instruction="Task 1"),
            TurnFactory.create_model_response(content="Response 1"),
        ]
        result = list(get_turns_for_prompt(turns))
        assert len(result) == 2
        assert result[0].content == "Response 1"
        assert result[1].instruction == "Task 1"

    def test_no_expiration_below_threshold(self):
        """Test no expiration occurs if user task count is below threshold."""
        turns = [
            TurnFactory.create_tool_response(
                name="tool1", timestamp="2025-01-01T00:00:00Z"
            ),
            TurnFactory.create_user_task(
                instruction="Task 1", timestamp="2025-01-01T00:01:00Z"
            ),
        ]
        from pipe.core.collections.turns import TurnCollection

        collection = TurnCollection(turns)

        modified = expire_old_tool_responses(collection, expiration_threshold=2)

        assert modified is False
        assert not isinstance(collection[0].response, ExpiredToolResponse)

    def test_only_expire_succeeded_responses(self):
        """Test that only 'succeeded' tool responses are expired."""
        # Threshold = 1. Last user task is "Task 1" at 00:01:00.
        # tool_failed (00:00:00) < 00:01:00 but status is "failed" -> Keep
        turns = [
            TurnFactory.create_tool_response(
                name="tool_failed", status="failed", timestamp="2025-01-01T00:00:00Z"
            ),
            TurnFactory.create_user_task(
                instruction="Task 1", timestamp="2025-01-01T00:01:00Z"
            ),
            TurnFactory.create_user_task(
                instruction="Task 2", timestamp="2025-01-01T00:02:00Z"
            ),
        ]
        from pipe.core.collections.turns import TurnCollection

        collection = TurnCollection(turns)

        modified = expire_old_tool_responses(collection, expiration_threshold=1)

        assert modified is False
        assert collection[0].response.status == "failed"
        assert not isinstance(collection[0].response, ExpiredToolResponse)

    def test_empty_collection(self):
        """Test expire_old_tool_responses with empty collection."""
        from pipe.core.collections.turns import TurnCollection

        collection = TurnCollection([])
        assert expire_old_tool_responses(collection) is False
