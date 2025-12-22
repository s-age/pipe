import pytest
from pipe.core.models.prompts.roles import PromptRoles
from pydantic import ValidationError


class TestPromptRolesModel:
    """PromptRoles モデルのバリデーションとシリアライズのテスト。"""

    def test_valid_prompt_roles_creation(self):
        """有効なデータで PromptRoles を作成できることを確認。"""
        roles = PromptRoles(
            description="Test description", definitions=["Role 1", "Role 2"]
        )
        assert roles.description == "Test description"
        assert roles.definitions == ["Role 1", "Role 2"]

    def test_prompt_roles_validation_missing_required_field(self):
        """必須フィールドが欠けている場合に ValidationError が発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            PromptRoles(description="Missing definitions")
        assert "definitions" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            PromptRoles(definitions=["Missing description"])
        assert "description" in str(exc_info.value)

    def test_prompt_roles_model_dump_with_aliases(self):
        """by_alias=True でシリアライズした際に camelCase になることを確認。"""
        roles = PromptRoles(description="Test description", definitions=["Role 1"])
        dumped = roles.model_dump(by_alias=True)
        # フィールド名自体が単一単語なので camelCase 変換の影響は受けにくいが、
        # 基底クラス CamelCaseModel の挙動を確認
        assert "description" in dumped
        assert "definitions" in dumped
        assert dumped["description"] == "Test description"

    def test_prompt_roles_roundtrip_serialization(self):
        """シリアライズとデシリアライズでデータが保持されることを確認。"""
        import json

        original = PromptRoles(
            description="Complex description with symbols: @#$",
            definitions=["Definition A", "Definition B"],
        )

        # JSON 文字列へシリアライズ (camelCase)
        json_str = original.model_dump_json(by_alias=True)

        # 辞書に戻してバリデーション
        data = json.loads(json_str)
        restored = PromptRoles.model_validate(data)

        assert restored.description == original.description
        assert restored.definitions == original.definitions
        assert restored == original
