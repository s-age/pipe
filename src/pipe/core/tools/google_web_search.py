from typing import Dict
import sys
import os
from pipe.core.search_agent import call_gemini_api_with_grounding
from pipe.core.models.settings import Settings

def google_web_search(query: str, settings: Settings, project_root: str = None) -> Dict[str, str]:
    """
    Performs a web search using Google Search and returns the results by executing a search agent.
    """
    if not query:
        return {"error": "google_web_search called without a query."}
    
    if not project_root:
        return {"error": "google_web_search requires project_root."}

    try:
        response = call_gemini_api_with_grounding(
            settings=settings,
            instruction=query,
            project_root=project_root
        )
        
        if response.candidates:
            content = "".join(part.text for part in response.candidates[0].content.parts if part.text)
            return {"content": content}
        else:
            return {"content": "No response from model."}

    except Exception as e:
        return {"error": f"Failed to execute search agent: {e}"}