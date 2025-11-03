import os
import tempfile
import unittest
from typing import Any

from pydantic import ValidationError

from src.pipe.web.requests.sessions.start_session import StartSessionRequest


class TestStartSessionRequest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.role_file = os.path.join(self.test_dir, "test_role.md")
        self.ref_file = os.path.join(self.test_dir, "test_ref.txt")
        self.artifact_file = os.path.join(self.test_dir, "test_artifact.txt")

        with open(self.role_file, "w") as f:
            f.write("role")
        with open(self.ref_file, "w") as f:
            f.write("reference")
        with open(self.artifact_file, "w") as f:
            f.write("artifact")

        self.base_data: dict[str, Any] = {
            "purpose": "Test Purpose",
            "background": "Test Background",
            "roles": [self.role_file],
            "references": [
                {"path": self.ref_file, "disabled": False, "persist": False}
            ],
            "artifacts": [self.artifact_file],
            "instruction": "Test Instruction",
            "multi_step_reasoning_enabled": True,
            "hyperparameters": {"temperature": 0.5, "top_p": 0.5, "top_k": 50},
        }

    def tearDown(self):
        # Clean up dummy files
        os.remove(self.role_file)
        os.remove(self.ref_file)
        os.remove(self.artifact_file)

    def test_valid_request(self):
        """Tests a completely valid request."""
        data = self.base_data.copy()
        data.update(
            {
                "roles": [self.role_file],
                "references": [
                    {"path": self.ref_file, "disabled": False, "persist": False}
                ],
                "artifacts": [self.artifact_file],
            }
        )

        try:
            StartSessionRequest(**data)
        except ValidationError as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_missing_required_fields(self):
        """Tests that validation fails when required fields are missing."""
        for field in ["purpose", "background", "instruction"]:
            with self.subTest(field=field):
                data = self.base_data.copy()
                data.pop(field)
                with self.assertRaises(ValidationError):
                    StartSessionRequest(**data)

    def test_empty_required_fields(self):
        """Tests that validation fails when required fields are empty."""
        for field in ["purpose", "background", "instruction"]:
            with self.subTest(field=field):
                data = self.base_data.copy()
                data[field] = ""
                with self.assertRaises(ValidationError):
                    StartSessionRequest(**data)

    def test_non_existent_role_file(self):
        """Tests that validation fails for a non-existent role file."""
        data = self.base_data.copy()
        data["roles"] = ["non_existent_role.md"]
        with self.assertRaises(ValidationError):
            StartSessionRequest(**data)

    def test_non_existent_reference_file(self):
        """Tests that validation fails for a non-existent reference file."""
        data = self.base_data.copy()
        data["references"] = [
            {"path": "non_existent_ref.txt", "disabled": False, "persist": False}
        ]
        with self.assertRaises(ValidationError):
            StartSessionRequest(**data)

    def test_non_existent_artifact_file(self):
        """Tests that validation fails for a non-existent artifact file."""
        data = self.base_data.copy()
        data["artifacts"] = ["non_existent_artifact.txt"]
        with self.assertRaises(ValidationError):
            StartSessionRequest(**data)

    def test_mixed_existence_references(self):
        """Tests that validation fails if at least one reference file is missing."""
        data = self.base_data.copy()
        data["references"] = [
            {"path": self.ref_file, "disabled": False, "persist": False},
            {"path": "non_existent_ref.txt", "disabled": False, "persist": False},
        ]
        with self.assertRaises(ValidationError):
            StartSessionRequest(**data)

    def test_mixed_existence_roles(self):
        """Tests that validation fails if at least one role file is missing."""
        data = self.base_data.copy()
        data["roles"] = [self.role_file, "non_existent_role.md"]
        with self.assertRaises(ValidationError):
            StartSessionRequest(**data)

    def test_mixed_existence_artifacts(self):
        """Tests that validation fails if at least one artifact file is missing."""
        data = self.base_data.copy()
        data["artifacts"] = [self.artifact_file, "non_existent_artifact.txt"]
        with self.assertRaises(ValidationError):
            StartSessionRequest(**data)


if __name__ == "__main__":
    unittest.main()
