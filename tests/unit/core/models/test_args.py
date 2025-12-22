from argparse import Namespace

from pipe.core.models.args import TaktArgs


class TestTaktArgs:
    """Tests for TaktArgs dataclass and parsing logic."""

    def test_init_defaults(self):
        """Test initialization with default values."""
        args = TaktArgs()
        assert args.dry_run is False
        assert args.session is None
        assert args.purpose is None
        assert args.background is None
        assert args.roles == []
        assert args.parent is None
        assert args.instruction is None
        assert args.references == []
        assert args.references_persist == []
        assert args.artifacts == []
        assert args.procedure is None
        assert args.multi_step_reasoning is False
        assert args.fork is None
        assert args.at_turn is None
        assert args.api_mode is None
        assert args.therapist is None
        assert args.output_format == "json"

    def test_from_parsed_args_basic(self):
        """Test creation from basic parsed arguments."""
        namespace = Namespace(
            dry_run=True,
            session="test-session",
            purpose="Test Purpose",
            background="Test Background",
            roles=None,
            parent=None,
            instruction="Test Instruction",
            references=None,
            references_persist=None,
            artifacts=None,
            procedure=None,
            multi_step_reasoning=True,
            fork=None,
            at_turn=None,
            api_mode=None,
            therapist="Test Therapist",
            output_format="text",
        )

        args = TaktArgs.from_parsed_args(namespace)

        assert args.dry_run is True
        assert args.session == "test-session"
        assert args.purpose == "Test Purpose"
        assert args.background == "Test Background"
        assert args.roles == []
        assert args.instruction == "Test Instruction"
        assert args.multi_step_reasoning is True
        assert args.therapist == "Test Therapist"
        assert args.output_format == "text"

    def test_from_parsed_args_list_parsing(self):
        """Test parsing of comma-separated list strings."""
        namespace = Namespace(
            dry_run=False,
            session=None,
            purpose=None,
            background=None,
            roles=" dev, tester , manager ",  # whitespace handling
            parent=None,
            instruction=None,
            references="ref1.md,ref2.py",
            references_persist="mem1.txt",
            artifacts="art1, art2",
            procedure=None,
            multi_step_reasoning=False,
            fork=None,
            at_turn=None,
            api_mode=None,
        )

        args = TaktArgs.from_parsed_args(namespace)

        assert args.roles == ["dev", "tester", "manager"]
        assert args.references == ["ref1.md", "ref2.py"]
        assert args.references_persist == ["mem1.txt"]
        # Note: Currently implementation parses artifacts as list of strings
        assert args.artifacts == ["art1", "art2"]

    def test_from_parsed_args_missing_optional_fields(self):
        """Test behavior when optional fields are missing from Namespace."""
        # Namespace without 'therapist' and 'output_format'
        namespace = Namespace(
            dry_run=False,
            session=None,
            purpose=None,
            background=None,
            roles=None,
            parent=None,
            instruction=None,
            references=None,
            references_persist=None,
            artifacts=None,
            procedure=None,
            multi_step_reasoning=False,
            fork=None,
            at_turn=None,
            api_mode=None,
        )

        args = TaktArgs.from_parsed_args(namespace)

        assert args.therapist is None
        assert args.output_format == "json"  # Default value check
