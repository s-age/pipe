import unittest
from pipe.core.models.reference import Reference

class TestReferenceModel(unittest.TestCase):

    def test_reference_creation_with_all_fields(self):
        """
        Tests that a Reference object can be created with all fields specified.
        """
        ref_data = {
            "path": "src/main.py",
            "disabled": True
        }
        reference = Reference(**ref_data)
        self.assertEqual(reference.path, "src/main.py")
        self.assertTrue(reference.disabled)

    def test_reference_creation_with_defaults(self):
        """
        Tests that a Reference object uses the default value for 'disabled'
        when it is not provided.
        """
        ref_data = {
            "path": "README.md"
        }
        reference = Reference(**ref_data)
        self.assertEqual(reference.path, "README.md")
        self.assertFalse(reference.disabled, "The 'disabled' field should default to False")

if __name__ == '__main__':
    unittest.main()
