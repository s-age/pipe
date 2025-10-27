import os
import tempfile
import unittest
from unittest.mock import patch

from pipe.core.collections.references import ReferenceCollection
from pipe.core.models.reference import Reference


class TestReferenceCollection(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the project root
        self.project_root = tempfile.TemporaryDirectory()

        # Create some dummy files for testing
        self.file1_path = os.path.join(self.project_root.name, "file1.txt")
        with open(self.file1_path, "w") as f:
            f.write("This is file 1.")

        self.file2_path = os.path.join(self.project_root.name, "file2.py")
        with open(self.file2_path, "w") as f:
            f.write("print('hello')")

        # A file outside the project root for security testing
        self.outside_file = tempfile.NamedTemporaryFile(delete=False)
        self.outside_file.write(b"outside content")
        self.outside_file.close()

    def tearDown(self):
        # Clean up the temporary directory and files
        self.project_root.cleanup()
        os.unlink(self.outside_file.name)

    def test_get_for_prompt_with_valid_and_disabled_references(self):
        """
        Tests that get_for_prompt correctly yields content for enabled references
        and ignores disabled ones.
        """
        references = [
            Reference(
                path=os.path.relpath(self.file1_path, self.project_root.name),
                disabled=False,
            ),
            Reference(
                path=os.path.relpath(self.file2_path, self.project_root.name),
                disabled=True,
            ),  # This one should be ignored
        ]

        collection = ReferenceCollection(references)
        prompt_data = list(collection.get_for_prompt(self.project_root.name))

        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(
            prompt_data[0]["path"],
            os.path.relpath(self.file1_path, self.project_root.name),
        )
        self.assertEqual(prompt_data[0]["content"], "This is file 1.")

    def test_get_for_prompt_with_empty_list(self):
        """
        Tests that get_for_prompt returns an empty iterator for an empty list of
        references.
        """
        collection = ReferenceCollection([])
        prompt_data = list(collection.get_for_prompt(self.project_root.name))
        self.assertEqual(len(prompt_data), 0)

    def test_get_for_prompt_ignores_files_outside_project_root(self):
        """
        Tests that get_for_prompt safely ignores file paths that resolve
        to outside the project root directory.
        """
        references = [
            Reference(path=self.outside_file.name, disabled=False),
            Reference(
                path=os.path.relpath(self.file1_path, self.project_root.name),
                disabled=False,
            ),
        ]

        collection = ReferenceCollection(references)
        prompt_data = list(collection.get_for_prompt(self.project_root.name))

        # It should only return the valid file within the project root
        self.assertEqual(
            len(prompt_data), 1, "Should ignore files outside the project root."
        )
        self.assertEqual(
            prompt_data[0]["path"],
            os.path.relpath(self.file1_path, self.project_root.name),
        )

    def test_get_for_prompt_handles_nonexistent_files_gracefully(self):
        """
        Tests that get_for_prompt does not raise an error for files that don't exist
        and simply omits them from the output.
        """
        non_existent_path = "nonexistent/file.txt"
        references = [
            Reference(path=non_existent_path, disabled=False),
            Reference(
                path=os.path.relpath(self.file1_path, self.project_root.name),
                disabled=False,
            ),
        ]

        collection = ReferenceCollection(references)

        # Ensure read_text_file is called with the correct non-existent path and
        # returns None
        with patch("pipe.core.collections.references.read_text_file") as mock_read:
            # Set up the mock to return None for the non-existent file
            # and real content for the existing one.
            def side_effect(path):
                if path == os.path.abspath(
                    os.path.join(self.project_root.name, non_existent_path)
                ):
                    return None
                elif path == self.file1_path:
                    with open(path) as f:
                        return f.read()
                return None

            mock_read.side_effect = side_effect

            prompt_data = list(collection.get_for_prompt(self.project_root.name))

        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(
            prompt_data[0]["path"],
            os.path.relpath(self.file1_path, self.project_root.name),
        )


class TestReferenceCollectionTTL(unittest.TestCase):
    def test_add_new_reference(self):
        references: list[Reference] = []
        collection = ReferenceCollection(references)
        collection.add("new_file.txt")
        self.assertEqual(len(references), 1)
        self.assertEqual(references[0].path, "new_file.txt")
        self.assertEqual(references[0].ttl, 3)
        self.assertFalse(references[0].disabled)

    def test_add_existing_reference(self):
        references = [Reference(path="existing.txt", disabled=True, ttl=0)]
        collection = ReferenceCollection(references)
        collection.add("existing.txt")
        self.assertEqual(len(references), 1)  # Should not add a duplicate
        self.assertEqual(references[0].ttl, 0)  # Should not modify existing

    def test_update_ttl(self):
        references = [Reference(path="file.txt", disabled=True, ttl=0)]
        collection = ReferenceCollection(references)

        # Update TTL to a positive value
        collection.update_ttl("file.txt", 5)
        self.assertEqual(references[0].ttl, 5)
        self.assertFalse(references[0].disabled)

        # Update TTL to zero
        collection.update_ttl("file.txt", 0)
        self.assertEqual(references[0].ttl, 0)
        self.assertTrue(references[0].disabled)

    def test_decrement_all_ttl(self):
        references = [
            Reference(path="file1.txt", disabled=False, ttl=3),
            Reference(path="file2.txt", disabled=False, ttl=1),
            Reference(
                path="file3.txt", disabled=False, ttl=None
            ),  # Should be treated as 3
            Reference(path="file4.txt", disabled=True, ttl=5),  # Should be ignored
        ]
        collection = ReferenceCollection(references)
        collection.decrement_all_ttl()

        self.assertEqual(references[0].ttl, 2)
        self.assertFalse(references[0].disabled)

        self.assertEqual(references[1].ttl, 0)
        self.assertTrue(references[1].disabled)

        self.assertEqual(references[2].ttl, 2)
        self.assertFalse(references[2].disabled)

        self.assertEqual(references[3].ttl, 5)  # Ignored
        self.assertTrue(references[3].disabled)

    def test_sort_by_ttl(self):
        references = [
            Reference(path="disabled_low_ttl.txt", disabled=True, ttl=1),
            Reference(path="active_low_ttl.txt", disabled=False, ttl=2),
            Reference(path="active_high_ttl.txt", disabled=False, ttl=5),
            Reference(
                path="active_none_ttl.txt", disabled=False, ttl=None
            ),  # Treated as 3
            Reference(path="disabled_high_ttl.txt", disabled=True, ttl=10),
        ]
        collection = ReferenceCollection(references)
        collection.sort_by_ttl()

        paths = [ref.path for ref in references]
        expected_order = [
            "active_high_ttl.txt",
            "active_none_ttl.txt",
            "active_low_ttl.txt",
            "disabled_high_ttl.txt",
            "disabled_low_ttl.txt",
        ]
        self.assertEqual(paths, expected_order)


if __name__ == "__main__":
    unittest.main()
