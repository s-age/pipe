import os
import shutil
import tempfile
import unittest

from pipe.core.models.results.search_file_content_result import (
    SearchFileContentResult,
)
from pipe.core.tools.search_file_content import search_file_content


class TestSearchFileContentTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        # Create dummy files with content to search
        self.file1_path = os.path.join(self.test_dir, "file1.txt")
        with open(self.file1_path, "w") as f:
            f.write("hello world\n")
            f.write("this is a test\n")

        self.file2_path = os.path.join(self.test_dir, "file2.py")
        with open(self.file2_path, "w") as f:
            f.write("import os\n")
            f.write("def hello():\n")
            f.write("    print('hello')\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_search_file_content_finds_pattern(self):
        """
        Tests that the search_file_content tool finds lines matching the regex pattern.
        """
        result = search_file_content(path=self.test_dir, pattern="hello")

        self.assertIsInstance(result, SearchFileContentResult)
        self.assertIsInstance(result.content, list)
        self.assertEqual(len(result.content), 3)

        # Check content of the results
        content = result.content
        assert isinstance(content, list)
        found_paths = {r.file_path for r in content}
        expected_paths = {
            os.path.relpath(self.file1_path, self.test_dir),
            os.path.relpath(self.file2_path, self.test_dir),
        }
        # Use assertCountEqual for unordered comparison
        self.assertCountEqual(found_paths, expected_paths)

        # A more robust check of the content
        hello_world_match = next(
            (
                m
                for m in content
                if m.file_path == os.path.relpath(self.file1_path, self.test_dir)
            ),
            None,
        )
        self.assertIsNotNone(hello_world_match)
        assert hello_world_match is not None
        self.assertEqual(hello_world_match.line_number, 1)
        self.assertEqual(hello_world_match.line_content, "hello world")

        def_hello_match = next(
            (
                m
                for m in content
                if m.file_path == os.path.relpath(self.file2_path, self.test_dir)
                and m.line_number == 2
            ),
            None,
        )
        self.assertIsNotNone(def_hello_match)
        assert def_hello_match is not None
        self.assertEqual(def_hello_match.line_content, "def hello():")

    def test_search_file_content_with_include_glob(self):
        """
        Tests that the 'include' glob pattern correctly filters the files to be
        searched.
        """
        result = search_file_content(
            path=self.test_dir, pattern="hello", include="*.txt"
        )

        self.assertIsInstance(result, SearchFileContentResult)
        self.assertIsInstance(result.content, list)
        content = result.content
        assert isinstance(content, list)
        self.assertEqual(len(content), 1)
        self.assertEqual(
            content[0].file_path,
            os.path.relpath(self.file1_path, self.test_dir),
        )

    def test_search_file_content_no_matches(self):
        """
        Tests that the tool returns an empty result set when no matches are found.
        """
        result = search_file_content(path=self.test_dir, pattern="non_existent_pattern")

        self.assertIsInstance(result, SearchFileContentResult)
        self.assertIsInstance(result.content, str)
        self.assertEqual(result.content, "No matches found.")


if __name__ == "__main__":
    unittest.main()
