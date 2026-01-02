from unittest.mock import Mock

import pytest
from pipe.core.models.procedure import ProcedureOption
from pipe.core.repositories.procedure_repository import ProcedureRepository
from pipe.core.services.procedure_service import ProcedureService


@pytest.fixture
def mock_repository():
    """Create a mock ProcedureRepository."""
    return Mock(spec=ProcedureRepository)


@pytest.fixture
def service(mock_repository):
    """Create a ProcedureService instance with mocked repository.

    IMPORTANT: Creates new instance per test to prevent state leakage.
    """
    return ProcedureService(procedure_repository=mock_repository)


class TestProcedureService:
    """Tests for ProcedureService."""

    def test_init(self, mock_repository):
        """Test initialization of ProcedureService."""
        service = ProcedureService(procedure_repository=mock_repository)
        assert service.procedure_repository == mock_repository

    def test_get_all_procedure_options(self, service, mock_repository):
        """Test get_all_procedure_options calls repository and returns results."""
        # Arrange
        expected_options = [
            ProcedureOption(label="Test 1", value="test1"),
            ProcedureOption(label="Test 2", value="test2"),
        ]
        mock_repository.get_all_procedure_options.return_value = expected_options

        # Act
        result = service.get_all_procedure_options()

        # Assert
        assert result == expected_options
        mock_repository.get_all_procedure_options.assert_called_once()

    def test_get_all_procedure_options_empty(self, service, mock_repository):
        """Test get_all_procedure_options with empty results."""
        # Arrange
        mock_repository.get_all_procedure_options.return_value = []

        # Act
        result = service.get_all_procedure_options()

        # Assert
        assert result == []
        mock_repository.get_all_procedure_options.assert_called_once()
