from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TaktArgs:
    """Arguments parsed from the command line for takt."""
    dry_run: bool = False
    session: Optional[str] = None
    purpose: Optional[str] = None
    background: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    instruction: Optional[str] = None
    references: List[str] = field(default_factory=list)
    multi_step_reasoning: bool = False
    fork: Optional[str] = None
    at_turn: Optional[int] = None
    api_mode: Optional[str] = None

    @classmethod
    def from_parsed_args(cls, parsed_args):
        """Creates an instance from argparse's parsed arguments."""
        return cls(
            dry_run=parsed_args.dry_run,
            session=parsed_args.session,
            purpose=parsed_args.purpose,
            background=parsed_args.background,
            roles=[r.strip() for r in parsed_args.roles.split(',')] if parsed_args.roles else [],
            parent=parsed_args.parent,
            instruction=parsed_args.instruction,
            references=[r.strip() for r in parsed_args.references.split(',')] if parsed_args.references else [],
            multi_step_reasoning=parsed_args.multi_step_reasoning,
            fork=parsed_args.fork,
            at_turn=parsed_args.at_turn,
            api_mode=parsed_args.api_mode
        )
