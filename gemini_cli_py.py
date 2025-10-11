import subprocess
import sys

def call_gemini_cli(prompt: str, model_name: str, yolo: bool) -> str:
    command = ['gemini', '-m', model_name, '-p', prompt]
    if yolo:
        command.insert(1, '-y')
    try:
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        model_response_text = process.stdout
        if process.stderr:
            print(f"Warning from gemini-cli: {process.stderr}", file=sys.stderr)
        return model_response_text
    except FileNotFoundError:
        return "Error: 'gemini' command not found. Make sure it's in your PATH."
    except subprocess.CalledProcessError as e:
        return f"Error during gemini-cli execution: {e.stderr}"
