"""Unit tests for VerificationService."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.verification_result import (
    VerificationError,
    VerificationResult,
)
from pipe.core.models.turn import CompressedHistoryTurn
from pipe.core.services.verification_service import VerificationService

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.turn_factory import TurnFactory


@pytest.fixture
def mock_session_service():
    """Create a mock SessionService."""
    return MagicMock()


@pytest.fixture
def mock_session_turn_service():
    """Create a mock SessionTurnService."""
    return MagicMock()


@pytest.fixture
def mock_takt_agent():
    """Create a mock TaktAgent."""
    return MagicMock()


@pytest.fixture
def service(mock_session_service, mock_session_turn_service, mock_takt_agent):
    """Create a VerificationService instance with mocked dependencies."""
    return VerificationService(
        session_service=mock_session_service,
        session_turn_service=mock_session_turn_service,
        takt_agent=mock_takt_agent,
    )


class TestVerificationServiceInit:
    """Test VerificationService.__init__ method."""

    def test_init(
        self, mock_session_service, mock_session_turn_service, mock_takt_agent
    ):
        """Test that dependencies are correctly assigned."""
        service = VerificationService(
            session_service=mock_session_service,
            session_turn_service=mock_session_turn_service,
            takt_agent=mock_takt_agent,
        )
        assert service.session_service == mock_session_service
        assert service.session_turn_service == mock_session_turn_service
        assert service.takt_agent == mock_takt_agent


class TestVerificationServiceVerifySummary:
    """Test VerificationService.verify_summary method."""

    def test_verify_summary_success(self, service, mock_session_service):
        """Test successful verification flow."""
        session_id = "original-session"
        verifier_session_id = "verifier-session"
        summary_text = "Test summary"

        # Mock internal methods
        with (
            patch.object(service, "_prepare_verification_turns") as mock_prepare,
            patch.object(service, "_create_verifier_session") as mock_create,
            patch.object(service, "_run_verifier_agent") as mock_run,
            patch.object(service, "_parse_verification_result") as mock_parse,
        ):
            mock_prepare.return_value = []
            mock_session = MagicMock()
            mock_session.session_id = verifier_session_id
            mock_create.return_value = mock_session
            expected_result = VerificationResult(
                verification_status="pending_approval",
                verifier_session_id=verifier_session_id,
                verifier_response="Approved: ...",
                next_action="...",
            )
            mock_parse.return_value = expected_result

            result = service.verify_summary(session_id, 1, 3, summary_text)

            assert result == expected_result
            mock_prepare.assert_called_once_with(session_id, 1, 3, summary_text)
            mock_create.assert_called_once_with(session_id, [])
            mock_run.assert_called_once_with(verifier_session_id, session_id, 1, 3)
            mock_parse.assert_called_once_with(verifier_session_id, summary_text)
            # Verify cleanup
            mock_session_service.delete_session.assert_called_once_with(
                verifier_session_id
            )

    def test_verify_summary_value_error(self, service):
        """Test handling of ValueError."""
        with patch.object(
            service, "_prepare_verification_turns", side_effect=ValueError("Invalid")
        ):
            result = service.verify_summary("id", 1, 1, "summary")
            assert isinstance(result, VerificationError)
            assert result.error == "Invalid"

    def test_verify_summary_unexpected_error(self, service):
        """Test handling of unexpected exceptions."""
        with patch.object(
            service, "_prepare_verification_turns", side_effect=Exception("Boom")
        ):
            result = service.verify_summary("id", 1, 1, "summary")
            assert isinstance(result, VerificationError)
            assert "Unexpected error: Boom" in result.error

    def test_verify_summary_cleanup_failure(self, service, mock_session_service):
        """Test that cleanup failure doesn't affect the result."""
        session_id = "original-session"
        verifier_session_id = "verifier-session"

        with (
            patch.object(service, "_prepare_verification_turns"),
            patch.object(service, "_create_verifier_session") as mock_create,
            patch.object(service, "_run_verifier_agent"),
            patch.object(service, "_parse_verification_result") as mock_parse,
        ):
            mock_session = MagicMock()
            mock_session.session_id = verifier_session_id
            mock_create.return_value = mock_session
            mock_parse.return_value = MagicMock(spec=VerificationResult)

            # Cleanup fails
            mock_session_service.delete_session.side_effect = Exception("Delete failed")

            result = service.verify_summary(session_id, 1, 1, "summary")

            assert isinstance(result, VerificationResult)
            mock_session_service.delete_session.assert_called_once()


