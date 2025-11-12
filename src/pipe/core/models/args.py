from dataclasses import dataclass, field

from pipe.core.models.artifact import Artifact


@dataclass
class TaktArgs:
    """Arguments parsed from the command line for takt."""

    dry_run: bool = False
    session: str | None = None
    purpose: str | None = None
    background: str | None = None
    roles: list[str] = field(default_factory=list)
    parent: str | None = None
    instruction: str | None = None
    references: list[str] = field(default_factory=list)
    references_persist: list[str] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    procedure: str | None = None
    multi_step_reasoning: bool = False
    fork: str | None = None
    at_turn: int | None = None
    api_mode: str | None = None

    def to_turn(self, timestamp: str):
        """Converts args to a UserTaskTurn."""
        from pipe.core.models.turn import UserTaskTurn

        return UserTaskTurn(
            type="user_task", instruction=self.instruction, timestamp=timestamp
        )

    @classmethod
    def from_parsed_args(cls, parsed_args):
        """Creates an instance from argparse's parsed arguments."""
        return cls(
            dry_run=parsed_args.dry_run,
            session=parsed_args.session,
            purpose=parsed_args.purpose,
            background=parsed_args.background,
            roles=(
                [r.strip() for r in parsed_args.roles.split(",")]
                if parsed_args.roles
                else []
            ),
            parent=parsed_args.parent,
            instruction=parsed_args.instruction,
            references=(
                [r.strip() for r in parsed_args.references.split(",")]
                if parsed_args.references
                else []
            ),
            references_persist=(
                [r.strip() for r in parsed_args.references_persist.split(",")]
                if parsed_args.references_persist
                else []
            ),
            artifacts=(
                [r.strip() for r in parsed_args.artifacts.split(",")]
                if parsed_args.artifacts
                else []
            ),
            procedure=parsed_args.procedure,
            multi_step_reasoning=parsed_args.multi_step_reasoning,
            fork=parsed_args.fork,
            at_turn=parsed_args.at_turn,
            api_mode=parsed_args.api_mode,
        )
