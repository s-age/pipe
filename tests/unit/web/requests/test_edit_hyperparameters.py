"""Unit tests for EditHyperparametersRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.edit_hyperparameters import EditHyperparametersRequest
from pydantic import ValidationError


class TestEditHyperparametersRequest:
    """Tests for the EditHyperparametersRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_full_initialization(self, mock_get_service: MagicMock) -> None:
        """Test initialization with all fields provided."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        data = {
            "session_id": "test-session",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
        }
        request = EditHyperparametersRequest(**data)

        assert request.session_id == "test-session"
        assert request.temperature == 0.7
        assert request.top_p == 0.9
        assert request.top_k == 40

    @patch("pipe.web.service_container.get_session_service")
    def test_partial_initialization(self, mock_get_service: MagicMock) -> None:
        """Test initialization with only one hyperparameter."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        request = EditHyperparametersRequest(session_id="test-session", temperature=0.5)
        assert request.temperature == 0.5
        assert request.top_p is None
        assert request.top_k is None

    @patch("pipe.web.service_container.get_session_service")
    def test_camel_case_normalization(self, mock_get_service: MagicMock) -> None:
        """Test that camelCase keys are normalized to snake_case."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        data = {
            "session_id": "test-session",
            "topP": 0.8,
            "topK": 50,
        }
        request = EditHyperparametersRequest(**data)
        assert request.top_p == 0.8
        assert request.top_k == 50

    def test_missing_hyperparameters_raises_error(self) -> None:
        """Test that providing no hyperparameters raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditHyperparametersRequest(session_id="test-session")

        assert (
            "At least one of ['temperature', 'top_p', 'top_k'] must be provided."
            in str(exc_info.value)
        )

    @pytest.mark.parametrize("field", ["temperature", "top_p", "top_k"])
    def test_null_values_raise_error(self, field: str) -> None:
        """Test that null values for hyperparameters are disallowed."""
        data = {"session_id": "test-session", field: None}
        with pytest.raises(ValidationError) as exc_info:
            EditHyperparametersRequest(**data)

        assert f"'{field}' cannot be null." in str(exc_info.value)

    @pytest.mark.parametrize("value", [-0.1, "not-a-number"])
    def test_temperature_validation(self, value: float | str) -> None:
        """Test temperature range and type validation."""
        data = {"session_id": "test-session", "temperature": value}
        with pytest.raises(ValidationError) as exc_info:
            EditHyperparametersRequest(**data)

        if isinstance(value, int | float):
            assert "'temperature' must be >= 0." in str(exc_info.value)
        else:
            assert "'temperature' must be a number." in str(exc_info.value)

    @pytest.mark.parametrize("value", [-0.1, 1.1, "not-a-number"])
    def test_top_p_validation(self, value: float | str) -> None:
        """Test top_p range and type validation."""
        data = {"session_id": "test-session", "top_p": value}
        with pytest.raises(ValidationError) as exc_info:
            EditHyperparametersRequest(**data)

        if isinstance(value, int | float):
            assert "'top_p' must be between 0.0 and 1.0." in str(exc_info.value)
        else:
            assert "'top_p' must be a number between 0.0 and 1.0." in str(
                exc_info.value
            )

    @pytest.mark.parametrize("value", [-1, 10.5, "not-a-number"])
    def test_top_k_validation(self, value: int | float | str) -> None:
        """Test top_k range and type validation."""
        data = {"session_id": "test-session", "top_k": value}
        with pytest.raises(ValidationError) as exc_info:
            EditHyperparametersRequest(**data)

        if isinstance(value, int):
            assert "'top_k' must be >= 0." in str(exc_info.value)
        else:
            assert "'top_k' must be an integer >= 0." in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found_raises_error(self, mock_get_service: MagicMock) -> None:
        """Test that NotFoundError is raised if session does not exist."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = None

        with pytest.raises(NotFoundError, match="Session not found."):
            EditHyperparametersRequest(session_id="non-existent", temperature=0.5)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service: MagicMock) -> None:
        """Test creating request with path parameters and body data."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "path-session"}

        path_params = {"session_id": "path-session"}
        body_data = {"temperature": 0.8}

        request = EditHyperparametersRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "path-session"
        assert request.temperature == 0.8

    def test_invalid_body_type(self) -> None:
        """Test that non-dict body raises an error."""
        with pytest.raises(ValidationError) as exc_info:
            EditHyperparametersRequest.model_validate(["not", "a", "dict"])

        assert "Request body must be a JSON object." in str(exc_info.value)
