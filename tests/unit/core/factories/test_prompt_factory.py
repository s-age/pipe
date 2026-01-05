"""Unit tests for PromptFactory."""

import os
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from pipe.core.factories.prompt_factory import PromptFactory
from pipe.core.models.prompt import Prompt
from pipe.core.models.prompts.constraints import PromptConstraints
from pipe.core.models.prompts.conversation_history import PromptConversationHistory
from pipe.core.models.prompts.roles import PromptRoles
from pipe.core.repositories.resource_repository import ResourceRepository

from tests.factories.models.artifact_factory import ArtifactFactory
from tests.factories.models.reference_factory import ReferenceFactory
from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.settings_factory import create_test_settings
from tests.factories.models.todo_factory import TodoFactory
from tests.factories.models.turn_factory import TurnFactory


@pytest.fixture
def mock_resource_repository():
    """Create a mock ResourceRepository."""
    repo = MagicMock(spec=ResourceRepository)
    # Use a consistent absolute path for testing
    repo.project_root = os.path.abspath("/app")
    return repo


@pytest.fixture
def factory(mock_resource_repository):
    """Create a PromptFactory instance."""
    return PromptFactory(
        project_root=os.path.abspath("/app"),
        resource_repository=mock_resource_repository,
    )


@pytest.fixture
def settings():
    """Create test settings."""
    return create_test_settings(timezone="UTC", language="Japanese")


