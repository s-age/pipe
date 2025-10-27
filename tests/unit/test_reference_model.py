import unittest

from pipe.core.models.reference import Reference
from pydantic import ValidationError


class TestReferenceModel(unittest.TestCase):
    def test_reference_creation_with_all_fields(self):
        """
        Tests that a Reference object can be created with all fields specified.
        """
        ref_data = {"path": "src/main.py", "disabled": True, "ttl": 5}
        reference = Reference(**ref_data)
        self.assertEqual(reference.path, "src/main.py")
        self.assertTrue(reference.disabled)
        self.assertEqual(reference.ttl, 5)

    def test_reference_creation_with_defaults(self):
        """
        Tests that a Reference object uses default values for 'disabled' and 'ttl'.
        """
        ref_data = {"path": "README.md"}
        reference = Reference(**ref_data)
        self.assertEqual(reference.path, "README.md")
        self.assertFalse(
            reference.disabled, "The 'disabled' field should default to False"
        )
        self.assertIsNone(reference.ttl, "The 'ttl' field should default to None")

    def test_reference_ttl_validation(self):
        """
        Tests that the 'ttl' field only accepts integers.
        """
        # Valid cases
        Reference(path="a.txt", ttl=10)
        Reference(path="b.txt", ttl=0)
        Reference(path="c.txt", ttl=None)

        # Invalid case
        with self.assertRaises(ValidationError):
            Reference(path="d.txt", ttl="not-an-integer")


if __name__ == "__main__":
    unittest.main()
