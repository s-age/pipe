import unittest

from pipe.core.models.hyperparameters import Hyperparameters


class TestHyperparametersModel(unittest.TestCase):
    def test_hyperparameters_creation_with_full_data(self):
        """
        Tests the creation of a Hyperparameters instance with all values provided.
        """
        hyperparameters_data = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
        }
        hyperparams = Hyperparameters(**hyperparameters_data)

        self.assertEqual(hyperparams.temperature, 0.9)
        self.assertEqual(hyperparams.top_p, 0.95)
        self.assertEqual(hyperparams.top_k, 40)

    def test_hyperparameters_creation_with_partial_data(self):
        """
        Tests that a Hyperparameters instance can be created with only some values,
        and others remain None.
        """
        hyperparameters_data = {"temperature": 0.7}
        hyperparams = Hyperparameters(**hyperparameters_data)

        self.assertEqual(hyperparams.temperature, 0.7)
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


if __name__ == "__main__":
    unittest.main()
