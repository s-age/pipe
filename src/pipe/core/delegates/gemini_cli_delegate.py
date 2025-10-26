from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService
from pipe.core.gemini_cli import call_gemini_cli

def run(
    args: TaktArgs,
    session_service: SessionService
):
    """
    Handles the logic for the 'gemini-cli' mode by delegating to call_gemini_cli.
    """
    return call_gemini_cli(
        session_service
    )
