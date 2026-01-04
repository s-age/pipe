"""Unit tests for GetProceduresAction."""

from unittest.mock import MagicMock, patch

from pipe.core.models.procedure import ProcedureOption
from pipe.web.action_responses import ProceduresResponse
from pipe.web.actions.fs.get_procedures_action import GetProceduresAction


class TestGetProceduresAction:
    """Tests for the GetProceduresAction class."""

    @patch("pipe.web.actions.fs.get_procedures_action.get_procedure_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test that execute returns a ProceduresResponse with data from the service.

        Verifies that:
        1. The procedure service is retrieved from the container.
        2. get_all_procedure_options() is called on the service.
        3. The result is wrapped in a ProceduresResponse.
        """
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        expected_options = [
            ProcedureOption(label="Test Procedure 1", value="test_proc_1"),
            ProcedureOption(label="Test Procedure 2", value="test_proc_2"),
        ]
        mock_service.get_all_procedure_options.return_value = expected_options

        action = GetProceduresAction()

        # Exercise
        result = action.execute()

        # Verify
        assert isinstance(result, ProceduresResponse)
        assert result.procedures == expected_options
        mock_get_service.assert_called_once()
        mock_service.get_all_procedure_options.assert_called_once()

    @patch("pipe.web.actions.fs.get_procedures_action.get_procedure_service")
    def test_execute_empty_list(self, mock_get_service: MagicMock) -> None:
        """Test that execute handles an empty procedure list correctly.

        Verifies that the action returns a ProceduresResponse even when no
        procedures are available.
        """
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_all_procedure_options.return_value = []

        action = GetProceduresAction()

        # Exercise
        result = action.execute()

        # Verify
        assert isinstance(result, ProceduresResponse)
        assert result.procedures == []
        mock_get_service.assert_called_once()
        mock_service.get_all_procedure_options.assert_called_once()
