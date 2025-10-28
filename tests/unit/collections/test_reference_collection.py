import os
import tempfile
import unittest
from unittest.mock import patch

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

    @patch(
        "pipe.core.collections.references.read_text_file", return_value="file content"
    )
    def test_get_for_prompt(self, mock_read):
        rel_path = os.path.relpath(self.file1_path, self.project_root.name)
        collection = ReferenceCollection([Reference(path=rel_path, disabled=False)])
        prompt_data = list(collection.get_for_prompt(self.project_root.name))
        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(prompt_data[0]["path"], rel_path)
        self.assertEqual(prompt_data[0]["content"], "file content")


if __name__ == "__main__":
    unittest.main()
