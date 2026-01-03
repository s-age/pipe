#!/usr/bin/env python3
"""
sessions/*/*.json から統計情報を抽出するスクリプト
"""

import json
from pathlib import Path
from typing import Any


def extract_target_file(purpose: str) -> str:
    """purposeから 'Generate tests for' を除去"""
    if purpose.startswith("Generate tests for "):
        return purpose.replace("Generate tests for ", "", 1)
    return purpose


def count_user_turns(turns: list[dict[str, Any]]) -> int:
    """user_task タイプのターン数をカウント"""
    return sum(1 for turn in turns if turn.get("type") == "user_task")


def count_tool_calls(turns: list[dict[str, Any]]) -> int:
    """function_calling タイプのターン数をカウント"""
    return sum(1 for turn in turns if turn.get("type") == "function_calling")


def extract_tool_history(turns: list[dict[str, Any]]) -> list[str]:
    """function_calling タイプのresponseを抽出"""
    return [
        turn.get("response", "")
        for turn in turns
        if turn.get("type") == "function_calling" and turn.get("response")
    ]


def extract_reference_paths(references: list[dict[str, Any]]) -> list[str]:
    """referencesからpathのリストを抽出"""
    return [ref.get("path", "") for ref in references if ref.get("path")]


def process_session_file(file_path: Path) -> dict[str, Any]:
    """単一のセッションファイルを処理"""
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    return {
        "session_id": data.get("session_id", ""),
        "target_file": extract_target_file(data.get("purpose", "")),
        "token_count": data.get("token_count", 0),
        "cached_content_token_count": data.get("cached_content_token_count", 0),
        "cumulative_total_tokens": data.get("cumulative_total_tokens", 0),
        "cumulative_cached_tokens": data.get("cumulative_cached_tokens", 0),
        "references": extract_reference_paths(data.get("references", [])),
        "user_turn_count": count_user_turns(data.get("turns", [])),
        "tool_call_count": count_tool_calls(data.get("turns", [])),
        "tool_history": extract_tool_history(data.get("turns", [])),
    }


def main():
    """メイン処理"""
    # sessionsディレクトリ配下の全JSONファイルを検索
    sessions_dir = Path("sessions")

    if not sessions_dir.exists():
        print(
            json.dumps(
                {"error": "sessions directory not found"}, indent=2, ensure_ascii=False
            )
        )
        return

    # sessions/*/*.json のみを収集
    json_files = list(sessions_dir.glob("*/*.json"))

    # 各ファイルを処理
    results = []
    for json_file in sorted(json_files):
        try:
            result = process_session_file(json_file)
            results.append(result)
        except Exception as e:
            # エラーが発生したファイルはスキップして続行
            print(
                f"Warning: Failed to process {json_file}: {e}",
                file=__import__("sys").stderr,
            )
            continue

    # JSON配列として出力
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
