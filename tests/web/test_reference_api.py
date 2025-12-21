import json
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.models.reference import Reference
from pipe.core.models.session import Session
from pipe.web.app import create_app


class TestReferenceApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        self.mock_session_service = MagicMock()
        self.mock_session_reference_service = MagicMock()

        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.reference_patcher = patch(
            "pipe.web.service_container.get_session_reference_service",
            return_value=self.mock_session_reference_service,
        )
        self.patcher.start()
        self.reference_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.reference_patcher.stop()

    def test_edit_references_api_success(self):
        """Tests successfully editing references."""
        payload = {"references": [{"path": "/test.py", "disabled": False, "ttl": -1}]}
        response = self.client.patch(
            "/api/v1/session/sid/references",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.mock_session_reference_service.update_references.assert_called_once()

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

        response = self.client.open(
            f"/api/v1/session/{session_id}/references/{reference_index}/ttl",
            method="PATCH",
            json={"ttl": new_ttl},
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_service.get_session.assert_called_once_with(session_id)
        self.mock_session_reference_service.update_reference_ttl_by_index.assert_called_once_with(
            session_id, reference_index, new_ttl
        )

    def test_edit_reference_ttl_api_session_not_found(self):
        """Tests the API response when the session ID does not exist."""
        self.mock_session_service.get_session.return_value = None

        response = self.client.open(
            "/api/session/nonexistent/references/0/ttl",
            method="PATCH",
            json={"ttl": 5},
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_reference_ttl_api_index_out_of_range(self):
        """Tests the API response for an out-of-range reference index."""
        session_id = "test_session"
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path="test.py")]
        self.mock_session_service.get_session.return_value = mock_session

        response = self.client.open(
            f"/api/v1/session/{session_id}/references/99/ttl",
            # Index 99 is out of range
            method="PATCH",
            json={"ttl": 5},
        )

        self.assertEqual(response.status_code, 400)

    def test_edit_reference_ttl_api_invalid_ttl_value(self):
        """Tests the API response for various invalid TTL values."""
        session_id = "test_session"
        mock_session = MagicMock(spec=Session)
        mock_session.references = [Reference(path="test.py")]
        self.mock_session_service.get_session.return_value = mock_session

        invalid_payloads = [
            {"ttl": -1},
            {"ttl": "not-a-number"},
            {"ttl": 1.5},
            {},  # Missing ttl
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.open(
                    f"/api/v1/session/{session_id}/references/0/ttl",
                    method="PATCH",
                    json=payload,
                )
                self.assertEqual(response.status_code, 422)
