import os
import unittest

from pipe.web.validators.rules.file_exists import (
    validate_comma_separated_files,
    validate_file_exists,
    validate_space_separated_files,
)


class TestFileValidators(unittest.TestCase):
    def setUp(self):
        # Create dummy files for testing
        self.existing_file1 = "test_file1.tmp"
        self.existing_file2 = "test_file2.tmp"
        with open(self.existing_file1, "w") as f:
            f.write("test")
        with open(self.existing_file2, "w") as f:
            f.write("test")

    def tearDown(self):
        # Clean up dummy files
        os.remove(self.existing_file1)
        os.remove(self.existing_file2)

    def test_validate_file_exists_success(self):
        """Tests that validate_file_exists passes for an existing file."""
        try:
            validate_file_exists(self.existing_file1)
        except ValueError:
            self.fail("validate_file_exists() raised ValueError unexpectedly!")

    def test_validate_file_exists_failure(self):
        """Tests that validate_file_exists raises ValueError for a non-existent file."""
        with self.assertRaises(ValueError):
            validate_file_exists("non_existent_file.tmp")

    def test_validate_comma_separated_files_success(self):
        """Tests validation of a comma-separated string of existing files."""
        paths = f"{self.existing_file1},{self.existing_file2}"
        try:
            validate_comma_separated_files(paths)
        except ValueError:
            self.fail(
                "validate_comma_separated_files() raised ValueError unexpectedly!"
            )

    def test_validate_comma_separated_files_failure(self):
        """Tests that comma-separated validation fails if one file is missing."""
        paths = f"{self.existing_file1},non_existent_file.tmp"
        with self.assertRaises(ValueError):
            validate_comma_separated_files(paths)

    def test_validate_space_separated_files_success(self):
        """Tests validation of a space-separated string of existing files."""
        paths = f"{self.existing_file1} {self.existing_file2}"
        try:
            validate_space_separated_files(paths)
        except ValueError:
            self.fail(
                "validate_space_separated_files() raised ValueError unexpectedly!"
            )

    def test_validate_space_separated_files_with_quotes_success(self):
        """Tests validation of space-separated files with quotes."""
        paths = f'"{self.existing_file1}" "{self.existing_file2}"'
        try:
            validate_space_separated_files(paths)
        except ValueError:
            self.fail(
                "validate_space_separated_files() with quotes raised ValueError "
                "unexpectedly!"
            )

    def test_validate_space_separated_files_failure(self):
        """Tests that space-separated validation fails if one file is missing."""
        paths = f"{self.existing_file1} non_existent_file.tmp"
        with self.assertRaises(ValueError):
            validate_space_separated_files(paths)


if __name__ == "__main__":
    unittest.main()
