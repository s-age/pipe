import google.genai as genai
import os
import sys
import json

# --- 1. JSONデータをPythonの辞書として定義 ---
PROMPT_DATA = {
  "description": "JSON object representing the entire request to the AI sub-agent. The agent's goal is to accomplish the 'current_task' based on all provided context.",
  "main_instruction": "When you receive JSON data, process your thoughts according to the following flowchart:\n\n```mermaid\ngraph TD\n    A[\"Start: JSON Input\"] --> B[\"Step 1: Read 'current_task.instruction' to identify task objective\"];\n    B --> C[\"Step 2: Extract relevant information from the latest turns in 'conversation_history.turns'\"];\n    C --> D[\"Step 3: Integrate extracted task instructions and historical information, then summarize the current context\"];\n    D --> E[\"Step 4: Based on the summarized information, think and plan for response generation\"];\n    E --> F[\"Step 5: Generate final response based on the plan\"];\n    F --> G[\"End: Output Response\"];\n```",
  "hyperparameters": {
    "description": "Contextual instructions to control the AI model's generation process. The model should strive to follow these instructions.",
    "temperature": { "type": "number", "value": 0.2, "description": "Be precise and factual. A lower value is preferred for deterministic output." },
    "top_p": { "type": "number", "value": 0.5, "description": "Consider a broad range of possibilities, but adhere strictly to the temperature setting." },
    "top_k": { "type": "number", "value": 5, "description": "Limit the generation to the top 5 most likely tokens at each step." }
  },
  "session_goal": {
    "description": "The immutable purpose and background for this entire conversation session.",
    "purpose": "Implementation of src/components/atoms/Button",
    "background": "Component preparation for starting a React project"
  },
  "response_constraints": {
    "description": "Constraints that the AI sub-agent should adhere to when generating responses. The entire response, including all content, must be generated in the specified language.",
    "language": "Japanese"
  },
  "roles": {
    "description": "A list of personas or role definitions that the AI sub-agent should conform to.",
    "definitions": [
      "# Role: Software Engineer\n\nYou are a professional software engineer. Your primary goal is to write clean, efficient, and maintainable code based on the provided instructions and context. Adhere to best practices and coding standards relevant to the specified language.\n"
    ]
  },
  "conversation_history": {
    "description": "Historical record of past interactions in this session, in chronological order.",
    "turns": [
      { "type": "user_task", "instruction": "fooは2", "timestamp": "2025-10-13T15:26:01.243472+09:00" },
      { "type": "model_response", "content": "fooは2ですね。承知いたしました。", "timestamp": "2025-10-13T15:26:01.243941+09:00" }
    ]
  },
  "current_task": {
    "description": "The specific task that the AI sub-agent must currently execute.",
    "instruction": "ロールは何だ？"
  },
  "reasoning_process": "```mermaid\ngraph TD\n    A([\"Start: JSON Input\"]) --> B[\"Step 1: Read 'current_task.instruction' to identify task objective\"];\n    B --> C[\"Step 2: Derive general principles behind the task (Step-Back)\"];\n    C --> D[\"Step 3: Extract relevant information from the latest turns in 'conversation_history.turns'\"];\n    D --> E[\"Step 4: Integrate extracted task instructions, principles, and historical information, then summarize the current context\"];\n    E --> F[\"Step 5: Based on the summarized information, think and plan for response generation\"];\n    F --> G{\"Decision: Are there any contradictions or leaps in logic?\"];\n    G -- NO --> E;\n    G -- YES --> H[\"Step 6: Re-examine the reasoning path from multiple perspectives and confirm the robustness of the conclusion (Self-Consistency)\"];\n    H --> I[\"Step 7: Generate the final response based on the plan\"];\n    I --> J{\"Decision: Does it meet the initial requirements (format/purpose)?\"];\n    J -- NO --> F;\n    J -- YES --> K([\"End: Output Response\"]);\n```"
}
# ----------------------------------------------------------------------

def main():
    if 'GOOGLE_API_KEY' not in os.environ:
        print("エラー: GOOGLE_API_KEY環境変数が設定されていません。")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("エラー: 指示をコマンドライン引数として渡してください。")
        print("例: python genai_example.py \"fooとは何ですか？\"")
        sys.exit(1)

    instruction = sys.argv[1]

    # current_task.instructionを更新
    PROMPT_DATA["current_task"]["instruction"] = instruction
    
    # 辞書をJSON文字列に変換
    final_json_prompt = json.dumps(PROMPT_DATA, ensure_ascii=False, indent=2)

    try:
        # クライアントを初期化
        client = genai.Client()

        # テキストを生成
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=final_json_prompt
        )

        # 応答を出力
        print("--- 応答 ---")
        print(response.text)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()