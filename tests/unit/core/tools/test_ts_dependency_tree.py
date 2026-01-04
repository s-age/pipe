import json
import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.tools.ts_dependency_tree import (
    DependencyNode,
    DependencyTreeResult,
    _parse_dependency_tree,
    format_dependency_tree,
    ts_dependency_tree,
)


class TestTsDependencyTree:
    """Tests for ts_dependency_tree function."""

    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_node_modules_prohibited(self, mock_normpath):
        """Test that operation on node_modules is prohibited."""
        mock_normpath.return_value = "/path/to/node_modules/file.ts"
        result = ts_dependency_tree("node_modules/file.ts")
        assert not result.is_success
        assert "node_modules" in result.error

    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_file_not_found(self, mock_normpath, mock_exists):
        """Test that error is returned if file is not found."""
        mock_normpath.return_value = "/path/to/missing.ts"
        mock_exists.return_value = False
        result = ts_dependency_tree("missing.ts")
        assert not result.is_success
        assert "File not found" in result.error

    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_invalid_extension(self, mock_normpath, mock_exists):
        """Test that error is returned for non-TypeScript files."""
        mock_normpath.return_value = "/path/to/file.txt"
        mock_exists.return_value = True
        result = ts_dependency_tree("file.txt")
        assert not result.is_success
        assert "Not a TypeScript file" in result.error

    @patch("pipe.core.tools.ts_dependency_tree.subprocess.run")
    @patch("pipe.core.tools.ts_dependency_tree.get_project_root")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.abspath")
    def test_successful_execution(
        self, mock_abspath, mock_normpath, mock_exists, mock_root, mock_run
    ):
        """Test successful execution of ts_dependency_tree."""
        mock_normpath.return_value = "/path/to/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/path/to/file.ts"
        mock_root.return_value = "/project/root"

        mock_output = {
            "file_path": "/path/to/file.ts",
            "components": [{"name": "Comp", "source": "./Comp"}],
            "hooks": [],
            "actions": [],
            "utils": [],
            "types": [],
            "circular": False,
            "max_depth_reached": False,
        }

        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_process

        result = ts_dependency_tree("file.ts")

        assert result.is_success
        assert result.data is not None
        assert result.data.file_path == "/path/to/file.ts"
        assert len(result.data.components) == 1
        assert result.data.components[0].name == "Comp"

    @patch("pipe.core.tools.ts_dependency_tree.subprocess.run")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_subprocess_error(self, mock_normpath, mock_exists, mock_run):
        """Test handling of subprocess error."""
        mock_normpath.return_value = "/path/to/file.ts"
        mock_exists.return_value = True

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="npx ...", stderr="Some error"
        )

        result = ts_dependency_tree("file.ts")
        assert not result.is_success
        assert "ts_analyzer.ts failed: Some error" in result.error

    @patch("pipe.core.tools.ts_dependency_tree.subprocess.run")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_json_decode_error(self, mock_normpath, mock_exists, mock_run):
        """Test handling of JSON decode error."""
        mock_normpath.return_value = "/path/to/file.ts"
        mock_exists.return_value = True

        mock_process = MagicMock()
        mock_process.stdout = "Invalid JSON"
        mock_run.return_value = mock_process

        result = ts_dependency_tree("file.ts")
        assert not result.is_success
        assert "Failed to parse JSON output" in result.error

    @patch("pipe.core.tools.ts_dependency_tree.subprocess.run")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_analyzer_error_in_output(self, mock_normpath, mock_exists, mock_run):
        """Test handling of error message within JSON output."""
        mock_normpath.return_value = "/path/to/file.ts"
        mock_exists.return_value = True

        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"error": "Analyzer error"})
        mock_run.return_value = mock_process

        result = ts_dependency_tree("file.ts")
        assert not result.is_success
        assert result.error == "Analyzer error"

    @patch("pipe.core.tools.ts_dependency_tree.subprocess.run")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.exists")
    @patch("pipe.core.tools.ts_dependency_tree.os.path.normpath")
    def test_unexpected_error(self, mock_normpath, mock_exists, mock_run):
        """Test handling of unexpected error."""
        mock_normpath.return_value = "/path/to/file.ts"
        mock_exists.return_value = True
        mock_run.side_effect = Exception("Unexpected")

        result = ts_dependency_tree("file.ts")
        assert not result.is_success
        assert "An unexpected error occurred: Unexpected" in result.error


