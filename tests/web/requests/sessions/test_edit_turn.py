import unittest

from pipe.web.requests.sessions.edit_turn import EditTurnRequest


class TestEditTurnRequest(unittest.TestCase):
    def test_valid_turn_is_accepted(self):
        """
        Tests that a valid Turn object passes validation.
        """
        valid_turn_data = {
            "type": "user_task",
            "instruction": "This is a test instruction.",
            "timestamp": "2025-01-01T00:00:00Z",
        }

        request_data = {"turn": valid_turn_data}

        try:
            EditTurnRequest(**request_data)
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")

    def test_invalid_data_raises_error(self):
        """
        Tests that data that is not a valid Turn object fails validation.
        """
        # This data is missing the required 'type' field for a Turn
        invalid_turn_data = {
            "instruction": "This is an invalid turn.",
            "timestamp": "2025-01-01T00:00:00Z",
        }

        request_data = {"turn": invalid_turn_data}

        with self.assertRaises(Exception):
            EditTurnRequest(**request_data)


if __name__ == "__main__":
    unittest.main()
