from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService
from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.models.turn import ModelResponseTurn
from pipe.core.utils.datetime import get_current_timestamp

def run(
    args: TaktArgs,
    session_service: SessionService
):
    """
    Handles the logic for the 'gemini-cli' mode by delegating to call_gemini_cli,
    then correctly merging the tool pool and saving the final model response.
    """
    # 1. Call the agent, which may populate the session's tool pool
    response_text = call_gemini_cli(
        session_service
    )

    # 2. Explicitly merge the tool calls from the pool into the main turns history
    session_service.merge_pool_into_turns(session_service.current_session_id)

    # 3. Create the final model response turn
    final_turn = ModelResponseTurn(
        type="model_response",
        content=response_text,
        timestamp=get_current_timestamp(session_service.timezone_obj)
    )

    # 4. Add the final model response turn to the session
    session_service.add_turn_to_session(session_service.current_session_id, final_turn)

    return response_text
