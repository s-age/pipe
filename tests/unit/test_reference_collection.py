import unittest
import os
import tempfile
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
            Reference(path=os.path.relpath(self.file1_path, self.project_root.name), disabled=False),
            Reference(path=os.path.relpath(self.file2_path, self.project_root.name), disabled=True), # This one should be ignored
        ]
        
        collection = ReferenceCollection(references)
        prompt_data = list(collection.get_for_prompt(self.project_root.name))
        
        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(prompt_data[0]['path'], os.path.relpath(self.file1_path, self.project_root.name))
        self.assertEqual(prompt_data[0]['content'], "This is file 1.")

    def test_get_for_prompt_with_empty_list(self):
        """
        Tests that get_for_prompt returns an empty iterator for an empty list of references.
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
            Reference(path=os.path.relpath(self.file1_path, self.project_root.name), disabled=False),
        ]
        
        collection = ReferenceCollection(references)
        prompt_data = list(collection.get_for_prompt(self.project_root.name))
        
        # It should only return the valid file within the project root
        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(prompt_data[0]['path'], os.path.relpath(self.file1_path, self.project_root.name))

    def test_get_for_prompt_handles_nonexistent_files_gracefully(self):
        """
        Tests that get_for_prompt does not raise an error for files that don't exist
        and simply omits them from the output.
        """
        non_existent_path = "nonexistent/file.txt"
        references = [
            Reference(path=non_existent_path, disabled=False),
            Reference(path=os.path.relpath(self.file1_path, self.project_root.name), disabled=False),
        ]
        
        collection = ReferenceCollection(references)
        
        # Ensure read_text_file is called with the correct non-existent path and returns None
        with patch('pipe.core.collections.references.read_text_file') as mock_read:
            # Set up the mock to return None for the non-existent file
            # and real content for the existing one.
            def side_effect(path):
                if path == os.path.abspath(os.path.join(self.project_root.name, non_existent_path)):
                    return None
                elif path == self.file1_path:
                    with open(path, 'r') as f:
                        return f.read()
                return None
            mock_read.side_effect = side_effect
            
            prompt_data = list(collection.get_for_prompt(self.project_root.name))
        
        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(prompt_data[0]['path'], os.path.relpath(self.file1_path, self.project_root.name))

if __name__ == '__main__':
    unittest.main()
