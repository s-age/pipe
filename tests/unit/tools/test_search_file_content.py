import unittest
import os
import tempfile
import shutil

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
        
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], list)
        self.assertEqual(len(result["content"]), 3)
        
        # Check content of the results
        found_paths = {r['file_path'] for r in result["content"]}
        expected_paths = {
            os.path.relpath(self.file1_path, self.test_dir),
            os.path.relpath(self.file2_path, self.test_dir)
        }
        # Use assertCountEqual for unordered comparison
        self.assertCountEqual(found_paths, expected_paths)
        
        # A more robust check of the content
        hello_world_match = next((m for m in result["content"] if m['file_path'] == os.path.relpath(self.file1_path, self.test_dir)), None)
        self.assertIsNotNone(hello_world_match)
        self.assertEqual(hello_world_match['line_number'], 1)
        self.assertEqual(hello_world_match['line_content'], "hello world")

        def_hello_match = next((m for m in result["content"] if m['file_path'] == os.path.relpath(self.file2_path, self.test_dir) and m['line_number'] == 2), None)
        self.assertIsNotNone(def_hello_match)
        self.assertEqual(def_hello_match['line_content'], "def hello():")

    def test_search_file_content_with_include_glob(self):
        """
        Tests that the 'include' glob pattern correctly filters the files to be searched.
        """
        result = search_file_content(path=self.test_dir, pattern="hello", include="*.txt")
        
        self.assertIn("content", result)
        self.assertEqual(len(result["content"]), 1)
        self.assertEqual(result["content"][0]['file_path'], os.path.relpath(self.file1_path, self.test_dir))

    def test_search_file_content_no_matches(self):
        """
        Tests that the tool returns an empty result set when no matches are found.
        """
        result = search_file_content(path=self.test_dir, pattern="non_existent_pattern")
        
        self.assertIn("content", result)
        self.assertEqual(result["content"], "No matches found.")

if __name__ == '__main__':
    unittest.main()