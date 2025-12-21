import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from pipe.core.collections.references import ReferenceCollection
from pipe.core.models.reference import Reference


class TestReferenceCollection(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.TemporaryDirectory()
        self.file1_path = os.path.join(self.project_root.name, "file1.txt")
        with open(self.file1_path, "w") as f:
            f.write("This is file 1.")

    def tearDown(self):
        self.project_root.cleanup()

    def test_add_new_reference(self):
        collection = ReferenceCollection()
        collection.add("new_file.txt")
        self.assertEqual(len(collection), 1)
        self.assertEqual(collection[0].path, "new_file.txt")
        self.assertEqual(collection[0].ttl, 3)
        self.assertFalse(collection[0].disabled)

    def test_add_existing_reference(self):
        collection = ReferenceCollection([Reference(path="existing.txt", ttl=0)])
        collection.add("existing.txt")
        self.assertEqual(len(collection), 1)
        self.assertEqual(collection[0].ttl, 0)

    def test_update_ttl(self):
        collection = ReferenceCollection([Reference(path="file.txt", ttl=0)])
        collection.update_ttl("file.txt", 5)
        self.assertEqual(collection[0].ttl, 5)
        self.assertFalse(collection[0].disabled)
        collection.update_ttl("file.txt", 0)
        self.assertEqual(collection[0].ttl, 0)
        self.assertTrue(collection[0].disabled)

    def test_decrement_all_ttl(self):
        collection = ReferenceCollection(
            [
                Reference(path="file1.txt", ttl=3),
                Reference(path="file2.txt", ttl=1),
                Reference(path="file3.txt", ttl=None),
                Reference(path="file4.txt", disabled=True, ttl=5),
            ]
        )
        collection.decrement_all_ttl()

        # Find refs by path to make test order-independent
        ref1 = next(r for r in collection if r.path == "file1.txt")
        ref2 = next(r for r in collection if r.path == "file2.txt")
        ref3 = next(r for r in collection if r.path == "file3.txt")
        ref4 = next(r for r in collection if r.path == "file4.txt")

        self.assertEqual(ref1.ttl, 2)
        self.assertEqual(ref2.ttl, 0)
        self.assertTrue(ref2.disabled)
        self.assertEqual(ref3.ttl, 2)
        self.assertEqual(ref4.ttl, 5)

    def test_sort_by_ttl(self):
        collection = ReferenceCollection(
            [
                Reference(path="disabled_low_ttl.txt", disabled=True, ttl=1),
                Reference(path="active_low_ttl.txt", disabled=False, ttl=2),
                Reference(path="active_high_ttl.txt", disabled=False, ttl=5),
                Reference(path="active_none_ttl.txt", disabled=False, ttl=None),
                Reference(path="disabled_high_ttl.txt", disabled=True, ttl=10),
            ]
        )
        collection.sort_by_ttl()
        paths = [ref.path for ref in collection]
        expected_order = [
            "active_high_ttl.txt",
            "active_none_ttl.txt",
            "active_low_ttl.txt",
            "disabled_high_ttl.txt",
            "disabled_low_ttl.txt",
        ]
        self.assertEqual(paths, expected_order)

    def test_get_for_prompt(self):
        rel_path = os.path.relpath(self.file1_path, self.project_root.name)
        collection = ReferenceCollection([Reference(path=rel_path, disabled=False)])

        # Mock ResourceRepository
        mock_repo = MagicMock()
        mock_repo.read_text.return_value = "file content"

        prompt_data = list(collection.get_for_prompt(mock_repo, self.project_root.name))
        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(prompt_data[0]["path"], rel_path)
        self.assertEqual(prompt_data[0]["content"], "file content")

    def test_get_for_prompt_skips_outside_project_root(self):
        """
        Tests that get_for_prompt skips references outside the project root.
        """
        dangerous_path = "../../../etc/passwd"
        collection = ReferenceCollection(
            [Reference(path=dangerous_path, disabled=False)]
        )

        mock_repo = MagicMock()

        with patch("pipe.core.collections.references.logger") as mock_logger:
            prompt_data = list(
                collection.get_for_prompt(mock_repo, self.project_root.name)
            )
            self.assertEqual(len(prompt_data), 0)
            expected_warning = (
                f"Reference path '{dangerous_path}' is outside the "
                "project root. Skipping."
            )
            mock_logger.warning.assert_called_once_with(expected_warning)

    def test_get_for_prompt_skips_unreadable_file(self):
        """
        Tests that get_for_prompt skips files that return None from repository.
        """
        collection = ReferenceCollection(
            [Reference(path="unreadable.txt", disabled=False)]
        )

        mock_repo = MagicMock()
        mock_repo.read_text.return_value = None

        with patch("pipe.core.collections.references.logger") as mock_logger:
            prompt_data = list(
                collection.get_for_prompt(mock_repo, self.project_root.name)
            )
            self.assertEqual(len(prompt_data), 0)
            full_path = os.path.abspath(
                os.path.join(self.project_root.name, "unreadable.txt")
            )
            expected_warning = (
                f"Reference file not found or could not be read: {full_path}"
            )
            mock_logger.warning.assert_called_once_with(expected_warning)

    def test_get_for_prompt_handles_exception(self):
        """
        Tests that get_for_prompt handles exceptions during file processing.
        """
        collection = ReferenceCollection([Reference(path="error.txt", disabled=False)])

        mock_repo = MagicMock()
        mock_repo.read_text.side_effect = Exception("Test error")

        with patch("pipe.core.collections.references.logger") as mock_logger:
            prompt_data = list(
                collection.get_for_prompt(mock_repo, self.project_root.name)
            )
            self.assertEqual(len(prompt_data), 0)
            expected_warning = "Could not process reference file error.txt: Test error"
            mock_logger.warning.assert_called_once_with(expected_warning)

    def test_pydantic_json_schema(self):
        """
        Tests the __get_pydantic_json_schema__ method for correct schema generation.
        """
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            references: ReferenceCollection = Field(default_factory=ReferenceCollection)

        schema = TestModel.model_json_schema()

        defs_key = "$defs" if "$defs" in schema else "definitions"
        self.assertIn(defs_key, schema)
        self.assertIn("Reference", schema[defs_key])

        props = schema["properties"]
        self.assertIn("references", props)
        self.assertEqual(props["references"]["type"], "array")

        # Pydantic v2 uses '$defs', v1 uses 'definitions'
        ref_path = f"#/{defs_key}/Reference"
        self.assertEqual(props["references"]["items"]["$ref"], ref_path)


if __name__ == "__main__":
    unittest.main()
