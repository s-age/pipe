from pathlib import Path
import yaml

def read_yaml_file(file_path: Path) -> dict:
    """Reads a YAML file and returns its content as a dictionary."""
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
