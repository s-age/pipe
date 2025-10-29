import unittest

from pipe.core.tools.save_memory import save_memory


class TestSaveMemoryTool(unittest.TestCase):
    def test_save_memory_returns_success(self):
        """
        Tests that the save_memory tool returns a success message.
        """
        fact_to_save = "The user prefers Python."
        result = save_memory(fact=fact_to_save)

        expected_result = {"status": "success", "message": "Fact saved (stub)."}
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
