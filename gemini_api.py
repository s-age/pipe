import google.generativeai as genai
import os
import sys
from pathlib import Path
import yaml
import argparse
from typing import Union, List

# Tooling imports from the project
from tools.list_directory import list_directory as list_directory_tool, ListDirectoryFileFilteringOptions
from tools.read_file import read_file as read_file_tool
from tools.search_file_content import search_file_content as search_file_content_tool
from tools.glob import glob as glob_tool
from tools.replace import replace as replace_tool
from tools.write_file import write_file as write_file_tool
from tools.web_fetch import web_fetch as web_fetch_tool
from tools.read_many_files import read_many_files as read_many_files_tool, ReadManyFilesFileFilteringOptions
from tools.run_shell_command import run_shell_command as run_shell_command_tool
from tools.save_memory import save_memory as save_memory_tool
from tools.google_web_search import google_web_search as google_web_search_tool

# Define tools as top-level functions
def list_directory(path: str) -> dict:
    """Lists the names of files and subdirectories directly within a specified directory path."""
    return list_directory_tool(path, file_filtering_options=None, ignore=None)

def read_file(absolute_path: str, limit: Union[float, None] = None, offset: Union[float, None] = None) -> dict:
    """Reads and returns the content of a specified file."""
    return read_file_tool(absolute_path, limit, offset)

def search_file_content(pattern: str, include: Union[str, None] = None, path: Union[str, None] = None) -> dict:
    """Searches for a regular expression pattern within the content of files in a specified directory (or current working directory)."""
    return search_file_content_tool(pattern, include, path)

def glob(pattern: str, case_sensitive: Union[bool, None] = None, path: Union[str, None] = None, respect_gemini_ignore: Union[bool, None] = None, respect_git_ignore: Union[bool, None] = None) -> dict:
    """Efficiently finds files matching specific glob patterns."""
    return glob_tool(pattern, case_sensitive, path, respect_gemini_ignore, respect_git_ignore)

def replace(file_path: str, instruction: str, old_string: str, new_string: str) -> dict:
    """Replaces text within a file."""
    return replace_tool(file_path, instruction, old_string, new_string)

def write_file(file_path: str, content: str) -> dict:
    """Writes content to a specified file in the local filesystem."""
    return write_file_tool(file_path, content)

def web_fetch(prompt: str) -> dict:
    """Processes content from URL(s) embedded in a prompt."""
    return web_fetch_tool(prompt)

def read_many_files(paths: list[str], exclude: Union[List[str], None] = [], file_filtering_options: Union[ReadManyFilesFileFilteringOptions, None] = None, include: Union[List[str], None] = [], recursive: Union[bool, None] = True, useDefaultExcludes: Union[bool, None] = True) -> dict:
    """Reads content from multiple files."""
    return read_many_files_tool(paths, exclude, file_filtering_options, include, recursive, useDefaultExcludes)

def run_shell_command(command: str, description: Union[str, None] = None, directory: Union[str, None] = None) -> dict:
    """Executes a given shell command."""
    return run_shell_command_tool(command, description, directory)

def save_memory(fact: str) -> dict:
    """Saves a specific piece of information or fact to your long-term memory."""
    return save_memory_tool(fact)

def google_web_search(query: str) -> dict:
    """Performs a web search using Google Search and returns the results."""
    return google_web_search_tool(query)


def call_gemini_api(contents: list, model_name: str, tools_json: list, settings: dict) -> str:
    """
    Calls the Gemini API using the automatic tool calling feature with top-level functions.
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        available_tools = [
            web_fetch, run_shell_command, save_memory, google_web_search
        ]

        # Extract hyperparameters from settings and build generation_config
        generation_config = {}
        if "parameters" in settings:
            for key, value_desc_pair in settings["parameters"].items():
                if "value" in value_desc_pair:
                    # Directly assign the value. The API will handle type validation.
                    # Convert camelCase to snake_case for API compatibility
                    snake_case_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
                    generation_config[snake_case_key] = value_desc_pair["value"]

        model = genai.GenerativeModel(model_name=model_name, tools=available_tools, generation_config=generation_config)
        
        history = contents[:-1]
        current_prompt = contents[-1]['parts'][0]['text']

        chat = model.start_chat(history=history, enable_automatic_function_calling=True)


        response = chat.send_message(current_prompt)

        while response.candidates[0].content.parts[0].function_call:
            part = response.candidates[0].content.parts[0]
            function_call = part.function_call
            function_name = function_call.name
            function_args = {key: value for key, value in function_call.args.items()}



            try:
                tool_function = getattr(tool_executor, function_name)
                tool_output = tool_function(**function_args)

                last_tool_output = tool_output # Store the last tool output
            except Exception as e:
                error_message = f"Error executing tool '{function_name}': {e}"
                print(error_message, file=sys.stderr)
                tool_output = {"error": error_message}
                last_tool_output = tool_output # Store error output as well

            # Send the tool response back to the model.

            response = chat.send_message(
                # Note: In older versions, the tool response is sent as a Part-like dict.
                {
                    "function_response": {
                        "name": function_name,
                        "response": tool_output,
                    }
                }
            )

        final_response_text = response.text
        if not final_response_text and 'run_shell_command_response' in last_tool_output and 'output' in last_tool_output['run_shell_command_response']:
            return last_tool_output['run_shell_command_response']['output']
        return final_response_text

    except Exception as e:

        import traceback
        traceback.print_exc()
        return f"Error: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call Gemini API with a given instruction.")
    parser.add_argument("--instruction", type=str, help="The instruction to send to the Gemini API.")
    args = parser.parse_args()

    setting_file_path = os.path.join(os.path.dirname(__file__), "setting.yml")
    model_from_setting = "gemini-pro"
    try:
        with open(setting_file_path, 'r') as f:
            settings = yaml.safe_load(f)
            model_from_setting = settings.get("model", "gemini-pro")
    except FileNotFoundError:
        pass
    except yaml.YAMLError as e:
        pass

    initial_content = [{'role': 'user', 'parts': [{'text': args.instruction}]}]
    final_response = call_gemini_api(contents=initial_content, model_name=model_from_setting)
    

