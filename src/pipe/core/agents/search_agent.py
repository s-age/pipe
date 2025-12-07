import os
import sys
import warnings

import google.genai as genai
from google.genai import types
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_yaml_file

# Suppress specific UserWarning from pydantic
warnings.filterwarnings(
    "ignore", message='Field name ".*" shadows an attribute in parent "Operation";'
)


def call_gemini_api_with_grounding(
    settings: Settings, instruction: str, project_root: str
) -> types.GenerateContentResponse:
    model_name = settings.search_model
    if not model_name:
        raise ValueError("'search_model' not found in setting.yml")

    api_contents = [{"role": "user", "parts": [{"text": instruction}]}]

    all_tools: list[types.Tool] = [types.Tool(google_search=types.GoogleSearch())]

    gen_config_params = {
        "temperature": settings.parameters.temperature.value,
        "top_p": settings.parameters.top_p.value,
        "top_k": settings.parameters.top_k.value,
    }

    config = types.GenerateContentConfig(
        tools=all_tools,  # type: ignore[arg-type]
        temperature=gen_config_params.get("temperature"),
        top_p=gen_config_params.get("top_p"),
        top_k=gen_config_params.get("top_k"),
    )

    client = genai.Client()

    try:
        response = client.models.generate_content(
            contents=api_contents, config=config, model=model_name
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_agent.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )

    settings_dict = read_yaml_file(os.path.join(project_root, "setting.yml"))
    settings = Settings(**settings_dict)

    try:
        response = call_gemini_api_with_grounding(
            settings=settings, instruction=query, project_root=project_root
        )
        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.text:
                    print(part.text)
        else:
            print("No response from model.")
    except Exception as e:
        print(f"Error: {e}")
