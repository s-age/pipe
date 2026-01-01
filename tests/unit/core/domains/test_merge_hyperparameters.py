"""Unit tests for Hyperparameters domain logic."""

from pipe.core.domains.hyperparameters import merge_hyperparameters
from pipe.core.models.hyperparameters import Hyperparameters


class TestMergeHyperparameters:
    """Tests for merge_hyperparameters function."""

    def test_merge_with_none_existing(self):
        """Test merging when existing hyperparameters are None."""
        new_params = Hyperparameters(temperature=0.5, top_p=0.9, top_k=40)
        result = merge_hyperparameters(None, new_params)

        assert result == new_params
        assert (
            result is new_params
        )  # Should return the same instance if existing is None

    def test_merge_with_all_new_values(self):
        """Test merging when all new values are provided."""
        existing = Hyperparameters(temperature=0.1, top_p=0.1, top_k=1)
        new_params = Hyperparameters(temperature=0.8, top_p=0.9, top_k=50)

        result = merge_hyperparameters(existing, new_params)

        assert result.temperature == 0.8
        assert result.top_p == 0.9
        assert result.top_k == 50
        assert result is not existing
        assert result is not new_params

    def test_merge_with_partial_new_values(self):
        """Test merging when only some new values are provided."""
        existing = Hyperparameters(temperature=0.5, top_p=0.5, top_k=20)
        new_params = Hyperparameters(temperature=0.8, top_p=None, top_k=None)

        result = merge_hyperparameters(existing, new_params)

        assert result.temperature == 0.8
        assert result.top_p == 0.5
        assert result.top_k == 20

    def test_merge_with_no_new_values(self):
        """Test merging when new_params has all None values."""
        existing = Hyperparameters(temperature=0.5, top_p=0.5, top_k=20)
        new_params = Hyperparameters(temperature=None, top_p=None, top_k=None)

        result = merge_hyperparameters(existing, new_params)

        assert result.temperature == 0.5
        assert result.top_p == 0.5
        assert result.top_k == 20
        assert result == existing
        assert result is not existing  # Should be a new instance

    def test_merge_preserves_immutability(self):
        """Test that the original Hyperparameters objects are not modified."""
        existing = Hyperparameters(temperature=0.5, top_p=0.5, top_k=20)
        new_params = Hyperparameters(temperature=0.8, top_p=0.9, top_k=50)

        existing_copy = existing.model_copy(deep=True)
        new_params_copy = new_params.model_copy(deep=True)

        merge_hyperparameters(existing, new_params)

        assert existing == existing_copy
        assert new_params == new_params_copy

    def test_merge_with_existing_none_fields(self):
        """Test merging when existing has None fields and new_params provides them."""
        existing = Hyperparameters(temperature=None, top_p=None, top_k=None)
        new_params = Hyperparameters(temperature=0.7, top_p=0.8, top_k=30)

        result = merge_hyperparameters(existing, new_params)

        assert result.temperature == 0.7
        assert result.top_p == 0.8
        assert result.top_k == 30