class TestVerificationServicePrepareVerificationTurns:
    """Test VerificationService._prepare_verification_turns method."""

    def test_prepare_verification_turns_success(self, service, mock_session_service):
        """Test successful preparation of turns."""
        session_id = "test-session"
        turns = TurnFactory.create_batch(5)
        session = SessionFactory.create(session_id=session_id, turns=turns)
        mock_session_service.get_session.return_value = session

        summary_text = "Summary"
        start_turn, end_turn = 2, 4  # Turns 2, 3, 4 (indices 1, 2, 3)

        with patch(
            "pipe.core.services.verification_service.get_current_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-01-01T12:00:00Z"
            result = service._prepare_verification_turns(
                session_id, start_turn, end_turn, summary_text
            )

            assert len(result) == 3  # 5 - 3 + 1
            assert isinstance(result[1], CompressedHistoryTurn)
            assert result[1].content == summary_text
            assert result[1].original_turns_range == [start_turn, end_turn]
            assert result[1].timestamp == "2025-01-01T12:00:00Z"
            # Verify original turns are preserved around the summary
            assert result[0] == turns[0]
            assert result[2] == turns[4]

    def test_prepare_verification_turns_session_not_found(
        self, service, mock_session_service
    ):
        """Test error when session is not found."""
        mock_session_service.get_session.return_value = None
        with pytest.raises(ValueError, match="Session with ID .* not found"):
            service._prepare_verification_turns("id", 1, 1, "summary")

    @pytest.mark.parametrize(
        "start, end, turn_count",
        [
            (0, 1, 3),  # Start too low
            (4, 4, 3),  # Start too high
            (1, 4, 3),  # End too high
            (3, 2, 3),  # Start > End
        ],
    )
    def test_prepare_verification_turns_out_of_range(
        self, service, mock_session_service, start, end, turn_count
    ):
        """Test error when turn indices are out of range."""
        turns = TurnFactory.create_batch(turn_count)
        session = SessionFactory.create(turns=turns)
        mock_session_service.get_session.return_value = session

        with pytest.raises(ValueError, match="Turn indices are out of range"):
            service._prepare_verification_turns("id", start, end, "summary")


class TestVerificationServiceCreateVerifierSession:
    """Test VerificationService._create_verifier_session method."""

    def test_create_verifier_session(self, service, mock_session_service):
        """Test creation of verifier session."""
        target_id = "target-123"
        turns = [TurnFactory.create_user_task()]
        mock_verifier_session = MagicMock()
        mock_session_service.create_new_session.return_value = mock_verifier_session

        result = service._create_verifier_session(target_id, turns)

        assert result == mock_verifier_session
        mock_session_service.create_new_session.assert_called_once()
        args, kwargs = mock_session_service.create_new_session.call_args
        assert target_id in kwargs["purpose"]
        assert "roles/verifier.md" in kwargs["roles"]
        assert kwargs["multi_step_reasoning_enabled"] is True

        assert mock_verifier_session.turns == turns
        mock_session_service.repository.save.assert_called_once_with(
            mock_verifier_session
        )


class TestVerificationServiceRunVerifierAgent:
    """Test VerificationService._run_verifier_agent method."""

    def test_run_verifier_agent_success(self, service, mock_takt_agent):
        """Test successful agent execution."""
        mock_takt_agent.run_existing_session.return_value = ("stdout", "stderr")

        stdout, stderr = service._run_verifier_agent("v-id", "t-id", 1, 5)

        assert stdout == "stdout"
        assert stderr == "stderr"
        mock_takt_agent.run_existing_session.assert_called_once()
        _, kwargs = mock_takt_agent.run_existing_session.call_args
        assert kwargs["session_id"] == "v-id"
        assert "v-id" in kwargs["instruction"]
        assert "t-id" in kwargs["instruction"]

    def test_run_verifier_agent_called_process_error(self, service, mock_takt_agent):
        """Test handling of subprocess.CalledProcessError."""
        error = subprocess.CalledProcessError(
            returncode=1, cmd="test", output="out", stderr="err"
        )
        mock_takt_agent.run_existing_session.side_effect = error

        with pytest.raises(RuntimeError, match="TaktAgent execution failed"):
            service._run_verifier_agent("v-id", "t-id", 1, 1)

    def test_run_verifier_agent_unexpected_error(self, service, mock_takt_agent):
        """Test handling of unexpected agent errors."""
        mock_takt_agent.run_existing_session.side_effect = Exception("Agent crash")

        with pytest.raises(
            RuntimeError, match="TaktAgent execution failed: Agent crash"
        ):
            service._run_verifier_agent("v-id", "t-id", 1, 1)


class TestVerificationServiceParseVerificationResult:
    """Test VerificationService._parse_verification_result method."""

    def test_parse_verification_result_approved(self, service, mock_session_service):
        """Test parsing of approved response."""
        v_id = "v-id"
        summary = "The Summary"
        response_text = "Approved: Looks good."
        turns = [
            TurnFactory.create_user_task(),
            TurnFactory.create_model_response(content=response_text),
        ]
        session = SessionFactory.create(turns=turns)
        mock_session_service.get_session.return_value = session

        result = service._parse_verification_result(v_id, summary)

        assert isinstance(result, VerificationResult)
        assert result.verification_status == "pending_approval"
        assert result.verifier_session_id == v_id
        assert summary in result.verifier_response
        assert response_text in result.verifier_response

    def test_parse_verification_result_rejected(self, service, mock_session_service):
        """Test parsing of rejected response."""
        v_id = "v-id"
        response_text = "Rejected: Too short."
        turns = [TurnFactory.create_model_response(content=response_text)]
        session = SessionFactory.create(turns=turns)
        mock_session_service.get_session.return_value = session

        result = service._parse_verification_result(v_id, "summary")

        assert result.verification_status == "rejected"
        assert result.verifier_response == response_text

    def test_parse_verification_result_unexpected_format(
        self, service, mock_session_service
    ):
        """Test parsing of response with unexpected format."""
        v_id = "v-id"
        response_text = "I don't know what to do."
        turns = [TurnFactory.create_model_response(content=response_text)]
        session = SessionFactory.create(turns=turns)
        mock_session_service.get_session.return_value = session

        result = service._parse_verification_result(v_id, "summary")

        assert result.verification_status == "rejected"
        assert "expected format" in result.verifier_response
        assert response_text in result.verifier_response

    def test_parse_verification_result_no_response(self, service, mock_session_service):
        """Test error when no model response is found."""
        v_id = "v-id"
        turns = [TurnFactory.create_user_task()]
        session = SessionFactory.create(turns=turns)
        mock_session_service.get_session.return_value = session

        with pytest.raises(ValueError, match="No model_response found"):
            service._parse_verification_result(v_id, "summary")