class TestPromptFactory:
    """Tests for PromptFactory class."""

    def test_init(self, mock_resource_repository):
        """Test initialization of PromptFactory."""
        project_root = os.path.abspath("/app")
        factory = PromptFactory(
            project_root=project_root, resource_repository=mock_resource_repository
        )
        assert factory.project_root == project_root
        assert factory.resource_repository == mock_resource_repository

    @freeze_time("2025-01-01 12:00:00")
    @patch("pipe.core.domains.references.get_active_references")
    @patch("pipe.core.domains.todos.get_todos_for_prompt")
    @patch("pipe.core.collections.roles.RoleCollection")
    @patch("pipe.core.domains.turns.get_turns_for_prompt")
    def test_create_basic(
        self,
        mock_get_turns,
        mock_role_collection,
        mock_get_todos,
        mock_get_refs,
        factory,
        settings,
    ):
        """Test basic prompt creation with minimal data."""
        # Setup
        session = SessionFactory.create(
            purpose="Test Purpose", background="Test Background"
        )
        mock_get_refs.return_value = []
        mock_get_todos.return_value = []
        mock_role_collection.return_value.get_for_prompt.return_value = [
            "Role definition"
        ]
        mock_get_turns.return_value = iter([])

        # Execute
        prompt = factory.create(session=session, settings=settings)

        # Verify
        assert isinstance(prompt, Prompt)
        assert prompt.session_goal.purpose == "Test Purpose"
        assert prompt.session_goal.background == "Test Background"
        assert prompt.roles.definitions == ["Role definition"]
        assert prompt.constraints.language == "Japanese"
        # freezegun makes isoformat() return +00:00 for UTC
        assert prompt.current_datetime == "2025-01-01T12:00:00+00:00"
        assert prompt.current_task.instruction == ""
        assert (
            prompt.main_instruction
            == "Your main instruction is to be helpful and follow all previous instructions."
        )

    @patch("pipe.core.domains.references.get_active_references")
    def test_create_with_references(
        self, mock_get_refs, factory, settings, mock_resource_repository
    ):
        """Test prompt creation with file references."""
        # Setup
        session = SessionFactory.create()
        ref = ReferenceFactory.create(path="src/test.py")
        mock_get_refs.return_value = [ref]
        mock_resource_repository.read_text.return_value = "file content"

        # Execute
        prompt = factory.create(session=session, settings=settings)

        # Verify
        assert prompt.file_references is not None
        assert len(prompt.file_references) == 1
        assert prompt.file_references[0].path == "src/test.py"
        assert prompt.file_references[0].content == "file content"
        # Note: factory uses os.path.abspath(os.path.join(self.project_root, ref.path))
        expected_path = os.path.abspath(
            os.path.join(factory.project_root, "src/test.py")
        )
        mock_resource_repository.read_text.assert_called_once_with(
            expected_path, factory.project_root
        )

    @patch("pipe.core.domains.references.get_active_references")
    def test_create_with_references_outside_root(
        self, mock_get_refs, factory, settings, mock_resource_repository
    ):
        """Test prompt creation skips references outside project root."""
        # Setup
        session = SessionFactory.create()
        # Path that goes outside /app
        ref = ReferenceFactory.create(path="../../outside.py")
        mock_get_refs.return_value = [ref]

        # Execute
        prompt = factory.create(session=session, settings=settings)

        # Verify
        assert prompt.file_references is None
        mock_resource_repository.read_text.assert_not_called()

    @patch("pipe.core.domains.todos.get_todos_for_prompt")
    def test_create_with_todos(self, mock_get_todos, factory, settings):
        """Test prompt creation with todos."""
        session = SessionFactory.create()
        todo = TodoFactory.create(title="Task 1", description="Desc 1", checked=False)
        session.todos = [todo]
        mock_get_todos.return_value = [todo.model_dump()]

        prompt = factory.create(session=session, settings=settings)

        assert prompt.todos is not None
        assert len(prompt.todos) == 1
        assert prompt.todos[0].title == "Task 1"

    def test_create_with_artifacts(self, factory, settings):
        """Test prompt creation with artifacts."""
        session = SessionFactory.create()
        artifacts = ArtifactFactory.create_batch(2)

        prompt = factory.create(session=session, settings=settings, artifacts=artifacts)

        assert prompt.artifacts == artifacts

    def test_create_with_current_instruction(self, factory, settings):
        """Test prompt creation with explicit current instruction."""
        session = SessionFactory.create()
        instruction = "Do something specific"

        prompt = factory.create(
            session=session, settings=settings, current_instruction=instruction
        )

        assert prompt.current_task.instruction == instruction

    def test_create_with_last_turn_as_instruction(self, factory, settings):
        """Test prompt creation using the last turn as current instruction."""
        last_turn = TurnFactory.create_user_task(instruction="Last instruction")
        session = SessionFactory.create(turns=[last_turn])

        prompt = factory.create(session=session, settings=settings)

        assert prompt.current_task.instruction == "Last instruction"
        # History should be empty because the last turn was moved to current_task
        assert len(prompt.conversation_history.turns) == 0

    def test_create_with_history_and_instruction(self, factory, settings):
        """Test prompt creation with history and explicit instruction."""
        turn1 = TurnFactory.create_user_task(instruction="Turn 1")
        turn2 = TurnFactory.create_model_response(content="Response 2")
        session = SessionFactory.create(turns=[turn1, turn2])
        instruction = "Current instruction"

        prompt = factory.create(
            session=session, settings=settings, current_instruction=instruction
        )

        assert prompt.current_task.instruction == instruction
        # History should include both turns since the last one isn't a UserTaskTurn matching instruction
        assert len(prompt.conversation_history.turns) == 2

    def test_create_with_matching_last_turn_instruction(self, factory, settings):
        """Test prompt creation where current_instruction matches the last turn."""
        turn1 = TurnFactory.create_user_task(instruction="Turn 1")
        turn2 = TurnFactory.create_user_task(instruction="Current instruction")
        session = SessionFactory.create(turns=[turn1, turn2])
        instruction = "Current instruction"

        prompt = factory.create(
            session=session, settings=settings, current_instruction=instruction
        )

        assert prompt.current_task.instruction == instruction
        # Last turn should be excluded from history
        assert len(prompt.conversation_history.turns) == 1
        assert prompt.conversation_history.turns[0].instruction == "Turn 1"

    def test_create_with_session_hyperparameters(self, factory, settings):
        """Test prompt creation using session-specific hyperparameters."""
        from pipe.core.models.hyperparameters import Hyperparameters

        session_hp = Hyperparameters(temperature=0.8, top_p=0.95, top_k=50)
        session = SessionFactory.create(hyperparameters=session_hp)

        prompt = factory.create(session=session, settings=settings)

        assert prompt.constraints.hyperparameters.temperature == 0.8
        assert prompt.constraints.hyperparameters.top_p == 0.95
        assert prompt.constraints.hyperparameters.top_k == 50

    def test_create_with_reasoning_process(self, factory, settings):
        """Test prompt creation with reasoning process enabled."""
        session = SessionFactory.create(multi_step_reasoning_enabled=True)

        prompt = factory.create(session=session, settings=settings)

        assert prompt.reasoning_process is not None
        assert "Think step-by-step" in prompt.reasoning_process["description"]
        assert prompt.constraints.processing_config.multi_step_reasoning_active is True

    def test_build_constraints(self, factory, settings):
        """Test _build_constraints private method."""
        from pipe.core.models.hyperparameters import Hyperparameters

        hp = Hyperparameters(temperature=0.5, top_p=0.9, top_k=40)

        constraints = factory._build_constraints(settings, hp, True)

        assert isinstance(constraints, PromptConstraints)
        assert constraints.language == settings.language
        assert constraints.processing_config.multi_step_reasoning_active is True
        assert constraints.hyperparameters.temperature == 0.5
        assert constraints.hyperparameters.top_p == 0.9
        assert constraints.hyperparameters.top_k == 40

    @patch("pipe.core.collections.roles.RoleCollection")
    def test_build_roles(self, mock_role_collection, factory):
        """Test _build_roles private method."""
        mock_role_collection.return_value.get_for_prompt.return_value = [
            "Role 1",
            "Role 2",
        ]

        roles = factory._build_roles(["path1", "path2"])

        assert isinstance(roles, PromptRoles)
        assert roles.definitions == ["Role 1", "Role 2"]
        mock_role_collection.assert_called_once_with(["path1", "path2"])

    @patch("pipe.core.domains.turns.get_turns_for_prompt")
    def test_build_conversation_history(self, mock_get_turns, factory):
        """Test _build_conversation_history private method."""
        turn1 = TurnFactory.create_user_task(instruction="1")
        turn2 = TurnFactory.create_model_response(content="2")
        # get_turns_for_prompt returns in reverse order (newest first)
        mock_get_turns.return_value = iter([turn2, turn1])

        history = factory._build_conversation_history([], 3)

        assert isinstance(history, PromptConversationHistory)
        # Should be reversed back to chronological order (oldest first)
        assert history.turns == [turn1, turn2]

    def test_resolve_procedure_content_success(self, factory, mock_resource_repository):
        """Test _resolve_procedure_content with valid path."""
        mock_resource_repository.read_text.return_value = "procedure content"

        content = factory._resolve_procedure_content("proc.md", "UTC")

        assert content == "procedure content"
        expected_path = os.path.join(factory.project_root, "proc.md")
        mock_resource_repository.read_text.assert_called_once_with(
            expected_path, factory.project_root
        )

    def test_resolve_procedure_content_none(self, factory):
        """Test _resolve_procedure_content with None path."""
        assert factory._resolve_procedure_content(None, "UTC") is None

    def test_resolve_procedure_content_not_found(
        self, factory, mock_resource_repository
    ):
        """Test _resolve_procedure_content with missing file."""
        mock_resource_repository.read_text.side_effect = FileNotFoundError()

        content = factory._resolve_procedure_content("missing.md", "UTC")

        assert "Error: Procedure file not found" in content

    @patch("pipe.core.domains.references.get_active_references")
    def test_create_with_reference_read_none(
        self, mock_get_refs, factory, settings, mock_resource_repository
    ):
        """Test prompt creation when reference read returns None."""
        session = SessionFactory.create()
        ref = ReferenceFactory.create(path="src/test.py")
        mock_get_refs.return_value = [ref]
        mock_resource_repository.read_text.return_value = None

        prompt = factory.create(session=session, settings=settings)

        assert prompt.file_references is None

    @patch("pipe.core.domains.references.get_active_references")
    def test_create_with_reference_read_error(
        self, mock_get_refs, factory, settings, mock_resource_repository
    ):
        """Test prompt creation when reference read raises FileNotFoundError."""
        session = SessionFactory.create()
        ref = ReferenceFactory.create(path="src/test.py")
        mock_get_refs.return_value = [ref]
        mock_resource_repository.read_text.side_effect = FileNotFoundError("Not found")

        prompt = factory.create(session=session, settings=settings)

        assert prompt.file_references is None

    @patch("pipe.core.domains.references.get_active_references")
    def test_create_with_reference_generic_error(
        self, mock_get_refs, factory, settings, mock_resource_repository
    ):
        """Test prompt creation when reference read raises a generic Exception."""
        session = SessionFactory.create()
        ref = ReferenceFactory.create(path="src/test.py")
        mock_get_refs.return_value = [ref]
        mock_resource_repository.read_text.side_effect = Exception("Generic error")

        prompt = factory.create(session=session, settings=settings)

        assert prompt.file_references is None
