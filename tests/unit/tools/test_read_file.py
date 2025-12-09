import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

from pipe.core.collections.references import ReferenceCollection
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_service import SessionService
from pipe.core.tools.read_file import read_file


class TestReadFileTool(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.mock_repository = Mock(spec=SessionRepository)
        self.session_service = SessionService(
            project_root=self.project_root,
            settings=self.settings,
            repository=self.mock_repository,
        )
        session = self.session_service.create_new_session("Test", "Test", [])
        self.session_id = session.session_id

        # Create a dummy file for the tool to read
        self.test_file_path = os.path.join(self.project_root, "test.txt")
        with open(self.test_file_path, "w") as f:
            f.write("hello world")

        # Setup mock repository to return a session with a valid references collection
        self.mock_session = Mock()
        self.mock_session.references = ReferenceCollection()
        self.mock_repository.find.return_value = self.mock_session

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_read_file_adds_reference_to_session(self):
        """
        Tests that the read_file tool correctly adds a file path to the session's
        references.
        """
        result = read_file(
            absolute_path=self.test_file_path,
            session_service=self.session_service,
            session_id=self.session_id,
        )

        self.assertIn("message", result)
        self.assertNotIn("error", result)
        self.assertIn("has been added", result["message"])

        # Verify that the reference was actually added
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.references), 1)
        self.assertEqual(session.references[0].path, self.test_file_path)

    def test_read_file_handles_non_existent_file(self):
        """
        Tests that the read_file tool returns an error for a non-existent file.
        """
        non_existent_path = os.path.join(self.project_root, "not_real.txt")
        result = read_file(
            absolute_path=non_existent_path,
            session_service=self.session_service,
            session_id=self.session_id,
        )

        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

    def test_read_file_calls_correct_session_service_methods(self):
        """
        Tests that read_file calls the correct service methods for adding and
        updating a reference.
        """
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.repository = MagicMock()
        mock_session = MagicMock()
        mock_session.references.default_ttl = 3
        mock_session_service.get_session.return_value = mock_session

        with patch("os.path.getsize", return_value=10):
            with patch(
                "pipe.core.domains.references.add_reference"
            ) as mock_add_reference:
                with patch(
                    "pipe.core.domains.references.update_reference_ttl"
                ) as mock_update_reference_ttl:
                    read_file(
                        absolute_path=self.test_file_path,
                        session_service=mock_session_service,
                        session_id="mock_session_id",
                    )

                    mock_add_reference.assert_called_once_with(
                        mock_session.references, self.test_file_path, 3
                    )
                    mock_update_reference_ttl.assert_called_once_with(
                        mock_session.references, self.test_file_path, 3
                    )
                    mock_session_service.repository.save.assert_called_once_with(
                        mock_session
                    )


if __name__ == "__main__":
    unittest.main()
