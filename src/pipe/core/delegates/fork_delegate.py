"""
Delegate for handling the 'fork' command.
"""

from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService


def run(args: TaktArgs, session_service: SessionService):
    """Executes the session fork logic."""
    if not args.at_turn:
        raise ValueError("Error: --at-turn is required when using --fork.")

    try:
        fork_index = args.at_turn - 1
        session_service.fork_session(args.fork, fork_index)
        print(f"Successfully forked session {args.fork} at turn {args.at_turn}.")
    except (FileNotFoundError, IndexError) as e:
        raise ValueError(f"Error: {e}")
