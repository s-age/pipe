from pipe.core.collections.backup_files import SessionSummary
from pipe.core.models.base import CamelCaseModel
from pipe.core.models.file_search import LsEntry
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.procedure import ProcedureOption
from pipe.core.models.role import RoleOption
from pipe.core.models.search_result import SessionSearchResult
from pipe.core.models.turn import Turn
from pydantic import ConfigDict


class SuccessMessageResponse(CamelCaseModel):
    message: str


class StatusResponse(CamelCaseModel):
    status: str


class SessionStartResponse(CamelCaseModel):
    session_id: str


class SessionForkResponse(CamelCaseModel):
    new_session_id: str


class SessionOverview(CamelCaseModel):
    """Metadata summary of a session."""

    session_id: str
    purpose: str | None = None
    created_at: str | None = None
    last_updated_at: str | None = None
    # Allow other fields from the index
    model_config = ConfigDict(extra="allow")


class SessionTreeNode(CamelCaseModel):
    """A node in the session tree structure."""

    session_id: str
    overview: SessionOverview
    children: list["SessionTreeNode"] = []


class SessionTreeResponse(CamelCaseModel):
    """Response containing session tree data."""

    sessions: dict[str, SessionOverview]
    session_tree: list[SessionTreeNode]


class LsResponse(CamelCaseModel):
    entries: list[LsEntry]


class SimpleItem(CamelCaseModel):
    name: str
    path: str | None = None
    description: str | None = None


class RolesResponse(CamelCaseModel):
    roles: list[RoleOption]


class ProceduresResponse(CamelCaseModel):
    procedures: list[ProcedureOption]


class SearchSessionsResponse(CamelCaseModel):
    results: list[SessionSearchResult]


class SessionTurnsResponse(CamelCaseModel):
    turns: list[Turn]


class BackupListResponse(CamelCaseModel):
    sessions: list[SessionSummary]


class ReferenceToggleResponse(CamelCaseModel):
    path: str
    disabled: bool
    message: str | None = None


class ReferenceEditResponse(CamelCaseModel):
    message: str
    path: str


class SessionStopResponse(CamelCaseModel):
    message: str
    session_id: str


class SessionDeleteResponse(CamelCaseModel):
    message: str
    session_id: str


class SettingsInfo(CamelCaseModel):
    model: str
    search_model: str
    context_limit: int
    api_mode: str
    language: str
    yolo: bool
    max_tool_calls: int
    expert_mode: bool
    sessions_path: str
    reference_ttl: int
    tool_response_expiration: int
    timezone: str
    hyperparameters: Hyperparameters


class SettingsResponse(CamelCaseModel):
    settings: SettingsInfo
