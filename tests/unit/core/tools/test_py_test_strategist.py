"""Unit tests for py_test_strategist tool."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_condition_analyzer import (
    AnalyzeConditionResult,
    FunctionAnalysis,
    MockCandidate,
)
from pipe.core.tools.py_test_strategist import (
    FunctionStrategy,
    MockTarget,
    SerializationHint,
    _analyze_model_base_class,
    _extract_import_info,
    _extract_test_functions,
    _find_matching_test_function,
    _find_test_file,
    _generate_overall_recommendation,
    _get_module_namespace,
    _is_data_model_import,
    _is_stdlib_module,
    _recommend_test_level,
    py_test_strategist,
)
from pipe.core.tools.py_test_strategist import TestLevel as TLevel


class TestIsDataModelImport:
    """Tests for _is_data_model_import function."""

    @pytest.mark.parametrize(
        "import_path, expected",
        [
            ("from pipe.core.models.session import Session", True),
            ("from pipe.core.schemas.user import User", True),
            ("import pydantic", True),
            ("from dataclasses import dataclass", True),
            ("import os", False),
            ("from pipe.core.services.session_service import SessionService", False),
        ],
    )
    def test_is_data_model_import(self, import_path: str, expected: bool):
        """Test detection of data model imports."""
        assert _is_data_model_import(import_path) == expected


class TestIsStdlibModule:
    """Tests for _is_stdlib_module function."""

    @pytest.mark.parametrize(
        "import_path, dependency_name, expected",
        [
            ("import os", "os", True),
            ("import os.path", "os.path", True),
            ("from os.path import join", "join", True),
            ("from pathlib import Path", "Path", True),
            ("import json", "json", True),
            ("import requests", "requests", False),
            ("from pipe.core.utils import path", "path", False),
            ("from os.path import join as os_join", "os_join", True),
        ],
    )
    def test_is_stdlib_module(
        self, import_path: str, dependency_name: str, expected: bool
    ):
        """Test detection of standard library modules."""
        assert _is_stdlib_module(import_path, dependency_name) == expected


class TestGetModuleNamespace:
    """Tests for _get_module_namespace function."""

    @patch("pipe.core.tools.py_test_strategist.Path")
    def test_get_module_namespace_src(self, mock_path_class):
        """Test namespace extraction for files in src/."""
        mock_path = mock_path_class.return_value.resolve.return_value
        mock_path.parts = ("/", "project", "src", "pipe", "core", "utils", "path.py")
        mock_path.stem = "path"

        result = _get_module_namespace("src/pipe/core/utils/path.py")
        assert result == "pipe.core.utils.path"

    @patch("pipe.core.tools.py_test_strategist.Path")
    def test_get_module_namespace_no_src(self, mock_path_class):
        """Test namespace extraction when src is not in path."""
        mock_path = mock_path_class.return_value.resolve.return_value
        mock_path.parts = ("/", "project", "pipe", "core", "utils", "path.py")
        mock_path.stem = "path"

        result = _get_module_namespace("pipe/core/utils/path.py")
        assert result == "path"


class TestFindMatchingTestFunction:
    """Tests for _find_matching_test_function function."""

    def test_exact_match(self):
        """Test exact match (test_ + function_name)."""
        test_funcs = ["test_process", "test_save"]
        assert _find_matching_test_function("process", test_funcs) == "test_process"

    def test_partial_match(self):
        """Test partial match (case-insensitive)."""
        test_funcs = ["test_Process_Success", "test_save"]
        assert (
            _find_matching_test_function("process", test_funcs)
            == "test_Process_Success"
        )

    def test_no_match(self):
        """Test no match found."""
        test_funcs = ["test_save", "test_delete"]
        assert _find_matching_test_function("process", test_funcs) is None


class TestRecommendTestLevel:
    """Tests for _recommend_test_level function."""

    def test_recommend_test_level(self):
        """Verify it always returns UNIT."""
        assert _recommend_test_level() == TLevel.UNIT


class TestGenerateOverallRecommendation:
    """Tests for _generate_overall_recommendation function."""

    def test_no_test_file(self):
        """Test recommendation when no test file exists."""
        strategies: list[FunctionStrategy] = []
        result = _generate_overall_recommendation(strategies, False)
        assert "No test file found" in result

    def test_all_tested(self):
        """Test recommendation when all functions are tested."""
        strategies: list[FunctionStrategy] = [
            FunctionStrategy(
                function_name="f1",
                recommended_test_level=TLevel.UNIT,
                existing_test_function="test_f1",
                complexity=1,
            )
        ]
        result = _generate_overall_recommendation(strategies, True)
        assert "All 1 function(s) have corresponding tests" in result

    def test_missing_tests(self):
        """Test recommendation when some functions are missing tests."""
        strategies: list[FunctionStrategy] = [
            FunctionStrategy(
                function_name="f1",
                recommended_test_level=TLevel.UNIT,
                existing_test_function=None,
                complexity=1,
            )
        ]
        result = _generate_overall_recommendation(strategies, True)
        assert "1/1 function(s) are missing tests" in result

    def test_high_complexity(self):
        """Test recommendation with high complexity functions."""
        strategies: list[FunctionStrategy] = [
            FunctionStrategy(
                function_name="complex_func",
                recommended_test_level=TLevel.UNIT,
                existing_test_function="test_complex",
                complexity=15,
            )
        ]
        result = _generate_overall_recommendation(strategies, True)
        assert "high complexity" in result

    def test_good_coverage(self):
        """Test recommendation when coverage is good."""
        strategies: list[FunctionStrategy] = [
            FunctionStrategy(
                function_name="f1",
                recommended_test_level=TLevel.UNIT,
                existing_test_function="test_f1",
                complexity=1,
            )
        ]
        result = _generate_overall_recommendation(strategies, True)
        assert "All 1 function(s) have corresponding tests" in result


class TestAnalyzeModelBaseClass:
    """Tests for _analyze_model_base_class function."""

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_analyze_camel_case_model(self, mock_repo_factory):
        """Test detection of CamelCaseModel."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
