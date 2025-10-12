from typing import Dict, Any
from pathlib import Path
import subprocess
import sys

def google_web_search(query: str) -> Dict[str, Any]:
    """
    Performs a web search using Google Search and returns the results by executing a search agent.
    """
    if not query:
        return {"error": "google_web_search called without a query."}
    
    try:
        # pyenv exec python src/search_agent.py "$query" を実行
        # tools/google_web_search.pyから見たプロジェクトルートはPath(__file__).parent.parent
        command = f"pyenv exec python {Path(__file__).parent.parent / 'src' / 'search_agent.py'} \"{query}\""
        print(f"Executing search agent: {command}")
        
        # サブプロセスを実行し、出力をキャプチャ
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        
        if process.stderr:
            print(f"Search agent stderr: {process.stderr}", file=sys.stderr)
        
        return {"content": process.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to execute search agent: {e.stderr.strip()}"}
    except Exception as e:
        return {"error": f"Failed to execute search agent: {e}"}
