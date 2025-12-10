import unittest

from pipe.core.models.hyperparameters import Hyperparameters
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest
from pydantic import ValidationError


class TestEditSessionMetaRequest(unittest.TestCase):
    def test_valid_single_field(self):
        """
        Tests that the request is valid when at least one field is provided.
        """
        try:
            EditSessionMetaRequest.create_with_path_params(
                path_params={"session_id": "test_session"},
                body_data={"purpose": "New purpose"},
            )
            EditSessionMetaRequest.create_with_path_params(
                path_params={"session_id": "test_session"},
                body_data={
                    "hyperparameters": Hyperparameters(temperature=0.5).model_dump()
                },
            )
        except ValidationError as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_empty_request_raises_error(self):
        """
        Tests that an empty request body raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            EditSessionMetaRequest.create_with_path_params(
                path_params={"session_id": "test_session"}, body_data={}
            )

    def test_request_with_no_valid_fields_raises_error(self):
        """
        Tests that a request body with no valid fields raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            EditSessionMetaRequest.create_with_path_params(
                path_params={"session_id": "test_session"},
                body_data={"invalid_field": "some_value"},
            )


if __name__ == "__main__":
    unittest.main()
