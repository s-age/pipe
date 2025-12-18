import json
import os
import shutil
import unittest
import unittest.mock
import warnings

from pipe.core.tools.read_many_files import read_many_files
from pipe.core.utils.file import write_yaml_file


class TestReadManyFiles(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

        self.original_cwd = os.getcwd()
        import tempfile

        self.test_dir = tempfile.mkdtemp(prefix="pipe_test_read_many_files_")

        os.chdir(self.test_dir)

        # Patch get_project_root to return the test directory
        self.patcher = unittest.mock.patch(
            "pipe.core.tools.read_many_files.get_project_root"
        )
        self.mock_get_project_root = self.patcher.start()
        self.mock_get_project_root.return_value = self.test_dir

        # Also patch get_project_root in SettingsRepository
        self.patcher2 = unittest.mock.patch(
            "pipe.core.repositories.settings_repository.get_project_root"
        )
        self.mock_get_project_root2 = self.patcher2.start()
        self.mock_get_project_root2.return_value = self.test_dir

        # Create setting.yml
        self.settings_data = {
            "model": "gemini-2.5-flash",
            "search_model": "gemini-2.5-flash",
            "context_limit": 100000,
            "api_mode": "gemini-api",
            "max_tool_calls": 5,
            "language": "english",
            "yolo": False,
            "parameters": {
                "temperature": {"value": 0.2, "description": "desc"},
                "top_p": {"value": 0.5, "description": "desc"},
                "top_k": {"value": 5, "description": "desc"},
            },
            "expert_mode": False,
            "sessions_path": "sessions",
            "reference_ttl": 3,
            "tool_response_expiration": 3,
            "timezone": "UTC",
        }
        write_yaml_file("setting.yml", self.settings_data)

        # Create sessions dir
        self.sessions_dir = os.path.join(self.test_dir, "sessions")
        os.makedirs(self.sessions_dir)

        # Create dummy session
        self.test_session_id = "test_session"
        self.session_file = os.path.join(
            self.sessions_dir, f"{self.test_session_id}.json"
        )
        with open(self.session_file, "w") as f:
            json.dump(
                {
                    "session_id": self.test_session_id,
                    "references": [],
                    "turns": [],
                    "created_at": "2023-01-01T00:00:00Z",
                },
                f,
            )

        os.environ["PIPE_SESSION_ID"] = self.test_session_id

        # Create dummy files
        self.file1 = "file1.txt"
        with open(self.file1, "w") as f:
            f.write("content1")

        self.subdir = "subdir"
        os.makedirs(self.subdir)
        self.file2 = os.path.join(self.subdir, "file2.txt")
        with open(self.file2, "w") as f:
            f.write("content2")

        self.ignored_file = "ignored.log"
        with open(self.ignored_file, "w") as f:
            f.write("log")

    def tearDown(self):
        self.patcher.stop()
        self.patcher2.stop()
        os.chdir(self.original_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

    def _normalize_paths(self, file_contents):
        return {os.path.realpath(k): v for k, v in file_contents.items()}

    def test_read_many_files_success(self):
        result = read_many_files(paths=["**/*.txt"])
        self.assertIsNotNone(result.data.files)
        self.assertEqual(len(result.data.files), 2)
        file_contents = self._normalize_paths(
            {f.path: f.content for f in result.data.files}
        )
        abs_file1 = os.path.realpath(os.path.abspath(self.file1))
        abs_file2 = os.path.realpath(os.path.abspath(self.file2))

        self.assertIn(abs_file1, file_contents)
        self.assertEqual(file_contents[abs_file1], "content1")
        self.assertIn(abs_file2, file_contents)
        self.assertEqual(file_contents[abs_file2], "content2")

        # Verify session file
        with open(self.session_file) as f:
            data = json.load(f)

        references = data.get("references", [])
        self.assertEqual(len(references), 2)

        found_file1 = any(
            os.path.realpath(ref["path"]) == abs_file1 for ref in references
        )
        found_file2 = any(
            os.path.realpath(ref["path"]) == abs_file2 for ref in references
        )

        self.assertTrue(found_file1)
        self.assertTrue(found_file2)

    def test_read_many_files_exclude(self):
        result = read_many_files(paths=["**/*.txt", "*.log"], exclude=["**/subdir/**"])
        self.assertIsNotNone(result.data.files)
        self.assertEqual(len(result.data.files), 1)  # Only file1 should be included

        file_contents = self._normalize_paths(
            {f.path: f.content for f in result.data.files}
        )
        abs_file1 = os.path.realpath(os.path.abspath(self.file1))
        abs_file2 = os.path.realpath(os.path.abspath(self.file2))

        self.assertIn(abs_file1, file_contents)
        self.assertEqual(file_contents[abs_file1], "content1")
        self.assertNotIn(abs_file2, file_contents)  # file2 should be excluded

        with open(self.session_file) as f:
            data = json.load(f)
        references = data.get("references", [])

        # Check that file2 is NOT in paths (in references)
        found_file2_in_refs = any(
            os.path.realpath(ref["path"]) == abs_file2 for ref in references
        )
        self.assertFalse(found_file2_in_refs)

        # Check that file1 IS in paths (in references)
        found_file1_in_refs = any(
            os.path.realpath(ref["path"]) == abs_file1 for ref in references
        )
        self.assertTrue(found_file1_in_refs)

    def test_read_many_files_no_session_id(self):
        # Temporarily remove PIPE_SESSION_ID from environment
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

        result = read_many_files(paths=["**/*.txt"])

        self.assertIsNotNone(result.data.files)
        self.assertEqual(len(result.data.files), 2)
        file_contents = self._normalize_paths(
            {f.path: f.content for f in result.data.files}
        )
        abs_file1 = os.path.realpath(os.path.abspath(self.file1))
        abs_file2 = os.path.realpath(os.path.abspath(self.file2))

        self.assertIn(abs_file1, file_contents)
        self.assertEqual(file_contents[abs_file1], "content1")
        self.assertIn(abs_file2, file_contents)
        self.assertEqual(file_contents[abs_file2], "content2")

        # Assert no references were added to the session file
        with open(self.session_file) as f:
            data = json.load(f)
        references = data.get("references", [])
        self.assertEqual(len(references), 0)

        # When no session ID is provided, no message should be present
        self.assertIsNone(result.data.message)

    def test_read_many_files_no_match(self):
        result = read_many_files(paths=["**/*.xyz"])  # A pattern that won't match
        # any files

        self.assertIsNotNone(result.data.files)
        self.assertEqual(len(result.data.files), 0)
        self.assertEqual(result.data.message, "No files found matching the criteria.")

    def test_read_many_files_max_limit_exceeded(self):
        # Default max_files is 20. We have 2 .txt files.
        # Set max_files to 1, expecting it to truncate to 1 file with a warning.
        result = read_many_files(paths=["**/*.txt"], max_files=1)

        # Should succeed but truncate
        self.assertIsNone(result.error)
        self.assertIsNotNone(result.data.files)
        self.assertEqual(len(result.data.files), 1)

        # Should have a truncation warning message
        self.assertIsNotNone(result.data.message)
        self.assertIn("Found 2 files but showing only the first 1", result.data.message)

        # Test with a higher limit that includes all files (no truncation)
        result_pass = read_many_files(paths=["**/*.txt"], max_files=2)
        self.assertIsNone(result_pass.error)
        self.assertIsNotNone(result_pass.data.files)
        self.assertEqual(len(result_pass.data.files), 2)
        # No truncation warning
        if result_pass.data.message:
            self.assertNotIn("Found", result_pass.data.message)
