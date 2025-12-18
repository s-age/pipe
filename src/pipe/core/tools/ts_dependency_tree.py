import json
import os
import subprocess

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root
from pydantic import BaseModel, Field


class DependencyNode(BaseModel):
    """A node in the dependency tree."""

    name: str
    source: str
    dependencies: "DependencyTreeResult | None" = None


class DependencyTreeResult(BaseModel):
    """Result from building a dependency tree."""

    file_path: str
    components: list[DependencyNode] = Field(default_factory=list)
    hooks: list[DependencyNode] = Field(default_factory=list)
    actions: list[DependencyNode] = Field(default_factory=list)
    types: list[dict[str, str]] = Field(default_factory=list)
    utils: list[DependencyNode] = Field(default_factory=list)
    circular: bool = False
    max_depth_reached: bool = False


def ts_dependency_tree(
    file_path: str, max_depth: int = 3
) -> ToolResult[DependencyTreeResult]:
    """
    Builds a dependency tree for a TypeScript file.

    Args:
        file_path: Path to a TypeScript file
        max_depth: Maximum depth to traverse (default: 3)

    Returns:
        ToolResult containing a tree of dependencies including:
        - Components used in JSX
        - Hooks called (use* pattern)
        - Actions/API calls
        - Type imports
        - Utility functions
    """
    if "node_modules" in os.path.normpath(file_path):
        return ToolResult(
            error=(
                "Operation on files within 'node_modules' is not allowed: "
                f"{file_path}"
            )
        )

    if not os.path.exists(file_path):
        return ToolResult(error=f"File not found: {file_path}")

    if not (file_path.endswith(".ts") or file_path.endswith(".tsx")):
        return ToolResult(error=f"Not a TypeScript file: {file_path}")

    file_path = os.path.abspath(file_path)

    try:
        # Construct the absolute path to the ts_analyzer.ts script
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cli", "ts_analyzer.ts"
        )
        script_path = os.path.abspath(script_path)

        # Calculate project_root internally
        project_root = get_project_root()

        command = [
            "npx",
            "ts-node",
            script_path,
            "dependency_tree",
            file_path,
            "",  # symbolName placeholder
            "",  # searchDirectory placeholder
            str(max_depth),
        ]

        process = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=project_root
        )

        output = json.loads(process.stdout)

        if "error" in output:
            return ToolResult(error=output["error"])

        # Parse the output into our model
        result = _parse_dependency_tree(output)
        return ToolResult(data=result)

    except subprocess.CalledProcessError as e:
        return ToolResult(error=f"ts_analyzer.ts failed: {e.stderr.strip()}")
    except json.JSONDecodeError:
        return ToolResult(
            error=(
                "Failed to parse JSON output from ts_analyzer.ts: "
                f"{process.stdout.strip()}"
            )
        )
    except Exception as e:
        return ToolResult(error=f"An unexpected error occurred: {e}")


def _parse_dependency_tree(data: dict) -> DependencyTreeResult:
    """Parse dependency tree data from JSON."""
    result = DependencyTreeResult(
        file_path=data["file_path"],
        circular=data.get("circular", False),
        max_depth_reached=data.get("max_depth_reached", False),
    )

    # Parse components
    for comp_data in data.get("components", []):
        dep_node = DependencyNode(
            name=comp_data["name"],
            source=comp_data["source"],
            dependencies=(
                _parse_dependency_tree(comp_data["dependencies"])
                if comp_data.get("dependencies")
                else None
            ),
        )
        result.components.append(dep_node)

    # Parse hooks
    for hook_data in data.get("hooks", []):
        dep_node = DependencyNode(
            name=hook_data["name"],
            source=hook_data["source"],
            dependencies=(
                _parse_dependency_tree(hook_data["dependencies"])
                if hook_data.get("dependencies")
                else None
            ),
        )
        result.hooks.append(dep_node)

    # Parse actions
    for action_data in data.get("actions", []):
        dep_node = DependencyNode(
            name=action_data["name"],
            source=action_data["source"],
            dependencies=(
                _parse_dependency_tree(action_data["dependencies"])
                if action_data.get("dependencies")
                else None
            ),
        )
        result.actions.append(dep_node)

    # Parse utils
    for util_data in data.get("utils", []):
        dep_node = DependencyNode(
            name=util_data["name"],
            source=util_data["source"],
            dependencies=(
                _parse_dependency_tree(util_data["dependencies"])
                if util_data.get("dependencies")
                else None
            ),
        )
        result.utils.append(dep_node)

    # Parse types (simple list, no recursion needed)
    result.types = data.get("types", [])

    return result


def format_dependency_tree(tree: DependencyTreeResult, indent: str = "") -> str:
    """Format the dependency tree as a readable string."""
    lines = [f"{tree.file_path}"]

    if tree.circular:
        lines.append(f"{indent}  [CIRCULAR DEPENDENCY DETECTED]")
        return "\n".join(lines)

    if tree.max_depth_reached:
        lines.append(f"{indent}  [Max depth reached]")

    if tree.components:
        lines.append(f"{indent}├─ Components")
        for i, comp in enumerate(tree.components):
            is_last = i == len(tree.components) - 1 and not (
                tree.hooks or tree.actions or tree.utils or tree.types
            )
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {comp.name} ({comp.source})")
            if comp.dependencies and not comp.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(comp.dependencies, child_indent)
                # Skip the first line (file path) in child tree
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.hooks:
        lines.append(f"{indent}├─ Hooks")
        for i, hook in enumerate(tree.hooks):
            is_last = i == len(tree.hooks) - 1 and not (
                tree.actions or tree.utils or tree.types
            )
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {hook.name} ({hook.source})")
            if hook.dependencies and not hook.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(hook.dependencies, child_indent)
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.actions:
        lines.append(f"{indent}├─ Actions")
        for i, action in enumerate(tree.actions):
            is_last = i == len(tree.actions) - 1 and not (tree.utils or tree.types)
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {action.name} ({action.source})")
            if action.dependencies and not action.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(
                    action.dependencies, child_indent
                )
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.utils:
        lines.append(f"{indent}├─ Utils")
        for i, util in enumerate(tree.utils):
            is_last = i == len(tree.utils) - 1 and not tree.types
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {util.name} ({util.source})")
            if util.dependencies and not util.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(util.dependencies, child_indent)
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.types:
        lines.append(f"{indent}└─ Types")
        for i, type_info in enumerate(tree.types):
            is_last = i == len(tree.types) - 1
            prefix = "└─" if is_last else "├─"
            lines.append(
                f"{indent}   {prefix} {type_info['name']} ({type_info['source']})"
            )

    return "\n".join(lines)
