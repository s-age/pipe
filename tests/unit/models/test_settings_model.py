import unittest

from pipe.core.models.settings import (
    HyperparameterValue,
    ModelConfig,
    Parameters,
    Settings,
)


class TestSettingsModel(unittest.TestCase):
    def test_settings_creation_with_full_data(self):
        """
        Tests that a Settings object can be correctly created from a nested dictionary,
        simulating data loaded from a YAML file.
        """
        settings_data = {
            "model_configs": [
                {
                    "name": "gemini-pro",
                    "context_limit": 50000,
                    "cache_update_threshold": 20000,
                }
            ],
            "model": "gemini-pro",
            "search_model": "gemini-pro",
            "api_mode": "gemini-cli",
            "language": "Japanese",
            "yolo": True,
            "expert_mode": True,
            "timezone": "Asia/Tokyo",
            "parameters": {
                "temperature": {"value": 0.8, "description": "temp"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 30, "description": "k"},
            },
        }

        settings = Settings(**settings_data)

        self.assertIsInstance(settings.model, ModelConfig)
        self.assertEqual(settings.model.name, "gemini-pro")
        self.assertEqual(settings.model.context_limit, 50000)
        self.assertEqual(settings.model.cache_update_threshold, 20000)
        self.assertEqual(settings.api_mode, "gemini-cli")
        self.assertTrue(settings.expert_mode)
        self.assertTrue(settings.yolo)
        self.assertIsInstance(settings.parameters, Parameters)
        self.assertIsInstance(settings.parameters.temperature, HyperparameterValue)
        self.assertEqual(settings.parameters.temperature.value, 0.8)
        self.assertEqual(settings.parameters.top_k.description, "k")

    def test_settings_creation_requires_parameters(self):
        """
        Tests that the 'parameters' field is required and raises an error if missing.
        Pydantic should raise a ValidationError.
        """
        settings_data = {
            "model_configs": [
                {
                    "name": "gemini-pro",
                    "context_limit": 50000,
                    "cache_update_threshold": 20000,
                }
            ],
            "model": "gemini-pro",
            # 'parameters' field is missing
        }

        with self.assertRaises(
            Exception
        ):  # Pydantic's ValidationError is a good candidate
            Settings(**settings_data)

    def test_model_not_found_raises_error(self):
        """
        Tests that specifying a model not in model_configs raises a ValueError.
        """
        settings_data = {
            "model_configs": [
                {
                    "name": "gemini-pro",
                    "context_limit": 50000,
                    "cache_update_threshold": 20000,
                }
            ],
            "model": "non-existent-model",
            "search_model": "gemini-pro",
            "parameters": {
                "temperature": {"value": 0.8, "description": "temp"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 30, "description": "k"},
            },
        }

        with self.assertRaises(ValueError) as context:
            Settings(**settings_data)

        self.assertIn("not found in model_configs", str(context.exception))


if __name__ == "__main__":
    unittest.main()