class MyModel(CamelCaseModel):
    pass
"""
        import_path = "from pipe.core.models.session import MyModel"
        result = _analyze_model_base_class("MyModel", import_path)

        assert result is not None
        assert result.base_class == "CamelCaseModel"
        assert "snake_case" in result.serialization_notes

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_analyze_base_model(self, mock_repo_factory):
        """Test detection of BaseModel."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
class MyModel(BaseModel):
    pass
"""
        import_path = "from pipe.core.models.session import MyModel"
        result = _analyze_model_base_class("MyModel", import_path)

        assert result is not None
        assert result.base_class == "BaseModel"

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_analyze_attribute_base(self, mock_repo_factory):
        """Test detection of base class via attribute access."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
class MyModel(models.CamelCaseModel):
    pass
"""
        import_path = "from pipe.core.models.session import MyModel"
        result = _analyze_model_base_class("MyModel", import_path)

        assert result is not None
        assert result.base_class == "CamelCaseModel"

    def test_invalid_import_path(self):
        """Test with invalid import path."""
        assert _analyze_model_base_class("MyModel", "import MyModel") is None
        assert _analyze_model_base_class("MyModel", "from pipe.core import") is None

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_read_text_failure(self, mock_repo_factory):
        """Test when read_text fails."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.side_effect = [True, False]
        mock_repo.read_text.side_effect = Exception("Read error")

        import_path = "from pipe.core.models.session import MyModel"
        result = _analyze_model_base_class("MyModel", import_path)
        assert result is None

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_ast_parse_failure(self, mock_repo_factory):
        """Test when ast.parse fails."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = "invalid python code"

        import_path = "from pipe.core.models.session import MyModel"
        result = _analyze_model_base_class("MyModel", import_path)
        assert result is None


class TestExtractImportInfo:
    """Tests for _extract_import_info function."""

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_extract_imports(self, mock_namespace, mock_repo_factory):
        """Test extraction of various import types."""
        mock_namespace.return_value = "pipe.core.utils.path"
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
import os
from os.path import join as os_join
from typing import *
"""
        result = _extract_import_info("src/pipe/core/utils/path.py")

        assert "os" in result
        assert result["os"].patch_path == "pipe.core.utils.path.os"
        assert result["os"].import_type == "module"

        assert "os_join" in result
        assert result["os_join"].patch_path == "pipe.core.utils.path.os_join"
        assert result["os_join"].import_type == "from_import"

        # Wildcard import should be skipped
        assert "*" not in result

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_file_not_found(self, mock_repo_factory):
        """Test when file is not found."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = False
        assert _extract_import_info("non_existent.py") == {}

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_parse_error(self, mock_repo_factory):
        """Test when parsing fails."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = "invalid python"
        assert _extract_import_info("test.py") == {}


