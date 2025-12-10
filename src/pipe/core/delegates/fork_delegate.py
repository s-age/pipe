"""
Delegate for handling the 'fork' command.
"""

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings


def run(args: TaktArgs, project_root: str, settings: Settings):
    """Executes the session fork logic."""
    if not args.at_turn:
        raise ValueError("Error: --at-turn is required when using --fork.")

    try:
        fork_index = args.at_turn - 1
        service_factory = ServiceFactory(project_root, settings)
        workflow_service = service_factory.create_session_workflow_service()
        workflow_service.fork_session(args.fork, fork_index)
        print(f"Successfully forked session {args.fork} at turn {args.at_turn}.")
    except (FileNotFoundError, IndexError) as e:
        raise ValueError(f"Error: {e}")
