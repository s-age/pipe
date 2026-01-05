"""Unit tests for action_responses.py."""

from pipe.core.collections.backup_files import SessionSummary
from pipe.core.models.file_search import LsEntry
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.procedure import ProcedureOption
from pipe.core.models.role import RoleOption
from pipe.core.models.search_result import SessionSearchResult
from pipe.core.models.turn import UserTaskTurn
from pipe.web.action_responses import (
    BackupListResponse,
    LsResponse,
    ProceduresResponse,
    ReferenceEditResponse,
    ReferenceToggleResponse,
    RolesResponse,
    SearchSessionsResponse,
    SessionDeleteResponse,
    SessionForkResponse,
    SessionOverview,
    SessionStartResponse,
    SessionStopResponse,
    SessionTreeNode,
    SessionTreeResponse,
    SessionTurnsResponse,
    SettingsInfo,
    SettingsResponse,
    SimpleItem,
    StatusResponse,
    SuccessMessageResponse,
)


class TestActionResponses:
    """Tests for web action response models."""

    def test_success_message_response(self):
        """Test SuccessMessageResponse validation and serialization."""
        data = {"message": "Operation successful"}
        response = SuccessMessageResponse(**data)
        assert response.message == "Operation successful"
        assert response.model_dump(by_alias=True) == data

    def test_status_response(self):
        """Test StatusResponse validation and serialization."""
        data = {"status": "ok"}
        response = StatusResponse(**data)
        assert response.status == "ok"
        assert response.model_dump(by_alias=True) == data

    def test_session_start_response(self):
        """Test SessionStartResponse validation and serialization."""
        data = {"sessionId": "test-session"}
        # Test camelCase input
        response = SessionStartResponse(**data)
        assert response.session_id == "test-session"
        # Test serialization to camelCase
        assert response.model_dump(by_alias=True) == data

    def test_session_fork_response(self):
        """Test SessionForkResponse validation and serialization."""
        data = {"newSessionId": "new-session"}
        response = SessionForkResponse(**data)
        assert response.new_session_id == "new-session"
        assert response.model_dump(by_alias=True) == data

    def test_session_overview(self):
        """Test SessionOverview validation and serialization."""
        data = {
            "sessionId": "test-session",
            "purpose": "Testing",
            "createdAt": "2025-01-01T00:00:00Z",
            "lastUpdatedAt": "2025-01-01T01:00:00Z",
            "extraField": "allowed",
        }
        response = SessionOverview(**data)
        assert response.session_id == "test-session"
        assert response.purpose == "Testing"
        # Verify extra fields are allowed
        dump = response.model_dump(by_alias=True)
        assert dump["extraField"] == "allowed"

    def test_session_tree_node(self):
        """Test SessionTreeNode validation and serialization."""
        overview = SessionOverview(session_id="child-session")
        data = {
            "sessionId": "parent-session",
            "overview": overview.model_dump(by_alias=True),
            "children": [
                {
                    "sessionId": "child-session",
                    "overview": overview.model_dump(by_alias=True),
                    "children": [],
                }
            ],
        }
        response = SessionTreeNode(**data)
        assert response.session_id == "parent-session"
        assert len(response.children) == 1
        assert response.children[0].session_id == "child-session"
        assert response.model_dump(by_alias=True) == data

    def test_session_tree_response(self):
        """Test SessionTreeResponse validation and serialization."""
        overview = SessionOverview(session_id="test-session")
        node = SessionTreeNode(session_id="test-session", overview=overview)
        data = {
            "sessions": {"test-session": overview.model_dump(by_alias=True)},
            "sessionTree": [node.model_dump(by_alias=True)],
        }
        response = SessionTreeResponse(**data)
        assert "test-session" in response.sessions
        assert len(response.session_tree) == 1
        assert response.model_dump(by_alias=True) == data

    def test_ls_response(self):
        """Test LsResponse validation and serialization."""
        entry = LsEntry(
            name="file.txt",
            is_dir=False,
            path="/path/file.txt",
            parent_path_hash="hash",
        )
        data = {"entries": [entry.model_dump(by_alias=True)]}
        response = LsResponse(**data)
        assert len(response.entries) == 1
        assert response.entries[0].name == "file.txt"
        assert response.model_dump(by_alias=True) == data

    def test_simple_item(self):
        """Test SimpleItem validation and serialization."""
        data = {
            "name": "Item Name",
            "path": "/path/to/item",
            "description": "Item Description",
        }
        response = SimpleItem(**data)
        assert response.name == "Item Name"
        assert response.path == "/path/to/item"
        assert response.model_dump(by_alias=True) == data

    def test_roles_response(self):
        """Test RolesResponse validation and serialization."""
        role = RoleOption(label="Developer", value="dev")
        data = {"roles": [role.model_dump(by_alias=True)]}
        response = RolesResponse(**data)
        assert len(response.roles) == 1
        assert response.roles[0].label == "Developer"
        assert response.model_dump(by_alias=True) == data

    def test_procedures_response(self):
        """Test ProceduresResponse validation and serialization."""
        proc = ProcedureOption(label="Test Proc", value="test_proc")
        data = {"procedures": [proc.model_dump(by_alias=True)]}
        response = ProceduresResponse(**data)
        assert len(response.procedures) == 1
        assert response.procedures[0].label == "Test Proc"
        assert response.model_dump(by_alias=True) == data

    def test_search_sessions_response(self):
        """Test SearchSessionsResponse validation and serialization."""
        result = SessionSearchResult(session_id="test-session", title="Test Title")
        data = {"results": [result.model_dump(by_alias=True)]}
        response = SearchSessionsResponse(**data)
        assert len(response.results) == 1
        assert response.results[0].session_id == "test-session"
        assert response.model_dump(by_alias=True) == data

    def test_session_turns_response(self):
        """Test SessionTurnsResponse validation and serialization."""
        turn = UserTaskTurn(
            type="user_task", instruction="Hello", timestamp="2025-01-01T00:00:00Z"
        )
        data = {"turns": [turn.model_dump(by_alias=True)]}
        response = SessionTurnsResponse(**data)
        assert len(response.turns) == 1
        assert response.turns[0].type == "user_task"
        assert response.model_dump(by_alias=True) == data

    def test_backup_list_response(self):
        """Test BackupListResponse validation and serialization."""
        summary = SessionSummary(
            session_id="test-session",
            file_path="/path/to/backup.json",
            purpose="Testing",
            deleted_at="2025-01-01T00:00:00Z",
            session_data={"session_id": "test-session"},
        )
        data = {"sessions": [summary.model_dump(by_alias=True)]}
        response = BackupListResponse(**data)
        assert len(response.sessions) == 1
        assert response.sessions[0].session_id == "test-session"
        assert response.model_dump(by_alias=True) == data

    def test_reference_toggle_response(self):
        """Test ReferenceToggleResponse validation and serialization."""
        data = {"path": "/path/to/file", "disabled": True, "message": "Toggled"}
        response = ReferenceToggleResponse(**data)
        assert response.path == "/path/to/file"
        assert response.disabled is True
        assert response.model_dump(by_alias=True) == data

    def test_reference_edit_response(self):
        """Test ReferenceEditResponse validation and serialization."""
        data = {"message": "Edited", "path": "/path/to/file"}
        response = ReferenceEditResponse(**data)
        assert response.message == "Edited"
        assert response.path == "/path/to/file"
        assert response.model_dump(by_alias=True) == data

    def test_session_stop_response(self):
        """Test SessionStopResponse validation and serialization."""
        data = {"message": "Stopped", "sessionId": "test-session"}
        response = SessionStopResponse(**data)
        assert response.message == "Stopped"
        assert response.session_id == "test-session"
        assert response.model_dump(by_alias=True) == data

    def test_session_delete_response(self):
        """Test SessionDeleteResponse validation and serialization."""
        data = {"message": "Deleted", "sessionId": "test-session"}
        response = SessionDeleteResponse(**data)
        assert response.message == "Deleted"
        assert response.session_id == "test-session"
        assert response.model_dump(by_alias=True) == data

    def test_settings_info(self):
        """Test SettingsInfo validation and serialization."""
        hp = Hyperparameters(temperature=0.7, top_p=0.9, top_k=40)
        data = {
            "model": "gpt-4",
            "searchModel": "gpt-3.5",
            "contextLimit": 8192,
            "cacheUpdateThreshold": 100,
            "apiMode": "openai",
            "language": "en",
            "yolo": False,
            "maxToolCalls": 10,
            "expertMode": True,
            "sessionsPath": ".sessions",
            "referenceTtl": 3600,
            "toolResponseExpiration": 300,
            "timezone": "UTC",
            "hyperparameters": hp.model_dump(by_alias=True),
        }
        response = SettingsInfo(**data)
        assert response.model == "gpt-4"
        assert response.hyperparameters.temperature == 0.7
        assert response.model_dump(by_alias=True) == data

    def test_settings_response(self):
        """Test SettingsResponse validation and serialization."""
        hp = Hyperparameters(temperature=0.7)
        info = SettingsInfo(
            model="gpt-4",
            search_model="gpt-3.5",
            context_limit=8192,
            cache_update_threshold=100,
            api_mode="openai",
            language="en",
            yolo=False,
            max_tool_calls=10,
            expert_mode=True,
            sessions_path=".sessions",
            reference_ttl=3600,
            tool_response_expiration=300,
            timezone="UTC",
            hyperparameters=hp,
        )
        data = {"settings": info.model_dump(by_alias=True)}
        response = SettingsResponse(**data)
        assert response.settings.model == "gpt-4"
        assert response.model_dump(by_alias=True) == data
