import os

import google.genai as genai
from google.genai import types
import sys
import yaml

def call_gemini_api_with_grounding(settings: dict, instruction: str) -> types.GenerateContentResponse:
    model_name = settings.get('search_model')
    if not model_name:
        raise ValueError("'search_model' not found in setting.yml")

    api_contents = [
        {'role': 'user', 'parts': [{'text': instruction}]}
    ]

    all_tools = [types.Tool(google_search=types.GoogleSearch())]

    gen_config_params = {}
    if params := settings.get('parameters'):
        if temp := params.get('temperature'):
            gen_config_params['temperature'] = temp.get('value')
        if top_p := params.get('top_p'):
            gen_config_params['top_p'] = top_p.get('value')
        if top_k := params.get('top_k'):
            gen_config_params['top_k'] = top_k.get('value')

    config = types.GenerateContentConfig(
        tools=all_tools,
        temperature=gen_config_params.get('temperature'),
        top_p=gen_config_params.get('top_p'),
        top_k=gen_config_params.get('top_k')
    )

    client = genai.Client()

    try:
        response = client.models.generate_content(
            contents=api_contents,
            config=config,
            model=model_name
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_agent.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    with open(os.path.join(project_root, "setting.yml"), "r") as f:
        settings = yaml.safe_load(f)

    try:
        response = call_gemini_api_with_grounding(
            settings=settings,
            instruction=query
        )
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.text:
                    print(part.text)
        else:
            print("No response from model.")
    except Exception as e:
        print(f"Error: {e}")