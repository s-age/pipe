import argparse
import unittest

from pipe.core.models.args import TaktArgs


class TestArgsModel(unittest.TestCase):
    def test_taktargs_creation_from_parsed_args(self):
        """
        Tests that TaktArgs is correctly created from an argparse.Namespace object.
        """
        # Simulate the output of argparse.parse_args()
        parsed_args = argparse.Namespace(
            dry_run=True,
            session="test-session",
            purpose="Test purpose",
            background="Test background",
            roles="roles/a.md,roles/b.md",
            parent="parent-session",
            instruction="Do something",
            references="file1.txt, file2.txt",
            references_persist="file1.txt",
            artifacts="artifact1.txt, artifact2.json",
            procedure="procedure.md",
            multi_step_reasoning=True,
            fork="fork-session",
            at_turn=5,
            api_mode=None,  # Ensure None is handled correctly
        )

        takt_args = TaktArgs.from_parsed_args(parsed_args)

        self.assertTrue(takt_args.dry_run)
        self.assertEqual(takt_args.session, "test-session")
        self.assertEqual(takt_args.purpose, "Test purpose")
        self.assertEqual(takt_args.background, "Test background")
        self.assertEqual(takt_args.roles, ["roles/a.md", "roles/b.md"])
        self.assertEqual(takt_args.parent, "parent-session")
        self.assertEqual(takt_args.instruction, "Do something")
        self.assertEqual(takt_args.references, ["file1.txt", "file2.txt"])
        self.assertEqual(takt_args.references_persist, ["file1.txt"])
        self.assertEqual(takt_args.artifacts, ["artifact1.txt", "artifact2.json"])
        self.assertEqual(takt_args.procedure, "procedure.md")
        self.assertTrue(takt_args.multi_step_reasoning)
        self.assertEqual(takt_args.fork, "fork-session")
        self.assertEqual(takt_args.at_turn, 5)

    def test_taktargs_creation_with_minimal_args(self):
        """
        Tests that TaktArgs handles missing optional arguments gracefully.
        """
        parsed_args = argparse.Namespace(
            dry_run=False,
            session=None,
            purpose=None,
            background=None,
            roles=None,
            parent=None,
            instruction="Minimal instruction",
            references=None,
            references_persist=None,
            artifacts=None,
            procedure=None,
            multi_step_reasoning=False,
            fork=None,
            at_turn=None,
            api_mode=None,
        )

        takt_args = TaktArgs.from_parsed_args(parsed_args)

        self.assertFalse(takt_args.dry_run)
        self.assertIsNone(takt_args.session)
        self.assertIsNone(takt_args.purpose)
        self.assertEqual(takt_args.roles, [])
        self.assertEqual(takt_args.references, [])
        self.assertEqual(takt_args.references_persist, [])
        self.assertEqual(takt_args.artifacts, [])
        self.assertIsNone(takt_args.procedure)
        self.assertEqual(takt_args.instruction, "Minimal instruction")


if __name__ == "__main__":
    unittest.main()
