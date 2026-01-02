"""Unit tests for SessionOptimizationService."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.session_optimization import (
    DiagnosisData,
    DoctorResult,
    SessionModifications,
)
from pipe.core.models.turn import CompressedHistoryTurn
from pipe.core.services.session_optimization_service import (
    CompressorResult,
    DoctorResultResponse,
    SessionOptimizationService,
    TherapistResult,
)

from tests.factories.models import SessionFactory, TurnFactory


@pytest.fixture
def mock_takt_agent():
    """Create a mock TaktAgent."""
    return MagicMock()


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock()


@pytest.fixture
def service(mock_takt_agent, mock_repository):
    """Create SessionOptimizationService with mocked dependencies."""
    return SessionOptimizationService(
        project_root="/tmp/test",
        takt_agent=mock_takt_agent,
        repository=mock_repository,
    )


class TestSessionOptimizationServiceInit:
    """Test SessionOptimizationService initialization."""

    def test_init(self, mock_takt_agent, mock_repository):
        """Test that the service initializes correctly."""
        service = SessionOptimizationService(
            project_root="/tmp/test",
            takt_agent=mock_takt_agent,
            repository=mock_repository,
        )
        assert service.project_root == "/tmp/test"
        assert service.takt_agent == mock_takt_agent
        assert service.repository == mock_repository


class TestSessionOptimizationServiceRunCompression:
    """Test SessionOptimizationService.run_compression() method."""

    @patch(
        "pipe.core.services.session_optimization_service.build_compressor_instruction"
    )
    @patch(
        "pipe.core.services.session_optimization_service.extract_summary_from_compressor_response"
    )
    def test_run_compression_success(
        self,
        mock_extract,
        mock_build_instruction,
        service,
        mock_takt_agent,
        mock_repository,
    ):
        """Test successful compression run."""
        mock_build_instruction.return_value = "Test instruction"
        mock_takt_agent.run_new_session.return_value = (
            "compressor-123",
            "stdout",
            "stderr",
        )
        mock_extract.return_value = ("Test summary", "verifier-123")

        # Create a compressor session with a model response
        compressor_session = SessionFactory.create(session_id="compressor-123")
        model_response = TurnFactory.create_model_response(content="Response content")
        compressor_session.turns.append(model_response)
        mock_repository.find.return_value = compressor_session

        result = service.run_compression(
            session_id="target-123",
            policy="Test policy",
            target_length=100,
            start_turn=1,
            end_turn=5,
        )

        assert isinstance(result, CompressorResult)
        assert result.session_id == "compressor-123"
        assert result.summary == "Test summary"
        assert result.verifier_session_id == "verifier-123"

        mock_build_instruction.assert_called_once_with(
            "target-123", "Test policy", 100, 1, 5
        )
        mock_takt_agent.run_new_session.assert_called_once()
        mock_repository.find.assert_called_with("compressor-123")
        mock_extract.assert_called_once_with("Response content")

    def test_run_compression_session_not_found(
        self, service, mock_takt_agent, mock_repository
    ):
        """Test run_compression when session is not found after creation."""
        mock_takt_agent.run_new_session.return_value = (
            "compressor-123",
            "stdout",
            "stderr",
        )
        mock_repository.find.return_value = None

        with pytest.raises(
            ValueError, match="Session or turns not found after creation"
        ):
            service.run_compression("target-123", "policy", 100, 1, 5)

    @patch(
        "pipe.core.services.session_optimization_service.build_compressor_instruction"
    )
    def test_run_compression_no_model_response(
        self, mock_build_instruction, service, mock_takt_agent, mock_repository
    ):
        """Test run_compression when no model response is found."""
        mock_takt_agent.run_new_session.return_value = (
            "compressor-123",
            "stdout",
            "stderr",
        )
        compressor_session = SessionFactory.create(session_id="compressor-123")
        # Only user task, no model response
        compressor_session.turns.append(TurnFactory.create_user_task())
        mock_repository.find.return_value = compressor_session

        result = service.run_compression("target-123", "policy", 100, 1, 5)

        assert result.summary == ""
        assert result.verifier_session_id == ""


class TestSessionOptimizationServiceApproveCompression:
    """Test SessionOptimizationService.approve_compression() method."""

    @patch(
        "pipe.core.domains.session_optimization.extract_summary_from_compressor_response"
    )
    def test_approve_compression_success(
        self, mock_extract, service, mock_takt_agent, mock_repository
    ):
        """Test successful compression approval."""
        compressor_session_id = "compressor-123"
        background = "Target session: target-123, turns 1-5"
        compressor_session = SessionFactory.create(
            session_id=compressor_session_id, background=background
        )
        model_response = TurnFactory.create_model_response(
            content="Approved: Test summary"
        )
        compressor_session.turns.append(model_response)
        mock_repository.find.return_value = compressor_session
        mock_extract.return_value = ("Approved: Test summary", None)

        service.approve_compression(compressor_session_id)

        mock_takt_agent.run_existing_session.assert_called_once()
        call_args = mock_takt_agent.run_existing_session.call_args
        assert call_args[0][0] == compressor_session_id
        assert 'session_id="target-123"' in call_args[0][1]
        assert "start_turn=1" in call_args[0][1]
        assert "end_turn=5" in call_args[0][1]
        assert 'summary_text="Test summary"' in call_args[0][1]

        mock_repository.delete.assert_called_once_with(compressor_session_id)

    def test_approve_compression_session_not_found(self, service, mock_repository):
        """Test approve_compression when session is not found."""
        mock_repository.find.return_value = None
        with pytest.raises(ValueError, match="not found or has no turns"):
            service.approve_compression("nonexistent")

    def test_approve_compression_no_background(self, service, mock_repository):
        """Test approve_compression when background is missing."""
        compressor_session = SessionFactory.create(session_id="comp-123")
        compressor_session.background = None
        compressor_session.turns.append(TurnFactory.create_model_response())
        mock_repository.find.return_value = compressor_session

        with pytest.raises(ValueError, match="No background found"):
            service.approve_compression("comp-123")

    def test_approve_compression_invalid_background(self, service, mock_repository):
        """Test approve_compression when background cannot be parsed."""
        compressor_session = SessionFactory.create(session_id="comp-123")
        compressor_session.background = "Invalid background"
        compressor_session.turns.append(TurnFactory.create_model_response())
        mock_repository.find.return_value = compressor_session

        with pytest.raises(ValueError, match="Could not parse compression parameters"):
            service.approve_compression("comp-123")

    def test_approve_compression_no_model_response(self, service, mock_repository):
        """Test approve_compression when no model response is found."""
        compressor_session = SessionFactory.create(
            session_id="comp-123", background="Target session: t-1, turns 1-2"
        )
        # No turns
        mock_repository.find.return_value = compressor_session

        with pytest.raises(ValueError, match="not found or has no turns"):
            service.approve_compression("comp-123")

    @patch(
        "pipe.core.domains.session_optimization.extract_summary_from_compressor_response"
    )
    def test_approve_compression_rejected_summary(
        self, mock_extract, service, mock_repository
    ):
        """Test approve_compression when summary is rejected."""
        compressor_session = SessionFactory.create(
            session_id="comp-123", background="Target session: t-1, turns 1-2"
        )
        compressor_session.turns.append(TurnFactory.create_model_response())
        mock_repository.find.return_value = compressor_session
        mock_extract.return_value = ("Rejected: Too short", None)

        with pytest.raises(
            ValueError, match="Cannot approve: summary was not approved"
        ):
            service.approve_compression("comp-123")


class TestSessionOptimizationServiceDenyCompression:
    """Test SessionOptimizationService.deny_compression() method."""

    def test_deny_compression(self, service, mock_repository):
        """Test that deny_compression deletes the session."""
        service.deny_compression("comp-123")
        mock_repository.delete.assert_called_once_with("comp-123")


class TestSessionOptimizationServiceReplaceTurnRangeWithSummary:
    """Test SessionOptimizationService.replace_turn_range_with_summary() method."""

    @patch("pipe.core.services.session_optimization_service.get_current_timestamp")
    def test_replace_turn_range_success(self, mock_timestamp, service, mock_repository):
        """Test successful turn range replacement."""
        mock_timestamp.return_value = "2025-01-01T00:00:00Z"
        session = SessionFactory.create(session_id="target-123")
        session.turns = TurnFactory.create_batch(5)
        mock_repository.find.return_value = session

        service.replace_turn_range_with_summary("target-123", "Summary text", 1, 3)

        assert len(session.turns) == 3  # 5 - (3-1+1) + 1 = 3
        assert isinstance(session.turns[1], CompressedHistoryTurn)
        assert session.turns[1].content == "Summary text"
        assert session.turns[1].original_turns_range == [2, 4]
        mock_repository.save.assert_called_once_with(session)

    def test_replace_turn_range_session_not_found(self, service, mock_repository):
        """Test replacement when session is not found."""
        mock_repository.find.return_value = None
        with pytest.raises(ValueError, match="Session target-123 not found"):
            service.replace_turn_range_with_summary("target-123", "Summary", 0, 0)

    def test_replace_turn_range_invalid_range(self, service, mock_repository):
        """Test replacement with invalid range."""
        session = SessionFactory.create()
        session.turns = TurnFactory.create_batch(3)
        mock_repository.find.return_value = session

        invalid_ranges = [
            (-1, 1),  # start < 0
            (0, 3),  # end >= len
            (2, 1),  # start > end
        ]

        for start, end in invalid_ranges:
            with pytest.raises(ValueError, match="Invalid turn range"):
                service.replace_turn_range_with_summary("id", "Summary", start, end)


class TestSessionOptimizationServiceRunTherapist:
    """Test SessionOptimizationService.run_therapist() method."""

    @patch(
        "pipe.core.services.session_optimization_service.build_therapist_instruction"
    )
    @patch("pipe.core.services.session_optimization_service.parse_therapist_diagnosis")
    def test_run_therapist_success(
        self,
        mock_parse,
        mock_build_instruction,
        service,
        mock_takt_agent,
        mock_repository,
    ):
        """Test successful therapist run."""
        target_session = SessionFactory.create(session_id="target-123")
        target_session.turns = TurnFactory.create_batch(10)

        therapist_session = SessionFactory.create(session_id="therapist-123")
        therapist_session.turns.append(
            TurnFactory.create_model_response(content="Diagnosis content")
        )

        mock_repository.find.side_effect = [
            target_session,  # First call to get turns count
            therapist_session,  # Second call after creation
        ]

        mock_takt_agent.run_new_session.return_value = (
            "therapist-123",
            "stdout",
            "stderr",
        )
        mock_parse.return_value = DiagnosisData(
            summary="Test summary",
            deletions=[],
            edits=[],
            compressions=[],
            raw_diagnosis="Raw",
        )

        result = service.run_therapist("target-123")

        assert isinstance(result, TherapistResult)
        assert result.session_id == "therapist-123"
        assert result.diagnosis.summary == "Test summary"

        mock_repository.delete.assert_called_once_with("therapist-123")

    def test_run_therapist_target_not_found(self, service, mock_repository):
        """Test run_therapist when target session is not found."""
        mock_repository.find.return_value = None
        with pytest.raises(ValueError, match="Session target-123 not found"):
            service.run_therapist("target-123")

    def test_run_therapist_cleanup_on_error(
        self, service, mock_takt_agent, mock_repository
    ):
        """Test that therapist session is deleted even if an error occurs."""
        target_session = SessionFactory.create()
        target_session.turns = TurnFactory.create_batch(2)
        mock_repository.find.side_effect = [
            target_session,
            None,  # Error: session not found after creation
        ]
        mock_takt_agent.run_new_session.return_value = (
            "therapist-123",
            "stdout",
            "stderr",
        )

        with pytest.raises(
            ValueError, match="Session or turns not found after creation"
        ):
            service.run_therapist("target-123")

        mock_repository.delete.assert_called_once_with("therapist-123")


class TestSessionOptimizationServiceRunDoctor:
    """Test SessionOptimizationService.run_doctor() method."""

    @patch("pipe.core.services.session_optimization_service.filter_valid_modifications")
    @patch("pipe.core.services.session_optimization_service.build_doctor_instruction")
    @patch("pipe.core.services.session_optimization_service.parse_doctor_result")
    def test_run_doctor_success(
        self,
        mock_parse,
        mock_build_instruction,
        mock_filter,
        service,
        mock_takt_agent,
        mock_repository,
    ):
        """Test successful doctor run."""
        target_session = SessionFactory.create(session_id="target-123")
        target_session.turns = TurnFactory.create_batch(10)

        doctor_session = SessionFactory.create(session_id="doctor-123")
        doctor_session.turns.append(
            TurnFactory.create_model_response(content="Doctor response")
        )

        mock_repository.find.side_effect = [
            target_session,  # First call to validate turns
            doctor_session,  # Second call after creation
        ]

        mock_takt_agent.run_new_session.return_value = (
            "doctor-123",
            "stdout",
            "stderr",
        )
        mock_parse.return_value = DoctorResult(
            status="Succeeded",
            reason="",
            applied_deletions=[],
            applied_edits=[],
            applied_compressions=[],
        )

        modifications = SessionModifications(deletions=[], edits=[], compressions=[])
        result = service.run_doctor("target-123", modifications)

        assert isinstance(result, DoctorResultResponse)
        assert result.session_id == "doctor-123"
        assert result.result.status == "Succeeded"

        mock_repository.delete.assert_called_once_with("doctor-123")

    def test_run_doctor_target_not_found(self, service, mock_repository):
        """Test run_doctor when target session is not found."""
        mock_repository.find.return_value = None
        modifications = SessionModifications(deletions=[], edits=[], compressions=[])
        with pytest.raises(ValueError, match="Session target-123 not found"):
            service.run_doctor("target-123", modifications)

    def test_run_doctor_cleanup_on_error(
        self, service, mock_takt_agent, mock_repository
    ):
        """Test that doctor session is deleted even if an error occurs."""
        target_session = SessionFactory.create()
        target_session.turns = TurnFactory.create_batch(2)
        mock_repository.find.side_effect = [
            target_session,
            None,  # Error: session not found after creation
        ]
        mock_takt_agent.run_new_session.return_value = (
            "doctor-123",
            "stdout",
            "stderr",
        )

        modifications = SessionModifications(deletions=[], edits=[], compressions=[])
        with pytest.raises(
            ValueError, match="Session or turns not found after creation"
        ):
            service.run_doctor("target-123", modifications)

        mock_repository.delete.assert_called_once_with("doctor-123")
