import unittest
import json
from unittest.mock import patch, MagicMock

# The Flask app object needs to be imported for testing
from pipe.web.app import app
from pipe.core.models.session import Session
from pipe.core.models.reference import Reference

class TestAppApi(unittest.TestCase):

    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()

        # We patch the session_service used by the app to isolate the web layer
        # and avoid actual file system operations.
        self.mock_session_service = MagicMock()
        
        # The patch needs to target where the object is *used*
        self.patcher = patch('pipe.web.app.session_service', self.mock_session_service)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_edit_reference_ttl_api_success(self):
        """Tests the TTL update API endpoint with a valid request."""
        session_id = "test_session"
        reference_index = 0
        file_path = "test.py"
        new_ttl = 5

        # Mock the session that the service will return
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path=file_path, disabled=False, ttl=3)]
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.post(
            f'/api/session/{session_id}/references/ttl/{reference_index}',
            data=json.dumps({'ttl': new_ttl}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_service.get_session.assert_called_once_with(session_id)
        self.mock_session_service.update_reference_ttl_in_session.assert_called_once_with(
            session_id, file_path, new_ttl
        )

    def test_edit_reference_ttl_api_session_not_found(self):
        """Tests the API response when the session ID does not exist."""
        self.mock_session_service.get_session.return_value = None

        response = self.client.post(
            '/api/session/nonexistent/references/ttl/0',
            data=json.dumps({'ttl': 5}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_reference_ttl_api_index_out_of_range(self):
        """Tests the API response for an out-of-range reference index."""
        session_id = "test_session"
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path="test.py")]
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.post(
            f'/api/session/{session_id}/references/ttl/99', # Index 99 is out of range
            data=json.dumps({'ttl': 5}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_edit_reference_ttl_api_invalid_ttl_value(self):
        """Tests the API response for various invalid TTL values."""
        session_id = "test_session"
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path="test.py")]
        self.mock_session_service.get_session.return_value = mock_session

        invalid_payloads = [
            {'ttl': -1},
            {'ttl': 'not-a-number'},
            {'ttl': 1.5},
            {} # Missing ttl
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    f'/api/session/{session_id}/references/ttl/0',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()
