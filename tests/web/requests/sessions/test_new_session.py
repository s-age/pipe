import os
import unittest

from pydantic import ValidationError

from src.pipe.web.requests.sessions.new_session import NewSessionRequest


class TestNewSessionRequest(unittest.TestCase):
    def setUp(self):
        # Create dummy files for validation
        self.role_file = "test_role.md"
        self.ref_file = "test_ref.txt"
        with open(self.role_file, "w") as f:
            f.write("role")
        with open(self.ref_file, "w") as f:
            f.write("ref")

        self.base_data: dict[str, str | bool] = {
            "purpose": "Test Purpose",
            "background": "Test Background",
            "instruction": "Test Instruction",
            "multi_step_reasoning_enabled": False,
        }

    def tearDown(self):
        # Clean up dummy files
        os.remove(self.role_file)
        os.remove(self.ref_file)

    def test_valid_request(self):
        """Tests a completely valid request."""
        data = self.base_data.copy()
        data.update({"roles": self.role_file, "references": self.ref_file})
        try:
            NewSessionRequest(**data)  # type: ignore
        except ValidationError as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_missing_required_fields(self):
        """Tests that validation fails when required fields are missing."""
        for field in ["purpose", "background", "instruction"]:
            with self.subTest(field=field):
                data = self.base_data.copy()
                data.pop(field)
                with self.assertRaises(ValidationError):
                    NewSessionRequest(**data)  # type: ignore

    def test_empty_required_fields(self):
        """Tests that validation fails when required fields are empty."""
        for field in ["purpose", "background", "instruction"]:
            with self.subTest(field=field):
                data = self.base_data.copy()
                data[field] = ""
                with self.assertRaises(ValidationError):
                    NewSessionRequest(**data)  # type: ignore

    def test_non_existent_role_file(self):
        """Tests that validation fails for a non-existent role file."""
        data = self.base_data.copy()
        data["roles"] = "non_existent_role.md"
        with self.assertRaises(ValidationError):
            NewSessionRequest(**data)  # type: ignore

    def test_non_existent_reference_file(self):
        """Tests that validation fails for a non-existent reference file."""
        data = self.base_data.copy()
        data["references"] = "non_existent_ref.txt"
        with self.assertRaises(ValidationError):
            NewSessionRequest(**data)  # type: ignore

    def test_mixed_existence_references(self):
        """Tests that validation fails if at least one reference file is missing."""
        data = self.base_data.copy()
        data["references"] = f"{self.ref_file} non_existent_ref.txt"
        with self.assertRaises(ValidationError):
            NewSessionRequest(**data)  # type: ignore


if __name__ == "__main__":
    unittest.main()
