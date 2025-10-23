import json
import importlib
import inspect

from src.gemini_api import call_gemini_api
from src.utils.datetime import get_current_timestamp

# This function is a dependency for run()
def execute_tool_call(tool_call, session_manager, session_id, settings, project_root):
    """Dynamically imports and executes a tool function, passing context if needed."""
    tool_name = tool_call.name
    tool_args = dict(tool_call.args)
    
    print(f"Tool call: {tool_name}({tool_args})")

    try:
        tool_module = importlib.import_module(f"tools.{tool_name}")
        importlib.reload(tool_module)
        tool_function = getattr(tool_module, tool_name)
        
        sig = inspect.signature(tool_function)
        params = sig.parameters
        
        final_args = tool_args.copy()
        
        if 'session_manager' in params:
            final_args['session_manager'] = session_manager
        if 'session_id' in params and 'session_id' not in tool_args:
            final_args['session_id'] = session_id
        if 'settings' in params:
            final_args['settings'] = settings
        if 'project_root' in params:
            final_args['project_root'] = project_root

        result = tool_function(**final_args)
        return result
    except Exception as e:
        return {"error": f"Failed to execute tool {tool_name}: {e}"}


def run(args, settings, session_data_for_prompt, project_root, api_mode, local_tz, enable_multi_step_reasoning, session_manager, session_id):
    """The delegate function for running in gemini-api mode."""
    model_response_text = ""
    token_count = 0
    while True:
        stream = call_gemini_api(
            settings=settings,
            session_data=session_data_for_prompt,
            project_root=project_root,
            instruction=args.instruction,
            api_mode=api_mode,
            multi_step_reasoning_enabled=enable_multi_step_reasoning
        )

        response_chunks = []
        print("--- Response Received ---")
        for chunk in stream:
            if chunk.text:
                print(chunk.text, end='', flush=True)
            response_chunks.append(chunk)
        print("\n-------------------------\n")

        if not response_chunks:
            # ストリームが空だった場合のエラーハンドリング
            model_response_text = "API Error: Model stream was empty."
            break

        # チャンクから完全なレスポンスを再構築
        final_response = response_chunks[-1]
        full_text = "".join(chunk.text for chunk in response_chunks if chunk.text)
        if final_response.candidates:
            if final_response.candidates[0].content and final_response.candidates[0].content.parts:
                final_response.candidates[0].content.parts[0].text = full_text
            else:
                final_response.candidates[0].content = type(final_response.candidates[0].content)(parts=[type(final_response.candidates[0].content.parts[0])(text=full_text)])
        else:
            final_response.candidates.append(type(final_response.candidates[0])(content=type(final_response.candidates[0].content)(parts=[type(final_response.candidates[0].content.parts[0])(text=full_text)])))
        
        response = final_response # 後続処理のために変数名を合わせる

        token_count = response.usage_metadata.prompt_token_count + response.usage_metadata.candidates_token_count

        function_call = None
        try:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    break
        except (IndexError, AttributeError):
            function_call = None

        if not function_call:
            model_response_text = response.text
            break

        args_json_string = json.dumps(dict(function_call.args), ensure_ascii=False)
        response_string = f"{function_call.name}({args_json_string})"

        model_turn = {
            "type": "function_calling",
            "response": response_string,
            "timestamp": get_current_timestamp(local_tz)
        }
        session_manager.add_turn_to_session(session_id, model_turn)
        reloaded_session_data = session_manager.history_manager.get_session(session_id)
        if reloaded_session_data:
            session_data_for_prompt['turns'] = reloaded_session_data['turns']

        tool_result = execute_tool_call(function_call, session_manager, session_id, settings, project_root)
        
        reloaded_session_data = session_manager.history_manager.get_session(session_id)
        if reloaded_session_data:
            if 'references' in reloaded_session_data:
                session_data_for_prompt['references'] = reloaded_session_data['references']

        if isinstance(tool_result, dict) and 'error' in tool_result and tool_result['error'] != '(none)':
            formatted_response = {
                "status": "failed",
                "message": tool_result['error']
            }
        else:
            if isinstance(tool_result, dict) and 'message' in tool_result:
                message_content = tool_result['message']
            else:
                message_content = tool_result

            formatted_response = {
                "status": "succeeded",
                "message": message_content
            }

        tool_turn = {
            "type": "tool_response",
            "name": function_call.name,
            "response": formatted_response,
            "timestamp": get_current_timestamp(local_tz)
        }
        session_manager.add_turn_to_session(session_id, tool_turn)
        reloaded_session_data = session_manager.history_manager.get_session(session_id)
        if reloaded_session_data:
            session_data_for_prompt['turns'] = reloaded_session_data['turns']

    return model_response_text, token_count
