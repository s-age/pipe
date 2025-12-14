import json
import unittest
from unittest.mock import MagicMock, patch

from pipe.web.app import create_app


class TestMetaApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(init_index=False)
        self.app.config["TESTING"] = True
        with self.app.app_context():
            self.client = self.app.test_client()

        self.mock_session_service = MagicMock()
        self.mock_session_meta_service = MagicMock()

        self.patcher = patch(
            "pipe.web.service_container.get_session_service",
            return_value=self.mock_session_service,
        )
        self.meta_patcher = patch(
            "pipe.web.service_container.get_session_meta_service",
            return_value=self.mock_session_meta_service,
        )
        self.patcher.start()
        self.meta_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.meta_patcher.stop()

    def test_edit_session_meta_api_success(self):
        """Tests successfully editing session metadata via API."""
        session_id = "sid"
        payload = {"purpose": "New Purpose"}

        response = self.client.patch(
            f"/api/v1/session/{session_id}/meta",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_session_meta_service.edit_session_meta.assert_called_once_with(
            session_id, payload
        )
