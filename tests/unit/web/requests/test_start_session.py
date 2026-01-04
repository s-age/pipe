"""Unit tests for StartSessionRequest model."""

from unittest.mock import patch

import pytest
from pipe.web.requests.sessions.start_session import StartSessionRequest
from pydantic import ValidationError


class TestStartSessionRequest:
    """Tests for the StartSessionRequest model."""

    def test_valid_initialization_full(self):
        """Test initialization with all fields provided."""
        data = {
            "purpose": "Test purpose",
            "background": "Test background",
            "instruction": "Test instruction",
            "roles": ["role1.md"],
            "parent": "parent-session-id",
            "references": [{"path": "ref1.txt", "disabled": False}],
            "artifacts": ["artifact1.txt"],
            "procedure": "procedure.md",
            "multi_step_reasoning_enabled": True,
            "hyperparameters": {"temperature": 0.7, "top_p": 0.9, "top_k": 40},
        }
        # Mocking file existence checks to avoid real I/O
        with (
            patch(
                "pipe.web.requests.sessions.start_session.validate_list_of_files_exist"
            ),
            patch(
                "pipe.web.requests.sessions.start_session.os.path.isfile",
                return_value=True,
            ),
        ):
            request = StartSessionRequest.model_validate(data)

        assert request.purpose == "Test purpose"
        assert request.background == "Test background"
        assert request.instruction == "Test instruction"
        assert request.roles == ["role1.md"]
        assert request.parent == "parent-session-id"
        assert len(request.references) == 1
        assert request.references[0].path == "ref1.txt"
        assert request.artifacts == ["artifact1.txt"]
        assert request.procedure == "procedure.md"
        assert request.multi_step_reasoning_enabled is True
        assert request.hyperparameters.temperature == 0.7

    def test_valid_initialization_minimal(self):
        """Test initialization with only required fields."""
        data = {
            "purpose": "Test purpose",
            "background": "Test background",
            "instruction": "Test instruction",
        }
        request = StartSessionRequest.model_validate(data)
        assert request.purpose == "Test purpose"
        assert request.roles is None
        assert request.multi_step_reasoning_enabled is False

    def test_camel_case_normalization(self):
        """Test that camelCase keys are normalized to snake_case."""
        data = {
            "purpose": "Test purpose",
            "background": "Test background",
            "instruction": "Test instruction",
            "multiStepReasoningEnabled": True,
        }
        request = StartSessionRequest.model_validate(data)
        assert request.multi_step_reasoning_enabled is True

    @pytest.mark.parametrize("field_name", ["purpose", "background", "instruction"])
    def test_empty_required_fields(self, field_name):
        """Test that empty or whitespace-only required fields raise ValidationError."""
        base_data = {
            "purpose": "Test purpose",
            "background": "Test background",
            "instruction": "Test instruction",
        }

        # Test empty string
        data = base_data.copy()
        data[field_name] = ""
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest.model_validate(data)
        assert f"{field_name} must not be empty." in str(exc_info.value)

        # Test whitespace string
        data[field_name] = "   "
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest.model_validate(data)
        assert f"{field_name} must not be empty." in str(exc_info.value)

    @patch("pipe.web.requests.sessions.start_session.validate_list_of_files_exist")
    def test_validate_roles_exist(self, mock_validate):
        """Test that roles validation calls validate_list_of_files_exist."""
        data = {
            "purpose": "P",
            "background": "B",
            "instruction": "I",
            "roles": ["role1.md", "role2.md"],
        }
        StartSessionRequest.model_validate(data)
        mock_validate.assert_called_once_with(["role1.md", "role2.md"])

    @patch("pipe.web.requests.sessions.start_session.validate_list_of_files_exist")
    def test_validate_references_exist(self, mock_validate):
        """Test that references validation calls validate_list_of_files_exist with paths."""
        data = {
            "purpose": "P",
            "background": "B",
            "instruction": "I",
            "references": [{"path": "ref1.txt"}, {"path": "ref2.txt"}],
        }
        StartSessionRequest.model_validate(data)
        mock_validate.assert_called_once_with(["ref1.txt", "ref2.txt"])

    @patch("pipe.web.requests.sessions.start_session.os.path.isfile")
    def test_validate_procedure_exists(self, mock_isfile):
        """Test procedure file existence validation."""
        base_data = {"purpose": "P", "background": "B", "instruction": "I"}

        # Valid file
        mock_isfile.return_value = True
        data = base_data.copy()
        data["procedure"] = "valid_path.md"
        request = StartSessionRequest.model_validate(data)
        assert request.procedure == "valid_path.md"
        mock_isfile.assert_called_with("valid_path.md")

        # Invalid file
        mock_isfile.return_value = False
        data["procedure"] = "invalid_path.md"
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest.model_validate(data)
        assert "File not found: 'invalid_path.md'" in str(exc_info.value)

        # None or empty (should pass without calling isfile)
        mock_isfile.reset_mock()
        StartSessionRequest.model_validate({**base_data, "procedure": None})
        mock_isfile.assert_not_called()

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored as per model_config."""
        data = {
            "purpose": "P",
            "background": "B",
            "instruction": "I",
            "extra_field": "should be ignored",
        }
        request = StartSessionRequest.model_validate(data)
        assert not hasattr(request, "extra_field")
