from unittest.mock import patch

import pytest
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.turn import (
    ModelResponseTurn,
    ModelResponseTurnUpdate,
    UserTaskTurn,
    UserTaskTurnUpdate,
)

from tests.factories.models.turn_factory import TurnFactory


class TestTurnCollection:
    """Tests for TurnCollection."""

    def test_init_empty(self):
        """Test initializing an empty collection."""
        collection = TurnCollection()
        assert len(collection) == 0

    def test_init_with_list(self):
        """Test initializing with a list of turns."""
        turns = TurnFactory.create_batch(3)
        collection = TurnCollection(turns)
        assert len(collection) == 3
        assert collection[0] == turns[0]

    def test_add(self):
        """Test adding a turn."""
        collection = TurnCollection()
        turn = TurnFactory.create_user_task()
        collection.add(turn)
        assert len(collection) == 1
        assert collection[0] == turn

    def test_delete_by_index_success(self):
        """Test deleting a turn by index."""
        turns = TurnFactory.create_batch(3)
        collection = TurnCollection(turns)
        collection.delete_by_index(1)
        assert len(collection) == 2
        assert collection[0] == turns[0]
        assert collection[1] == turns[2]

    def test_delete_by_index_out_of_range(self):
        """Test deleting a turn with out of range index."""
        collection = TurnCollection(TurnFactory.create_batch(2))
        with pytest.raises(IndexError, match="Turn index out of range"):
            collection.delete_by_index(5)

    def test_merge_from(self):
        """Test merging turns from another collection."""
        col1 = TurnCollection(TurnFactory.create_batch(2))
        col2 = TurnCollection(TurnFactory.create_batch(2))
        col1.merge_from(col2)
        assert len(col1) == 4
        assert col1[2] == col2[0]

    def test_edit_by_index_user_task(self):
        """Test editing a user task turn."""
        turn = TurnFactory.create_user_task(instruction="Old")
        collection = TurnCollection([turn])

        update = UserTaskTurnUpdate(instruction="New")
        collection.edit_by_index(0, update)

        assert collection[0].instruction == "New"
        assert collection[0].timestamp == turn.timestamp
        assert isinstance(collection[0], UserTaskTurn)

    def test_edit_by_index_model_response(self):
        """Test editing a model response turn."""
        turn = TurnFactory.create_model_response(content="Old")
        collection = TurnCollection([turn])

        update = ModelResponseTurnUpdate(content="New")
        collection.edit_by_index(0, update)

        assert collection[0].content == "New"
        assert isinstance(collection[0], ModelResponseTurn)

    def test_edit_by_index_with_dict(self):
        """Test editing with a dictionary instead of DTO."""
        turn = TurnFactory.create_user_task(instruction="Old")
        collection = TurnCollection([turn])

        collection.edit_by_index(0, {"instruction": "New"})
        assert collection[0].instruction == "New"

    def test_edit_by_index_out_of_range(self):
        """Test editing with out of range index."""
        collection = TurnCollection(TurnFactory.create_batch(1))
        with pytest.raises(IndexError, match="Turn index out of range"):
            collection.edit_by_index(5, {"instruction": "New"})

    def test_edit_by_index_invalid_type(self):
        """Test editing a turn type that is not allowed."""
        turn = TurnFactory.create_function_calling()
        collection = TurnCollection([turn])

        with pytest.raises(
            ValueError, match="Editing turns of type 'function_calling' is not allowed"
        ):
            collection.edit_by_index(0, {"response": "New"})

    @patch("pipe.core.domains.turns.get_turns_for_prompt")
    def test_get_turns_for_prompt(self, mock_domain_func):
        """Test get_turns_for_prompt delegates to domain function."""
        collection = TurnCollection(TurnFactory.create_batch(2))
        mock_domain_func.return_value = iter(collection)

        result = list(collection.get_turns_for_prompt(tool_response_limit=5))

        mock_domain_func.assert_called_once_with(collection, 5)
        assert result == list(collection)

    def test_pydantic_validation(self):
        """Test Pydantic validation and serialization."""
        from pydantic import RootModel

        turns_data = [
            {
                "type": "user_task",
                "instruction": "Hi",
                "timestamp": "2025-01-01T00:00:00+09:00",
            },
            {
                "type": "model_response",
                "content": "Hello",
                "timestamp": "2025-01-01T00:01:00+09:00",
            },
        ]

        # Test validation from list of dicts
        class Model(RootModel):
            root: TurnCollection

        model = Model.model_validate(turns_data)
        assert isinstance(model.root, TurnCollection)
        assert len(model.root) == 2
        assert model.root[0].instruction == "Hi"

        # Test serialization
        dump = model.model_dump(exclude_none=True)
        assert dump == turns_data
