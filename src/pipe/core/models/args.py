from dataclasses import dataclass, field


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
    artifacts: list[str] = field(default_factory=list)
    procedure: str | None = None
    multi_step_reasoning: bool = False
    fork: str | None = None
    at_turn: int | None = None
    api_mode: str | None = None
    therapist: str | None = None
    output_format: str = "json"

    @classmethod
    def from_parsed_args(cls, parsed_args):
        """Creates an instance from argparse's parsed arguments."""

        def flatten_list_arg(arg_value):
            """Flatten list arguments that may contain comma-separated values.

            Supports both:
            - Multiple --arg flags: ['file1.md', 'file2.md'] (action='append')
            - Comma-separated values: 'file1.md,file2.md' (string)
            - Mixed: ['file1.md', 'file2.md,file3.md'] (action='append' with commas)
            """
            if not arg_value:
                return []
            # Handle both string (old behavior) and list (new with action='append')
            if isinstance(arg_value, str):
                # Old behavior: single string with comma-separated values
                return [v.strip() for v in arg_value.split(",") if v.strip()]
            # New behavior: list due to action='append'
            result = []
            for item in arg_value:
                # Each item might be comma-separated
                result.extend([v.strip() for v in item.split(",") if v.strip()])
            return result

        return cls(
            dry_run=parsed_args.dry_run,
            session=parsed_args.session,
            purpose=parsed_args.purpose,
            background=parsed_args.background,
            roles=flatten_list_arg(parsed_args.roles),
            parent=parsed_args.parent,
            instruction=parsed_args.instruction,
            references=flatten_list_arg(parsed_args.references),
            references_persist=flatten_list_arg(parsed_args.references_persist),
            artifacts=flatten_list_arg(parsed_args.artifacts),
            procedure=parsed_args.procedure,
            multi_step_reasoning=parsed_args.multi_step_reasoning,
            fork=parsed_args.fork,
            at_turn=parsed_args.at_turn,
            api_mode=parsed_args.api_mode,
            therapist=getattr(parsed_args, "therapist", None),
            output_format=getattr(parsed_args, "output_format", "json"),
        )