class TestFindTestFile:
    """Tests for _find_test_file function."""

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("os.walk")
    def test_find_test_file_success(self, mock_walk, mock_repo_factory):
        """Test successful test file discovery."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True

        mock_walk.return_value = [
            ("/project/tests/unit/core/tools", [], ["test_py_test_strategist.py"])
        ]

        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_path = MagicMock()
            mock_resolve.return_value = mock_path
            mock_path.stem = "py_test_strategist"

            project_root = MagicMock()
            (project_root / ".git").exists.return_value = True
            mock_path.parent = project_root

            result = _find_test_file("src/pipe/core/tools/py_test_strategist.py")
            assert result is not None
            assert "test_py_test_strategist.py" in result

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("os.walk")
    def test_find_test_file_no_git(self, mock_walk, mock_repo_factory):
        """Test test file discovery when .git is not found."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True

        mock_walk.return_value = [
            ("/project/src/pipe/core/tools/tests", [], ["test_py_test_strategist.py"])
        ]

        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_path = MagicMock()
            mock_resolve.return_value = mock_path
            mock_path.stem = "py_test_strategist"
            mock_path.parent.exists.return_value = True
            # Simulate .git not found by making exists() return False for all parents
            mock_path.parent.__truediv__.return_value.exists.return_value = False

            result = _find_test_file("src/pipe/core/tools/py_test_strategist.py")
            # Should fallback to target file's directory
            assert result is not None


class TestExtractTestFunctions:
    """Tests for _extract_test_functions function."""

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_extract_test_functions(self, mock_repo_factory):
        """Test extraction of test function names."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = """
def test_success(): pass
async def test_async_error(): pass
def other_func(): pass
"""
        result = _extract_test_functions("tests/test_file.py")
        assert "test_success" in result
        assert "test_async_error" in result
        assert "other_func" not in result

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_extract_failure(self, mock_repo_factory):
        """Test when extraction fails."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = "invalid python"
        assert _extract_test_functions("test.py") == []


