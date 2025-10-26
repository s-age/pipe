import unittest
import os
import tempfile
import shutil

from pipe.core.tools.write_file import write_file

class TestWriteFileTool(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_file_creates_new_file(self):
        """
        Tests that the write_file tool correctly creates a new file with the specified content.
        """
        new_file_path = os.path.join(self.test_dir, "new_file.txt")
        content_to_write = "This is a new file."
        
        result = write_file(
            file_path=new_file_path,
            content=content_to_write,
            project_root=self.test_dir
        )

        self.assertIn("message", result)
        self.assertNotIn("error", result)
        self.assertTrue(os.path.exists(new_file_path))

        with open(new_file_path, "r") as f:
            content_read = f.read()
        
        self.assertEqual(content_read, content_to_write)

    def test_write_file_overwrites_existing_file(self):
        """
        Tests that the write_file tool correctly overwrites an existing file.
        """
        existing_file_path = os.path.join(self.test_dir, "existing_file.txt")
        initial_content = "Initial content."
        with open(existing_file_path, "w") as f:
            f.write(initial_content)

        new_content = "This content should overwrite the old one."
        
        result = write_file(
            file_path=existing_file_path,
            content=new_content,
            project_root=self.test_dir
        )

        self.assertIn("message", result)
        
        with open(existing_file_path, "r") as f:
            content_read = f.read()
            
        self.assertEqual(content_read, new_content)

if __name__ == '__main__':
    unittest.main()
