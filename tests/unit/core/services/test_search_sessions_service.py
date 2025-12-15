import unittest
from unittest.mock import patch

from pipe.core.models.search_result import SessionSearchResult
from pipe.core.services.search_sessions_service import SearchSessionsService


class TestSearchSessionsService(unittest.TestCase):
    def setUp(self):
        self.sessions_dir = "/tmp/sessions"
        self.service = SearchSessionsService(self.sessions_dir)

    @patch("os.walk")
    @patch("builtins.open")
    @patch("json.load")
    def test_search_returns_session_search_result_objects(
        self, mock_json_load, mock_open, mock_walk
    ):
        # Mock file system
        mock_walk.return_value = [
            (self.sessions_dir, [], ["session1.json"]),
        ]

        # Mock file content
        mock_json_load.return_value = {
            "purpose": "Test Purpose",
            "background": "Test Background",
        }

        results = self.service.search("Test")

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], SessionSearchResult)
        self.assertEqual(results[0].session_id, "session1")
        self.assertEqual(results[0].title, "Test Purpose")
        self.assertTrue(results[0].path.endswith("session1.json"))
