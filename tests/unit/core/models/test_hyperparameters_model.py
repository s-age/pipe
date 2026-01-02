import pytest
from pipe.core.models.hyperparameters import Hyperparameters
from pydantic import ValidationError


class TestHyperparametersModel:
    """Hyperparameters model validation and serialization tests."""

    def test_default_values(self):
        """Test that default values are all None."""
        hp = Hyperparameters()
        assert hp.temperature is None
        assert hp.top_p is None
        assert hp.top_k is None

    def test_valid_values(self):
        """Test creating Hyperparameters with valid values."""
        hp = Hyperparameters(temperature=0.7, top_p=0.9, top_k=40)
        assert hp.temperature == 0.7
        assert hp.top_p == 0.9
        assert hp.top_k == 40

    @pytest.mark.parametrize(
        "field, value",
        [
            ("temperature", -0.1),
            ("temperature", 2.1),
            ("top_p", -0.1),
            ("top_p", 1.1),
            ("top_k", -1),
        ],
    )
    def test_invalid_values(self, field, value):
        """Test that invalid values raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Hyperparameters(**{field: value})
        assert field in str(exc_info.value)

    def test_model_dump_json_mode(self):
        """Test serialization with model_dump(mode='json') produces camelCase keys."""
        hp = Hyperparameters(temperature=0.5, top_p=0.8, top_k=20)
        dumped = hp.model_dump(mode="json", by_alias=True)
        # CamelCaseModel converts snake_case fields to camelCase
        assert dumped["temperature"] == 0.5
        assert dumped["topP"] == 0.8
        assert dumped["topK"] == 20

    def test_model_validate_camel_case(self):
        """Test deserialization from camelCase data."""
        data = {"temperature": 0.5, "topP": 0.8, "topK": 20}
        hp = Hyperparameters.model_validate(data)
        assert hp.temperature == 0.5
        assert hp.top_p == 0.8
        assert hp.top_k == 20
