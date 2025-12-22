"""Tests for the base model class."""

from pipe.core.models.base import CamelCaseModel


class MockModel(CamelCaseModel):
    """A concrete implementation of CamelCaseModel for testing."""

    test_field_name: str
    another_field: int = 10


class TestCamelCaseModel:
    """Tests for the CamelCaseModel base class."""

    def test_initialization_with_snake_case(self):
        """Test that the model can be initialized using snake_case field names."""
        model = MockModel(test_field_name="value", another_field=20)
        assert model.test_field_name == "value"
        assert model.another_field == 20

    def test_initialization_with_camel_case(self):
        """Test that the model can be initialized using camelCase aliases
        (populate_by_name=True).
        """
        # Pydantic V2 with populate_by_name=True allows using aliases in the constructor
        model = MockModel(testFieldName="value", anotherField=30)
        assert model.test_field_name == "value"
        assert model.another_field == 30

    def test_serialization_to_camel_case_dict(self):
        """Test that model_dump(by_alias=True) produces camelCase keys."""
        model = MockModel(test_field_name="value")
        dumped = model.model_dump(by_alias=True)
        assert "testFieldName" in dumped
        assert dumped["testFieldName"] == "value"
        assert "anotherField" in dumped
        assert dumped["anotherField"] == 10

    def test_serialization_json_mode(self):
        """Test that model_dump(mode='json', by_alias=True) produces camelCase keys."""
        model = MockModel(test_field_name="value")
        dumped = model.model_dump(mode="json", by_alias=True)
        assert "testFieldName" in dumped
        assert dumped["testFieldName"] == "value"

    def test_model_dump_json(self):
        """Test that model_dump_json(by_alias=True) produces a JSON string with
        camelCase keys.
        """
        import json

        model = MockModel(test_field_name="value")
        json_str = model.model_dump_json(by_alias=True)
        parsed = json.loads(json_str)
        assert "testFieldName" in parsed
        assert parsed["testFieldName"] == "value"

    def test_deserialization_from_camel_case(self):
        """Test that the model can be validated from a dictionary with camelCase
        keys.
        """
        data = {"testFieldName": "restored", "anotherField": 100}
        model = MockModel.model_validate(data)
        assert model.test_field_name == "restored"
        assert model.another_field == 100

    def test_from_attributes(self):
        """Test that from_attributes=True allows creation from object attributes."""

        class MockObj:
            def __init__(self):
                self.test_field_name = "from_obj"
                self.another_field = 50

        obj = MockObj()
        model = MockModel.model_validate(obj)
        assert model.test_field_name == "from_obj"
        assert model.another_field == 50
