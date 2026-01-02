"""Unit tests for RoleCollection."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.collections.roles import RoleCollection
from pipe.core.repositories.resource_repository import ResourceRepository


class TestRoleCollectionInit:
    """Tests for RoleCollection.__init__."""

    def test_init_with_paths(self):
        """Test initialization with a list of paths."""
        paths = ["roles/role1.md", "roles/role2.md"]
        collection = RoleCollection(paths)
        assert collection._role_paths == paths

    def test_init_with_none(self):
        """Test initialization with None (should default to empty list)."""
        collection = RoleCollection(None)  # type: ignore
        assert collection._role_paths == []


class TestRoleCollectionGetForPrompt:
    """Tests for RoleCollection.get_for_prompt."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for a mock ResourceRepository."""
        repo = MagicMock(spec=ResourceRepository)
        repo.project_root = "/mock/project/root"
        return repo

    def test_get_for_prompt_success(self, mock_repo):
        """Test loading content for valid role paths."""
        paths = ["role1.md", "role2.md"]
        collection = RoleCollection(paths)

        mock_repo.exists.return_value = True
        mock_repo.read_text.side_effect = ["Content 1", "Content 2"]

        contents = collection.get_for_prompt(mock_repo)

        assert contents == ["Content 1", "Content 2"]
        assert mock_repo.exists.call_count == 2
        assert mock_repo.read_text.call_count == 2

    def test_get_for_prompt_with_stripping(self, mock_repo):
        """Test that paths are stripped before joining."""
        paths = ["  role1.md  ", "\nrole2.md\t"]
        collection = RoleCollection(paths)

        mock_repo.exists.return_value = True
        mock_repo.read_text.side_effect = ["Content 1", "Content 2"]

        with patch("pipe.core.collections.roles.os.path.join") as mock_join:
            mock_join.side_effect = lambda root, path: f"{root}/{path}"
            collection.get_for_prompt(mock_repo)

            # Verify join was called with stripped paths
            mock_join.assert_any_call("/mock/project/root", "role1.md")
            mock_join.assert_any_call("/mock/project/root", "role2.md")

    def test_get_for_prompt_skips_missing_files(self, mock_repo):
        """Test that missing files are skipped."""
        paths = ["exists.md", "missing.md"]
        collection = RoleCollection(paths)

        def exists_side_effect(path, allowed_root):
            return "exists.md" in path

        mock_repo.exists.side_effect = exists_side_effect
        mock_repo.read_text.return_value = "Content"

        contents = collection.get_for_prompt(mock_repo)

        assert contents == ["Content"]
        assert mock_repo.read_text.call_count == 1

    def test_get_for_prompt_empty_collection(self, mock_repo):
        """Test behavior with an empty collection."""
        collection = RoleCollection([])
        contents = collection.get_for_prompt(mock_repo)
        assert contents == []
        mock_repo.exists.assert_not_called()
