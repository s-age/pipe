import unittest
from unittest.mock import MagicMock, patch

# The Flask app factory needs to be imported for testing
from pipe.web.app import create_app


class TestAppViews(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.mock_session_service = MagicMock()
        # Patch in the service container
        self.patcher = patch(
            "pipe.web.service_container.get_container",
            return_value=MagicMock(session_service=self.mock_session_service),
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_view_session_not_found(self):
        """Tests that a 404 is returned for a non-existent session."""
        self.mock_session_service.list_sessions().__contains__.return_value = False
        response = self.client.get("/session/non_existent_id")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
