import sys
from pipe.core.gemini_cli import call_gemini_cli

from pipe.core.models.session import Session

def run(args, settings, session_data: Session, project_root, api_mode, enable_multi_step_reasoning):
    """The delegate function for running in gemini-cli mode."""
    command_to_print = ['gemini', '-m', settings.get('model'), '-p', '...'] # Simplified for logging
    if settings.get('yolo', False):
        command_to_print.insert(1, '-y')
    if enable_multi_step_reasoning:
        command_to_print.append('--multi-step-reasoning')
    
    response = call_gemini_cli(
        settings=settings,
        session_data=session_data,
        project_root=project_root,
        instruction=args.instruction,
        api_mode=api_mode,
        multi_step_reasoning_enabled=enable_multi_step_reasoning,
        session_id=args.session
    )
    return response
