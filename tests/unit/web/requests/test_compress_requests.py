"""Unit tests for compressor request models."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.requests.compress_requests import (
    ApproveCompressorRequest,
    CreateCompressorRequest,
    DenyCompressorRequest,
)
from pydantic import ValidationError


class TestCreateCompressorRequest:
    """Tests for the CreateCompressorRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_request(self, mock_get_service):
        """Test initialization with valid data."""
        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 10
        mock_get_service.return_value.get_session.return_value = mock_session

        request = CreateCompressorRequest(
            session_id="test-session",
            policy="standard",
            target_length=1000,
            start_turn=1,
            end_turn=5,
        )
        assert request.session_id == "test-session"
        assert request.policy == "standard"
        assert request.target_length == 1000
        assert request.start_turn == 1
        assert request.end_turn == 5

    @patch("pipe.web.service_container.get_session_service")
    def test_invalid_turns_positive(self, mock_get_service):
        """Test that non-positive turn numbers raise ValidationError."""
        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 10
        mock_get_service.return_value.get_session.return_value = mock_session

        with pytest.raises(ValidationError) as exc_info:
            CreateCompressorRequest(
                session_id="test-session",
                policy="standard",
                target_length=1000,
                start_turn=0,
                end_turn=5,
            )
        assert "Turn number must be >= 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            CreateCompressorRequest(
                session_id="test-session",
                policy="standard",
                target_length=1000,
                start_turn=1,
                end_turn=-1,
            )
        assert "Turn number must be >= 1" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_invalid_turn_range(self, mock_get_service):
        """Test that end_turn < start_turn raises ValidationError."""
        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 10
        mock_get_service.return_value.get_session.return_value = mock_session

        with pytest.raises(ValidationError) as exc_info:
            CreateCompressorRequest(
                session_id="test-session",
                policy="standard",
                target_length=1000,
                start_turn=5,
                end_turn=3,
            )
        assert "end_turn must be greater than or equal to start_turn" in str(
            exc_info.value
        )

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service):
        """Test that non-existent session_id raises ValidationError."""
        mock_get_service.return_value.get_session.return_value = None

        with pytest.raises(ValidationError) as exc_info:
            CreateCompressorRequest(
                session_id="non-existent",
                policy="standard",
                target_length=1000,
                start_turn=1,
                end_turn=5,
            )
        assert "Session 'non-existent' not found" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_turn_not_found(self, mock_get_service):
        """Test that turn numbers exceeding session length raise ValidationError."""
        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 3
        mock_get_service.return_value.get_session.return_value = mock_session

        with pytest.raises(ValidationError) as exc_info:
            CreateCompressorRequest(
                session_id="test-session",
                policy="standard",
                target_length=1000,
                start_turn=1,
                end_turn=5,
            )
        assert "Turn 5 does not exist in session (max: 3)" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_invalid_target_length(self, mock_get_service):
        """Test that non-positive target_length raises ValidationError."""
        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 10
        mock_get_service.return_value.get_session.get_session.return_value = (
            mock_session
        )

        with pytest.raises(ValidationError) as exc_info:
            CreateCompressorRequest(
                session_id="test-session",
                policy="standard",
                target_length=0,
                start_turn=1,
                end_turn=5,
            )
        assert "target_length must be positive" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service):
        """Test create_with_path_params method."""
        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 10
        mock_get_service.return_value.get_session.return_value = mock_session

        request = CreateCompressorRequest.create_with_path_params(
            path_params={},
            body_data={
                "session_id": "abc-123",
                "policy": "standard",
                "target_length": 1000,
                "start_turn": 1,
                "end_turn": 10,
            },
        )
        assert request.session_id == "abc-123"
        assert request.policy == "standard"


class TestApproveCompressorRequest:
    """Tests for the ApproveCompressorRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_request(self, mock_get_service):
        """Test initialization with valid session_id."""
        mock_get_service.return_value.get_session.return_value = MagicMock()

        request = ApproveCompressorRequest(session_id="test-session")
        assert request.session_id == "test-session"

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service):
        """Test that non-existent session_id raises ValidationError."""
        mock_get_service.return_value.get_session.return_value = None

        with pytest.raises(ValidationError) as exc_info:
            ApproveCompressorRequest(session_id="non-existent")
        assert "Session 'non-existent' not found" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service):
        """Test create_with_path_params method."""
        mock_get_service.return_value.get_session.return_value = MagicMock()

        request = ApproveCompressorRequest.create_with_path_params(
            path_params={"session_id": "abc-123"},
            body_data=None,
        )
        assert request.session_id == "abc-123"


class TestDenyCompressorRequest:
    """Tests for the DenyCompressorRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_request(self, mock_get_service):
        """Test initialization with valid session_id."""
        mock_get_service.return_value.get_session.return_value = MagicMock()

        request = DenyCompressorRequest(session_id="test-session")
        assert request.session_id == "test-session"

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service):
        """Test that non-existent session_id raises ValidationError."""
        mock_get_service.return_value.get_session.return_value = None

        with pytest.raises(ValidationError) as exc_info:
            DenyCompressorRequest(session_id="non-existent")
        assert "Session 'non-existent' not found" in str(exc_info.value)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service):
        """Test create_with_path_params method."""
        mock_get_service.return_value.get_session.return_value = MagicMock()

        request = DenyCompressorRequest.create_with_path_params(
            path_params={"session_id": "abc-123"},
            body_data=None,
        )
        assert request.session_id == "abc-123"