class TestPyTestStrategist:
    """Tests for py_test_strategist main function."""

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_file_not_found(self, mock_repo_factory):
        """Test error when target file does not exist."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = False

        result = py_test_strategist("non_existent.py")
        assert isinstance(result, ToolResult)
        assert "File not found" in result.data.error

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    def test_not_python_file(self, mock_repo_factory):
        """Test error when target file is not a Python file."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True

        result = py_test_strategist("data.txt")
        assert "Not a Python file" in result.data.error

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    def test_static_analysis_failure(self, mock_analyzer, mock_repo_factory):
        """Test error when static analysis fails."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_analyzer.return_value = ToolResult(error="Analysis error")

        result = py_test_strategist("src/target.py")
        assert "Static analysis failed" in result.data.error

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._find_test_file")
    @patch("pipe.core.tools.py_test_strategist._extract_test_functions")
    @patch("pipe.core.tools.py_test_strategist._analyze_model_base_class")
    def test_py_test_strategist_success(
        self,
        mock_analyze_model,
        mock_extract_tests,
        mock_find_test,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test successful strategy generation."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {}
        mock_find_test.return_value = "tests/test_target.py"
        mock_extract_tests.return_value = ["test_process"]
        mock_analyze_model.return_value = SerializationHint(
            model_name="MyModel",
            base_class="BaseModel",
            default_naming_convention="snake_case",
            serialization_notes="Notes",
        )

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert result.data.target_file_path == "src/target.py"
        assert len(result.data.strategies) == 1
        assert result.data.strategies[0].function_name == "process"
        assert result.data.strategies[0].existing_test_function == "test_process"
        assert (
            "All 1 function(s) have corresponding tests"
            in result.data.overall_recommendation
        )

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_with_mocks(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation with mock targets."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="os.path.join", lineno=11, is_attribute_call=False
                            )
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {
            "os": MockTarget(
                dependency_name="os",
                patch_path="pipe.core.tools.py_test_strategist.os",
                import_type="module",
                original_import="import os",
            )
        }

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert "os.path.join" in result.data.additional_context.stdlib_usage
        assert len(result.data.strategies[0].mock_targets) == 0

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_with_custom_mocks(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation with custom mock targets."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="requests.get", lineno=11, is_attribute_call=False
                            )
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {
            "requests": MockTarget(
                dependency_name="requests",
                patch_path="pipe.core.tools.py_test_strategist.requests",
                import_type="module",
                original_import="import requests",
            )
        }

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert len(result.data.strategies[0].mock_targets) == 1
        assert (
            result.data.strategies[0].mock_targets[0].dependency_name == "requests.get"
        )
        assert (
            result.data.strategies[0].mock_targets[0].patch_path
            == "pipe.core.tools.py_test_strategist.requests.get"
        )

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_with_data_model_mock(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation when a data model is used in a call."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="Session.model_validate",
                                lineno=11,
                                is_attribute_call=False,
                            )
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {
            "Session": MockTarget(
                dependency_name="Session",
                patch_path="pipe.core.tools.py_test_strategist.Session",
                import_type="from_import",
                original_import="from pipe.core.models.session import Session",
            )
        }

        result = py_test_strategist("src/target.py")

        assert result.is_success
        # Session is a data model, so it should be in data_models and NOT in mock_targets
        assert "Session" in result.data.additional_context.data_models
        assert len(result.data.strategies[0].mock_targets) == 0

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_with_direct_import_mock(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation with direct import mock."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="requests", lineno=11, is_attribute_call=False
                            )
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {
            "requests": MockTarget(
                dependency_name="requests",
                patch_path="pipe.core.tools.py_test_strategist.requests",
                import_type="module",
                original_import="import requests",
            )
        }

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert len(result.data.strategies[0].mock_targets) == 1
        assert result.data.strategies[0].mock_targets[0].dependency_name == "requests"

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_fallback_mock(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation fallback for unknown dependencies."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="unknown_func", lineno=11, is_attribute_call=False
                            )
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {}

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert len(result.data.strategies[0].mock_targets) == 1
        assert (
            result.data.strategies[0].mock_targets[0].dependency_name == "unknown_func"
        )
        assert result.data.strategies[0].mock_targets[0].import_type == "unknown"

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_skip_instance_method(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation skipping instance methods (self.xxx)."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="self.internal_method",
                                lineno=11,
                                is_attribute_call=True,
                            )
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {}

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert len(result.data.strategies[0].mock_targets) == 0

    @patch("pipe.core.tools.py_test_strategist.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_test_strategist.py_condition_analyzer")
    @patch("pipe.core.tools.py_test_strategist._extract_import_info")
    @patch("pipe.core.tools.py_test_strategist._get_module_namespace")
    def test_py_test_strategist_complex_context(
        self,
        mock_namespace,
        mock_extract_imports,
        mock_analyzer,
        mock_repo_factory,
    ):
        """Test strategy generation with complex context (data models and stdlib)."""
        mock_repo = mock_repo_factory.return_value
        mock_repo.exists.return_value = True
        mock_namespace.return_value = "pipe.core.tools.py_test_strategist"

        mock_analyzer.return_value = ToolResult(
            data=AnalyzeConditionResult(
                file_path="src/target.py",
                functions=[
                    FunctionAnalysis(
                        name="process",
                        lineno=10,
                        end_lineno=20,
                        cyclomatic_complexity=5,
                        mock_candidates=[
                            MockCandidate(
                                name="os.path.join", lineno=11, is_attribute_call=False
                            ),
                            MockCandidate(
                                name="Session.model_validate",
                                lineno=12,
                                is_attribute_call=False,
                            ),
                        ],
                    )
                ],
            )
        )

        mock_extract_imports.return_value = {
            "os": MockTarget(
                dependency_name="os",
                patch_path="pipe.core.tools.py_test_strategist.os",
                import_type="module",
                original_import="import os",
            ),
            "Session": MockTarget(
                dependency_name="Session",
                patch_path="pipe.core.tools.py_test_strategist.Session",
                import_type="from_import",
                original_import="from pipe.core.models.session import Session",
            ),
        }

        result = py_test_strategist("src/target.py")

        assert result.is_success
        assert "os.path.join" in result.data.additional_context.stdlib_usage
        assert "Session" in result.data.additional_context.data_models