class TestParseDependencyTree:
    """Tests for _parse_dependency_tree function."""

    def test_parse_complex_tree(self):
        """Test parsing a complex dependency tree with recursion."""
        data = {
            "file_path": "root.ts",
            "components": [
                {
                    "name": "App",
                    "source": "./App",
                    "dependencies": {
                        "file_path": "App.ts",
                        "hooks": [{"name": "useAuth", "source": "./useAuth"}],
                    },
                }
            ],
            "hooks": [{"name": "useGlobal", "source": "./useGlobal"}],
            "actions": [{"name": "fetchData", "source": "./api"}],
            "utils": [{"name": "formatDate", "source": "./utils"}],
            "types": [{"name": "User", "source": "./types"}],
            "circular": False,
            "max_depth_reached": True,
        }

        result = _parse_dependency_tree(data)

        assert result.file_path == "root.ts"
        assert result.max_depth_reached is True
        assert len(result.components) == 1
        assert result.components[0].name == "App"
        assert result.components[0].dependencies is not None
        assert result.components[0].dependencies.hooks[0].name == "useAuth"
        assert result.hooks[0].name == "useGlobal"
        assert result.actions[0].name == "fetchData"
        assert result.utils[0].name == "formatDate"
        assert result.types[0]["name"] == "User"


class TestFormatDependencyTree:
    """Tests for format_dependency_tree function."""

    def test_format_basic(self):
        """Test basic formatting of dependency tree."""
        tree = DependencyTreeResult(
            file_path="src/App.tsx",
            components=[
                DependencyNode(name="Header", source="./Header"),
                DependencyNode(name="Footer", source="./Footer"),
            ],
            types=[{"name": "Config", "source": "./types"}],
        )

        output = format_dependency_tree(tree)
        assert "src/App.tsx" in output
        assert "├─ Components" in output
        assert "│  ├─ Header (./Header)" in output
        assert "│  ├─ Footer (./Footer)" in output
        assert "└─ Types" in output
        assert "   └─ Config (./types)" in output

    def test_format_circular(self):
        """Test formatting with circular dependency."""
        tree = DependencyTreeResult(file_path="src/A.ts", circular=True)
        output = format_dependency_tree(tree)
        assert "[CIRCULAR DEPENDENCY DETECTED]" in output

    def test_format_max_depth(self):
        """Test formatting when max depth is reached."""
        tree = DependencyTreeResult(file_path="src/A.ts", max_depth_reached=True)
        output = format_dependency_tree(tree)
        assert "[Max depth reached]" in output

    def test_format_complex_nested(self):
        """Test formatting of complex nested dependencies."""
        # Child tree for a hook
        hook_child = DependencyTreeResult(
            file_path="src/useAuth.ts",
            actions=[DependencyNode(name="login", source="./api")],
        )

        # Child tree for an action
        action_child = DependencyTreeResult(
            file_path="src/api.ts",
            utils=[DependencyNode(name="request", source="./utils")],
        )

        # Main tree
        tree = DependencyTreeResult(
            file_path="src/App.tsx",
            components=[
                DependencyNode(
                    name="Main",
                    source="./Main",
                    dependencies=DependencyTreeResult(
                        file_path="src/Main.tsx",
                        utils=[DependencyNode(name="helper", source="./utils")],
                    ),
                )
            ],
            hooks=[
                DependencyNode(
                    name="useAuth", source="./useAuth", dependencies=hook_child
                )
            ],
            actions=[
                DependencyNode(
                    name="fetchData", source="./api", dependencies=action_child
                )
            ],
            utils=[
                DependencyNode(
                    name="logger",
                    source="./logger",
                    dependencies=DependencyTreeResult(
                        file_path="src/logger.ts",
                        types=[{"name": "LogType", "source": "./types"}],
                    ),
                )
            ],
            types=[{"name": "User", "source": "./types"}],
        )

        output = format_dependency_tree(tree)
        assert "src/App.tsx" in output
        assert "├─ Components" in output
        assert "│  ├─ Main (./Main)" in output
        assert "│  ├─ Utils" in output
        assert "│  │  └─ helper (./utils)" in output
        assert "├─ Hooks" in output
        assert "│  ├─ useAuth (./useAuth)" in output
        assert "│  ├─ Actions" in output
        assert "│  │  └─ login (./api)" in output
        assert "├─ Actions" in output
        assert "│  ├─ fetchData (./api)" in output
        assert "│  ├─ Utils" in output
        assert "│  │  └─ request (./utils)" in output
        assert "├─ Utils" in output
        assert "│  ├─ logger (./logger)" in output
        assert "│  └─ Types" in output
        assert "│     └─ LogType (./types)" in output
        assert "└─ Types" in output
        assert "   └─ User (./types)" in output

    def test_format_multiple_types(self):
        """Test formatting with multiple types to cover all branches."""
        tree = DependencyTreeResult(
            file_path="types.ts",
            types=[
                {"name": "TypeA", "source": "./sourceA"},
                {"name": "TypeB", "source": "./sourceB"},
            ],
        )
        output = format_dependency_tree(tree)
        assert "   ├─ TypeA (./sourceA)" in output
        assert "   └─ TypeB (./sourceB)" in output
