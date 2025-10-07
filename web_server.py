import os
import json
from flask import Flask, jsonify, render_template

app = Flask(__name__)
HISTORY_DIR = 'sessions'

# Ensure the history directory exists for file operations
os.makedirs(HISTORY_DIR, exist_ok=True)

@app.route('/')
def index():
    """
    Serves the main HTML page for viewing conversation history.
    """
    return render_template('index.html')

@app.route('/api/history')
def get_history():
    """
    Reads all JSON files from the 'history/' directory, aggregates their content,
    and returns it as a single JSON array.
    """
    all_history_data = []
    
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(HISTORY_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_history_data.extend(data)
                    else:
                        all_history_data.append(data)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {filepath}. Skipping.")
            except Exception as e:
                print(f"Error reading {filepath}: {e}. Skipping.")
                
    # Sort history by timestamp if available, for better readability
    all_history_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return jsonify(all_history_data)

if __name__ == '__main__':
    # For demonstration, create some dummy history files if they don't exist
    dummy_history_files = [
        {
            "filename": "chat_1.json",
            "content": {
                "timestamp": "2023-10-26T10:00:00Z",
                "type": "user_message",
                "role": "user",
                "content": "Hello, how are you today?"
            }
        },
        {
            "filename": "chat_2.json",
            "content": {
                "timestamp": "2023-10-26T10:01:30Z",
                "type": "agent_response",
                "role": "assistant",
                "content": "I'm doing well, thank you for asking! How can I assist you?"
            }
        },
        {
            "filename": "task_1.json",
            "content": {
                "timestamp": "2023-10-26T10:05:15Z",
                "type": "user_task",
                "purpose": "Summarize document",
                "background": "The document discusses the history of AI.",
                "instruction": "Provide a 3-sentence summary of the provided background.",
                "roles": ["analyst"]
            }
        },
        {
            "filename": "agent_output_1.json",
            "content": {
                "timestamp": "2023-10-26T10:06:40Z",
                "type": "agent_output",
                "role": "analyst",
                "content": "AI's history began with ancient philosophical inquiries into intelligence. Modern AI started in the mid-20th century with the Dartmouth workshop. Since then, it has seen periods of rapid advancement and 'AI winters', leading to today's sophisticated models."
            }
        }
    ]

    for item in dummy_history_files:
        filepath = os.path.join(HISTORY_DIR, item["filename"])
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(item["content"], f, indent=4)
            print(f"Created dummy file: {filepath}")

    app.run(debug=True)
