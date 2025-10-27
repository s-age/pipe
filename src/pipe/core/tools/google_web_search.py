import os
import subprocess
import sys
from typing import Any


def google_web_search(query: str) -> dict[str, Any]:
    """
    Performs a web search using Google Search and returns the results by
    executing a search agent.
    """
    if not query:
        return {"error": "google_web_search called without a query."}

    try:
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        src_path = os.path.join(project_root, "src")
        agent_path = os.path.join(src_path, "pipe", "core", "agents", "search_agent.py")
        command = f'PYTHONPATH={src_path} pyenv exec python {agent_path} "{query}"'

        process = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )

        if process.stderr:
            print(f"Search agent stderr: {process.stderr}", file=sys.stderr)

        return {"content": process.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to execute search agent: {e.stderr.strip()}"}
    except Exception as e:
        return {"error": f"Failed to execute search agent: {e}"}
