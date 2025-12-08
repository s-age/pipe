import os
import shutil
import tempfile
import unittest

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.tools.read_many_files import read_many_files


class TestReadManyFilesTool(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()

        # Create dummy files and directories for testing
        self.dir1 = os.path.join(self.project_root, "dir1")
        os.makedirs(self.dir1)
        self.file1 = os.path.join(self.dir1, "file1.txt")
        with open(self.file1, "w") as f:
            f.write("content1")
        self.file2 = os.path.join(self.dir1, "file2.log")
        with open(self.file2, "w") as f:
            f.write("content2")
        self.file3 = os.path.join(self.project_root, "file3.md")
        with open(self.file3, "w") as f:
            f.write("content3")

        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.service_factory = ServiceFactory(self.project_root, self.settings)
        self.session_service = self.service_factory.create_session_service()
        self.reference_service = self.service_factory.create_session_reference_service()

        # Create a session
        session = self.session_service.create_new_session("Test", "Test", [])
        self.session_id = session.session_id

        # Add method to session_service for tool compatibility
        self.session_service.add_multiple_references = (
            self.reference_service.add_multiple_references
        )

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_simple_glob(self):
        read_many_files(
            paths=["dir1/*.txt"],
            session_service=self.session_service,
            session_id=self.session_id,
        )
        fetched_session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(fetched_session.references), 1)
        self.assertTrue(
            any("file1.txt" in ref.path for ref in fetched_session.references)
        )

    def test_directory_glob(self):
        read_many_files(
            paths=["dir1"],
            useDefaultExcludes=False,  # Disable default excludes to find .log file
            session_service=self.session_service,
            session_id=self.session_id,
        )
        fetched_session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(fetched_session.references), 2)

    def test_default_excludes(self):
        read_many_files(
            paths=["**/*"],
            useDefaultExcludes=True,
            session_service=self.session_service,
            session_id=self.session_id,
        )
        # Check that .log files are excluded
        fetched_session = self.session_service.get_session(self.session_id)
        paths = [ref.path for ref in fetched_session.references]
        # file2.log should be excluded
        self.assertFalse(any("file2.log" in p for p in paths))
        # file1.txt and file3.md should be included
        self.assertTrue(any("file1.txt" in p for p in paths))
        self.assertTrue(any("file3.md" in p for p in paths))

    def test_custom_exclude(self):
        read_many_files(
            paths=["dir1/*"],
            exclude=["*.log"],
            useDefaultExcludes=False,
            session_service=self.session_service,
            session_id=self.session_id,
        )
        fetched_session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(fetched_session.references), 1)
        self.assertTrue(
            any("file1.txt" in ref.path for ref in fetched_session.references)
        )

    def test_custom_include(self):
        read_many_files(
            paths=["dir1/*"],
            include=["*.log"],
            useDefaultExcludes=False,  # Disable default excludes
            session_service=self.session_service,
            session_id=self.session_id,
        )
        fetched_session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(fetched_session.references), 1)
        self.assertTrue(
            any("file2.log" in ref.path for ref in fetched_session.references)
        )

    def test_no_files_found(self):
        result = read_many_files(
            paths=["non_existent_dir/*"],
            session_service=self.session_service,
            session_id=self.session_id,
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "No files found matching the criteria.")
        fetched_session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(fetched_session.references), 0)

    def test_no_session_service(self):
        result = read_many_files(paths=["dir1/*.txt"], session_id=self.session_id)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires an active session.")

    def test_error_handling(self):
        # Test with invalid path that gets no files
        result = read_many_files(
            paths=["/invalid/../path"],
            session_service=self.session_service,
            session_id=self.session_id,
        )
        # Should return message about no files found
        self.assertIsInstance(result, dict)
        self.assertTrue(
            "error" in result or "message" in result,
            f"Expected 'error' or 'message' in result, got: {result}",
        )


if __name__ == "__main__":
    unittest.main()
