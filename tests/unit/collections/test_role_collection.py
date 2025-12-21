import os
import tempfile
import unittest

from pipe.core.collections.roles import RoleCollection
from pipe.core.repositories.resource_repository import ResourceRepository


class TestRoleCollection(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the project root
        self.project_root = tempfile.TemporaryDirectory()

        # Create some dummy role files for testing
        self.role1_path_rel = "roles/engineer.md"
        self.role2_path_rel = "roles/reviewer.md"
        self.non_existent_path_rel = "roles/non_existent.md"

        self.role1_path_abs = os.path.join(self.project_root.name, self.role1_path_rel)
        self.role2_path_abs = os.path.join(self.project_root.name, self.role2_path_rel)

        os.makedirs(os.path.dirname(self.role1_path_abs), exist_ok=True)

        with open(self.role1_path_abs, "w") as f:
            f.write("You are a senior software engineer.")

        with open(self.role2_path_abs, "w") as f:
            f.write("You are a meticulous code reviewer.")

        # Create a ResourceRepository for testing
        self.resource_repository = ResourceRepository(self.project_root.name)

    def tearDown(self):
        # Clean up the temporary directory and files
        self.project_root.cleanup()

    def test_get_for_prompt_with_valid_roles(self):
        """
        Tests that get_for_prompt correctly loads and returns the content of
        specified role files.
        """
        role_paths = [self.role1_path_rel, self.role2_path_rel]
        collection = RoleCollection(role_paths)

        prompt_data = collection.get_for_prompt(self.resource_repository)

        self.assertEqual(len(prompt_data), 2)
        self.assertIn("You are a senior software engineer.", prompt_data)
        self.assertIn("You are a meticulous code reviewer.", prompt_data)

    def test_get_for_prompt_with_empty_list(self):
        """
        Tests that get_for_prompt returns an empty list when initialized with an
        empty list.
        """
        collection = RoleCollection([])
        prompt_data = collection.get_for_prompt(self.resource_repository)
        self.assertEqual(len(prompt_data), 0)

    def test_get_for_prompt_handles_nonexistent_files_gracefully(self):
        """
        Tests that get_for_prompt ignores paths that do not correspond to existing files
        and does not raise an error.
        """
        role_paths = [self.role1_path_rel, self.non_existent_path_rel]
        collection = RoleCollection(role_paths)

        prompt_data = collection.get_for_prompt(self.resource_repository)

        self.assertEqual(len(prompt_data), 1)
        self.assertEqual(prompt_data[0], "You are a senior software engineer.")


if __name__ == "__main__":
    unittest.main()
