import pytest
from pipe.core.models.settings import (
    HyperparameterValue,
    ModelConfig,
    Parameters,
    Settings,
)


class TestSettingsModel:
    """Settings model validation and logic tests."""

    @pytest.fixture
    def default_parameters(self):
        """Create default parameters for testing."""
        return Parameters(
            temperature=HyperparameterValue(value=0.5, description="temp"),
            top_p=HyperparameterValue(value=0.9, description="top_p"),
            top_k=HyperparameterValue(value=40, description="top_k"),
        )

    def test_settings_legacy_initialization(self, default_parameters):
        """Test initialization with legacy fields (no model_configs)."""
        settings = Settings(
            model="legacy-model",
            search_model="legacy-model",
            context_limit=1000,
            parameters=default_parameters,
        )

        # Check that model_configs was automatically created
        assert settings.model_configs is not None
        assert len(settings.model_configs) == 1
        assert settings.model_configs[0].name == "legacy-model"
        assert settings.model_configs[0].context_limit == 1000

        # Check that model string was resolved to object
        assert isinstance(settings.model, ModelConfig)
        assert settings.model.name == "legacy-model"
        assert settings.model.context_limit == 1000

        # Check default search_model resolution
        assert isinstance(settings.search_model, ModelConfig)
        assert settings.search_model.name == "legacy-model"

    def test_settings_legacy_initialization_with_different_search_model(
        self, default_parameters
    ):
        """Test legacy initialization with distinct search model."""
        settings = Settings(
            model="model-a",
            search_model="model-b",
            context_limit=1000,
            parameters=default_parameters,
        )

        # Should create configs for both
        assert len(settings.model_configs) == 2
        names = [c.name for c in settings.model_configs]
        assert "model-a" in names
        assert "model-b" in names

        assert settings.model.name == "model-a"
        assert settings.search_model.name == "model-b"

    def test_settings_new_initialization(self, default_parameters):
        """Test initialization with explicit model_configs."""
        config_a = ModelConfig(
            name="model-a", context_limit=2000, cache_update_threshold=100
        )
        config_b = ModelConfig(
            name="model-b", context_limit=4000, cache_update_threshold=200
        )

        settings = Settings(
            model_configs=[config_a, config_b],
            model="model-a",
            search_model="model-b",
            parameters=default_parameters,
        )

        # Check resolution
        assert isinstance(settings.model, ModelConfig)
        assert settings.model.name == "model-a"
        assert settings.model.context_limit == 2000

        assert isinstance(settings.search_model, ModelConfig)
        assert settings.search_model.name == "model-b"
        assert settings.search_model.context_limit == 4000

    def test_validation_error_missing_context_limit_legacy(self, default_parameters):
        """Test error when model_configs is None and context_limit is missing."""
        with pytest.raises(
            ValueError,
            match="Either 'model_configs' or 'context_limit' must be provided",
        ):
            Settings(
                model="model-a", search_model="model-a", parameters=default_parameters
            )

    def test_validation_error_model_not_found(self, default_parameters):
        """Test error when model name is not in model_configs."""
        config = ModelConfig(
            name="existing-model", context_limit=1000, cache_update_threshold=100
        )
        with pytest.raises(ValueError, match="Model 'missing-model' not found"):
            Settings(
                model_configs=[config],
                model="missing-model",
                search_model="existing-model",
                parameters=default_parameters,
            )

    def test_validation_error_search_model_not_found(self, default_parameters):
        """Test error when search_model name is not in model_configs."""
        config = ModelConfig(
            name="model-a", context_limit=1000, cache_update_threshold=100
        )
        with pytest.raises(ValueError, match="Search model 'missing-search' not found"):
            Settings(
                model_configs=[config],
                model="model-a",
                search_model="missing-search",
                parameters=default_parameters,
            )

    def test_to_api_dict(self, default_parameters):
        """Test conversion to API dictionary format."""
        settings = Settings(
            model="api-model",
            context_limit=5000,
            cache_update_threshold=2500,
            parameters=default_parameters,
            search_model="api-model",
        )

        api_dict = settings.to_api_dict()

        # Check flattening and cleanup
        assert "modelConfigs" not in api_dict
        assert "model_configs" not in api_dict
        assert api_dict["model"] == "api-model"
        assert api_dict["contextLimit"] == 5000
        assert api_dict["cacheUpdateThreshold"] == 2500
        assert api_dict["searchModel"] == "api-model"

        # Check hyperparameters conversion
        assert "parameters" not in api_dict
        assert "hyperparameters" in api_dict
        assert api_dict["hyperparameters"]["temperature"] == 0.5
        assert api_dict["hyperparameters"]["top_p"] == 0.9
        assert api_dict["hyperparameters"]["top_k"] == 40

    def test_settings_roundtrip_serialization(self, default_parameters):
        """Test that serialization and deserialization preserve data."""
        original = Settings(
            model="roundtrip-model",
            search_model="roundtrip-model",
            context_limit=1000,
            parameters=default_parameters,
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        restored = Settings.model_validate_json(json_str)

        # Verify fields
        assert restored.model.name == original.model.name
        assert restored.context_limit == original.context_limit
        # Note: restored.model_configs will be populated/resolved again
        assert restored.model.name == "roundtrip-model"

    def test_model_validate(self, default_parameters):
        """Test validation from dictionary."""
        data = {
            "model": "validate-model",
            "searchModel": "validate-model",
            "contextLimit": 1000,
            "parameters": default_parameters.model_dump(by_alias=True),
        }

        settings = Settings.model_validate(data)
        assert settings.model.name == "validate-model"
