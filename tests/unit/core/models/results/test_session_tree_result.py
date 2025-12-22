"""Tests for SessionTreeResult and SessionTreeNode models."""

import pytest
from pipe.core.models.results.session_tree_result import (
    SessionTreeNode,
    SessionTreeResult,
)
from pydantic import ValidationError

from tests.helpers.results_factory import ResultFactory


class TestSessionTreeNode:
    """Tests for SessionTreeNode model."""

    def test_valid_creation(self):
        """Test creating a valid SessionTreeNode with default values."""
        overview = ResultFactory.create_session_overview(
            session_id="session-1", purpose="root"
        )
        node = ResultFactory.create_session_tree_node(
            session_id="session-1", overview=overview
        )
        assert node.session_id == "session-1"
        assert node.overview == overview
        assert node.overview.purpose == "root"
        assert node.children == []

    def test_nested_structure(self):
        """Test creating a nested SessionTreeNode structure."""
        child = ResultFactory.create_session_tree_node(session_id="child")
        parent = ResultFactory.create_session_tree_node(
            session_id="parent", children=[child]
        )
        assert len(parent.children) == 1
        assert parent.children[0].session_id == "child"

    def test_mutable_children(self):
        """Test that SessionTreeNode allows modification of children (frozen=False)."""
        node = ResultFactory.create_session_tree_node(session_id="node")
        child = ResultFactory.create_session_tree_node(session_id="child")

        # frozen=False allows appending to list or reassigning
        node.children.append(child)
        assert len(node.children) == 1

        node.children = []
        assert len(node.children) == 0

    def test_validation_error_missing_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            # overview and session_id are required, but here we test missing overview
            SessionTreeNode(session_id="test")


class TestSessionTreeResult:
    """Tests for SessionTreeResult model."""

    def test_valid_creation(self):
        """Test creating a valid SessionTreeResult."""
        overview = ResultFactory.create_session_overview(
            session_id="s1", purpose="test"
        )
        sessions = {"s1": overview}
        tree = [
            ResultFactory.create_session_tree_node(session_id="s1", overview=overview)
        ]

        result = SessionTreeResult(sessions=sessions, session_tree=tree)
        assert result.sessions == sessions
        assert len(result.session_tree) == 1
        assert result.session_tree[0].session_id == "s1"

    def test_frozen_config(self):
        """Test that SessionTreeResult is frozen and raises ValidationError on
        modification.
        """
        result = ResultFactory.create_session_tree_result()
        with pytest.raises(ValidationError):
            result.sessions = {}

    def test_roundtrip_serialization(self):
        """Test serialization and deserialization preserves data."""
        overview = ResultFactory.create_session_overview(
            session_id="s1", purpose="root"
        )
        original = ResultFactory.create_session_tree_result(
            sessions={"s1": overview},
            session_tree=[
                ResultFactory.create_session_tree_node(
                    session_id="s1",
                    overview=overview,
                    children=[
                        ResultFactory.create_session_tree_node(
                            session_id="s1-child",
                            overview=ResultFactory.create_session_overview(
                                session_id="s1-child"
                            ),
                        )
                    ],
                )
            ],
        )

        # Serialize
        json_str = original.model_dump_json()

        # Deserialize
        restored = SessionTreeResult.model_validate_json(json_str)

        assert restored.sessions["s1"].session_id == "s1"
        assert len(restored.session_tree) == 1
        assert restored.session_tree[0].session_id == "s1"
        assert len(restored.session_tree[0].children) == 1
        assert restored.session_tree[0].children[0].session_id == "s1-child"
