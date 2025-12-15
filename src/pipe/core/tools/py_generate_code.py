"""
Tool for generating new Python code snippets.
Proposes and generates new functions, classes, or code snippets
based on existing codebase and requirements.
"""

import ast
import os

from jinja2 import Environment, FileSystemLoader
from pipe.core.models.results.py_generate_code_result import PyGenerateCodeResult


def _parse_code_for_patterns(file_paths: list[str]) -> dict:
    """
    Parses Python code files for structural patterns using AST.
    """
    extracted_patterns: dict[str, list[str]] = {
        "classes": [],
        "functions": [],
        "imports": [],
    }
    extracted_patterns["type_hints"] = {}  # type: ignore

    for file_path in file_paths:
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    extracted_patterns["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    extracted_patterns["functions"].append(node.name)
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    # Basic import extraction
                    for alias in node.names:
                        extracted_patterns["imports"].append(alias.name)
                # More sophisticated type hint extraction can be added here later

        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            continue
    return extracted_patterns


def py_generate_code(
    instruction: str,
    name: str,
    layer: str,
    component_type: str | None = None,
    description: str | None = None,
    dependencies: list[str] | None = None,
    methods: list[dict] | None = None,
    context_file_paths: list[str] | None = None,
) -> PyGenerateCodeResult:
    """
    Generates a new Python code snippet based on the provided instruction and context.
    """
    template_dir = os.path.join(
        os.path.dirname(__file__), "../../../../templates/python_code_gen"
    )
    env = Environment(loader=FileSystemLoader(template_dir))

    # Determine which template to use based on layer and component_type
    template_name = "generic_template.j2"  # Default template
    if layer == "models" and component_type == "class":
        template_name = "models/pydantic_model.j2"
    elif layer == "services" and component_type == "class":
        template_name = "services/service_class.j2"
    elif layer == "agents" and component_type == "class":
        template_name = "agents/agent_class.j2"
    elif layer == "delegates" and component_type == "function":
        template_name = "delegates/delegate_function.j2"
    elif layer == "domains" and component_type == "function":
        template_name = "domains/domain_functions.j2"
    elif layer == "repositories" and component_type == "class":
        template_name = "repositories/repository_class.j2"
    elif layer == "collections" and component_type == "class":
        template_name = "collections/collection_class.j2"
    elif layer == "utils" and component_type == "function":
        template_name = "utils/utility_functions.j2"
    elif layer == "validators" and component_type == "function":
        template_name = "validators/validator_function.j2"

    try:
        template = env.get_template(template_name)
    except Exception as e:
        return PyGenerateCodeResult(error=f"Template loading error: {e}")

    # Extract patterns from context files if provided
    extracted_patterns = {}
    if context_file_paths:
        extracted_patterns = _parse_code_for_patterns(context_file_paths)

    # Prepare context for the template
    template_context = {
        "instruction": instruction,
        "name": name,
        "layer": layer,
        "component_type": component_type,
        "description": description,
        "dependencies": dependencies,
        "methods": methods,
        "context_file_paths": context_file_paths,
        "extracted_patterns": extracted_patterns,  # Add extracted patterns to context
    }

    generated_code = template.render(template_context)

    return PyGenerateCodeResult(generated_code=generated_code)
