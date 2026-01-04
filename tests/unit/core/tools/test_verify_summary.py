"""Unit tests for verify_summary tool."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.verification_result import (
    VerificationError,
    VerificationResult,
)
from pipe.core.models.settings import Settings
from pipe.core.tools.verify_summary import verify_summary


class TestVerifySummary:
    """Tests for verify_summary function."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock Settings object."""
        return MagicMock(spec=Settings)

    @pytest.fixture
    def mock_verification_result(self) -> VerificationResult:
        """Create a mock VerificationResult."""
        return VerificationResult(
            verification_status="pending_approval",
            verifier_session_id="verifier-123",
            message="Summary looks good",
            verifier_response="I have verified the summary.",
            next_action="Proceed to next step",
        )

    @patch("pipe.core.tools.verify_summary.ServiceFactory")
    def test_verify_summary_success(
        self,
        mock_service_factory_class: MagicMock,
        mock_settings: MagicMock,
        mock_verification_result: VerificationResult,
    ) -> None:
        """Test successful summary verification."""
        # Setup mocks
        mock_factory = mock_service_factory_class.return_value
        mock_service = mock_factory.create_verification_service.return_value
        mock_service.verify_summary.return_value = mock_verification_result

        # Execute
        result = verify_summary(
            session_id="test-session",
            start_turn=1,
            end_turn=5,
            summary_text="Test summary",
            settings=mock_settings,
            project_root="/tmp/project",
        )

        # Assertions
        assert result.is_success
        assert result.data == mock_verification_result
        assert result.error is None
        mock_service_factory_class.assert_called_once_with(
            "/tmp/project", mock_settings
        )
        mock_service.verify_summary.assert_called_once_with(
            "test-session", 1, 5, "Test summary"
        )

    @patch("pipe.core.tools.verify_summary.ServiceFactory")
    def test_verify_summary_verification_error(
        self,
        mock_service_factory_class: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """Test summary verification returning a VerificationError."""
        # Setup mocks
        mock_factory = mock_service_factory_class.return_value
        mock_service = mock_factory.create_verification_service.return_value
        verification_error = VerificationError(error="Summary is inaccurate")
        mock_service.verify_summary.return_value = verification_error

        # Execute
        result = verify_summary(
            session_id="test-session",
            start_turn=1,
            end_turn=5,
            summary_text="Test summary",
            settings=mock_settings,
            project_root="/tmp/project",
        )

        # Assertions
        assert not result.is_success
        assert result.data is None
        assert result.error == "Summary is inaccurate"

    @patch("pipe.core.tools.verify_summary.ServiceFactory")
    def test_verify_summary_unexpected_exception(
        self,
        mock_service_factory_class: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """Test summary verification handling unexpected exceptions."""
        # Setup mocks to raise an exception
        mock_service_factory_class.side_effect = Exception("Unexpected failure")

        # Execute
        result = verify_summary(
            session_id="test-session",
            start_turn=1,
            end_turn=5,
            summary_text="Test summary",
            settings=mock_settings,
            project_root="/tmp/project",
        )

        # Assertions
        assert not result.is_success
        assert result.data is None
        assert result.error is not None
        assert "An unexpected error occurred" in result.error
        assert "Unexpected failure" in result.error
