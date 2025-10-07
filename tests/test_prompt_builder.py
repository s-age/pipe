import unittest
from pathlib import Path
from src.prompt_builder import PromptBuilder

class TestPromptBuilder(unittest.TestCase):

    def test_build_prompt(self):
        """Test the basic prompt construction."""
        builder = PromptBuilder(
            purpose="Test Purpose",
            background="Test Background",
            roles_paths=[]
        )
        prompt = builder.build(history=[], instruction="Test Instruction")
        self.assertIn("Test Purpose", prompt)
        self.assertIn("Test Background", prompt)
        self.assertIn("Test Instruction", prompt)

if __name__ == '__main__':
    unittest.main()
