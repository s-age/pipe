import unittest
from pipe.core.models.hyperparameters import HyperparameterValue, Hyperparameters

class TestHyperparametersModel(unittest.TestCase):

    def test_hyperparameter_value_creation(self):
        """
        Tests the creation of a HyperparameterValue instance.
        """
        value_data = {
            "value": 0.8,
            "description": "This should be ignored by the model"
        }
        hp_value = HyperparameterValue(**value_data)
        self.assertEqual(hp_value.value, 0.8)
        with self.assertRaises(AttributeError):
            _ = hp_value.description

    def test_hyperparameters_creation_with_full_data(self):
        """
        Tests the creation of a Hyperparameters instance with all values provided.
        """
        hyperparameters_data = {
            "temperature": {"value": 0.9, "description": "Temp desc"},
            "top_p": {"value": 0.95, "description": "TopP desc"},
            "top_k": {"value": 40, "description": "TopK desc"}
        }
        hyperparams = Hyperparameters(**hyperparameters_data)
        
        self.assertIsInstance(hyperparams.temperature, HyperparameterValue)
        self.assertEqual(hyperparams.temperature.value, 0.9)
        self.assertEqual(hyperparams.top_p.value, 0.95)
        self.assertEqual(hyperparams.top_k.value, 40)

    def test_hyperparameters_creation_with_partial_data(self):
        """
        Tests that a Hyperparameters instance can be created with only some values,
        and others remain None.
        """
        hyperparameters_data = {
            "temperature": {"value": 0.7, "description": "Only temp"}
        }
        hyperparams = Hyperparameters(**hyperparameters_data)
        
        self.assertEqual(hyperparams.temperature.value, 0.7)
        self.assertIsNone(hyperparams.top_p)
        self.assertIsNone(hyperparams.top_k)

    def test_hyperparameters_creation_with_empty_data(self):
        """
        Tests that a Hyperparameters instance can be created with no data,
        resulting in all fields being None.
        """
        hyperparams = Hyperparameters()
        
        self.assertIsNone(hyperparams.temperature)
        self.assertIsNone(hyperparams.top_p)
        self.assertIsNone(hyperparams.top_k)

if __name__ == '__main__':
    unittest.main()
