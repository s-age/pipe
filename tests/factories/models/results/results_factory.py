"""Factory for creating Result model test fixtures."""

from pipe.core.models.results.compress_session_turns_result import (
    CompressSessionTurnsResult,
)
from pipe.core.models.results.delete_session_turns_result import (
    DeleteSessionTurnsResult,
)
from pipe.core.models.results.delete_todos_result import DeleteTodosResult
from pipe.core.models.results.edit_todos_result import EditTodosResult
from pipe.core.models.results.glob_result import GlobResult
from pipe.core.models.results.py_auto_format_code_result import (
    FormatterToolResult,
    PyAutoFormatCodeResult,
)
from pipe.core.models.results.py_run_and_test_code_result import PyRunAndTestCodeResult
from pipe.core.models.results.read_file_result import ReadFileResult
from pipe.core.models.results.read_many_files_result import (
    FileContent,
    ReadManyFilesResult,
)
from pipe.core.models.results.replace_result import ReplaceResult
from pipe.core.models.results.run_shell_command_result import RunShellCommandResult
from pipe.core.models.results.save_memory_result import SaveMemoryResult
from pipe.core.models.results.search_file_content_result import (
    FileMatchItem,
    SearchFileContentResult,
)
from pipe.core.models.results.session_tree_result import (
    SessionOverview,
    SessionTreeNode,
    SessionTreeResult,
)
from pipe.core.models.results.ts_auto_format_code_result import (
    FormatterToolResult as TsFormatterToolResult,
)
from pipe.core.models.results.ts_auto_format_code_result import (
    TsAutoFormatCodeResult,
)
from pipe.core.models.results.ts_run_and_test_code_result import (
    TsRunAndTestCodeResult,
)
from pipe.core.models.results.verification_result import (
    VerificationError,
    VerificationResult,
)
from pipe.core.models.results.web_fetch_result import WebFetchResult
from pipe.core.models.results.write_file_result import WriteFileResult
from pipe.core.models.todo import TodoItem


class ResultFactory:
    """Helper class for creating Result objects in tests."""

    @staticmethod
    def create_verification_result(
        verification_status: str = "pending_approval",
        verifier_session_id: str = "verifier-123",
        message: str | None = "Verification successful",
        verifier_response: str = "Looks good",
        next_action: str = "Proceed with caution",
        **kwargs,
    ) -> VerificationResult:
        """Create a VerificationResult object."""
        return VerificationResult(
            verification_status=verification_status,  # type: ignore
            verifier_session_id=verifier_session_id,
            message=message,
            verifier_response=verifier_response,
            next_action=next_action,
            **kwargs,
        )

    @staticmethod
    def create_verification_error(
        error: str = "Verification failed due to timeout",
        **kwargs,
    ) -> VerificationError:
        """Create a VerificationError object."""
        return VerificationError(error=error, **kwargs)

    @staticmethod
    def create_session_overview(
        session_id: str = "test-session",
        created_at: str = "2025-01-01T00:00:00+09:00",
        last_updated_at: str = "2025-01-01T01:00:00+09:00",
        purpose: str | None = "test purpose",
        **kwargs,
    ) -> SessionOverview:
        """Create a SessionOverview object."""
        return SessionOverview(
            session_id=session_id,
            created_at=created_at,
            last_updated_at=last_updated_at,
            purpose=purpose,
            **kwargs,
        )

    @staticmethod
    def create_save_memory_result(
        status: str = "success",
        message: str | None = "Memory saved successfully",
        **kwargs,
    ) -> SaveMemoryResult:
        """Create a SaveMemoryResult object."""
        return SaveMemoryResult(status=status, message=message, **kwargs)

    @staticmethod
    def create_file_content(
        path: str = "test.py",
        content: str | None = "print('hello')",
        error: str | None = None,
        **kwargs,
    ) -> FileContent:
        """Create a FileContent object."""
        return FileContent(path=path, content=content, error=error, **kwargs)

    @staticmethod
    def create_read_many_files_result(
        files: list[FileContent] | None = None,
        message: str | None = "Files read successfully",
        error: str | None = None,
        **kwargs,
    ) -> ReadManyFilesResult:
        """Create a ReadManyFilesResult object."""
        if files is None:
            files = [ResultFactory.create_file_content()]

        return ReadManyFilesResult(files=files, message=message, error=error, **kwargs)

    @staticmethod
    def create_formatter_tool_result(
        tool: str = "black",
        stdout: str | None = "reformatted src/main.py",
        stderr: str | None = "",
        exit_code: int = 0,
        error: str | None = None,
        message: str | None = "Formatted successfully",
        **kwargs,
    ) -> FormatterToolResult:
        """Create a FormatterToolResult object."""
        return FormatterToolResult(
            tool=tool,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            error=error,
            message=message,
            **kwargs,
        )

    @staticmethod
    def create_py_auto_format_code_result(
        formatting_results: list[FormatterToolResult] | None = None,
        message: str | None = "Code formatted successfully",
        **kwargs,
    ) -> PyAutoFormatCodeResult:
        """Create a PyAutoFormatCodeResult object."""
        if formatting_results is None:
            formatting_results = [ResultFactory.create_formatter_tool_result()]

        return PyAutoFormatCodeResult(
            formatting_results=formatting_results, message=message, **kwargs
        )

    @staticmethod
    def create_ts_formatter_tool_result(
        tool: str = "prettier",
        stdout: str | None = "src/main.tsx formatted",
        stderr: str | None = "",
        exit_code: int = 0,
        error: str | None = None,
        message: str | None = "Formatted successfully",
        **kwargs,
    ) -> TsFormatterToolResult:
        """Create a TsFormatterToolResult object."""
        return TsFormatterToolResult(
            tool=tool,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            error=error,
            message=message,
            **kwargs,
        )

    @staticmethod
    def create_ts_auto_format_code_result(
        formatting_results: list[TsFormatterToolResult] | None = None,
        message: str | None = "TypeScript code formatted successfully",
        **kwargs,
    ) -> TsAutoFormatCodeResult:
        """Create a TsAutoFormatCodeResult object."""
        if formatting_results is None:
            formatting_results = [ResultFactory.create_ts_formatter_tool_result()]

        return TsAutoFormatCodeResult(
            formatting_results=formatting_results, message=message, **kwargs
        )

    @staticmethod
    def create_glob_result(
        content: str | None = "src/main.py\nsrc/utils.py",
        error: str | None = None,
        **kwargs,
    ) -> GlobResult:
        """Create a GlobResult object."""
        return GlobResult(content=content, error=error, **kwargs)

    @staticmethod
    def create_compress_session_turns_result(
        message: str | None = "Turns compressed successfully",
        current_turn_count: int | None = 5,
        error: str | None = None,
        **kwargs,
    ) -> CompressSessionTurnsResult:
        """Create a CompressSessionTurnsResult object."""
        return CompressSessionTurnsResult(
            message=message,
            current_turn_count=current_turn_count,
            error=error,
            **kwargs,
        )

    @staticmethod
    def create_delete_session_turns_result(
        message: str | None = "Turns deleted successfully",
        error: str | None = None,
        **kwargs,
    ) -> DeleteSessionTurnsResult:
        """Create a DeleteSessionTurnsResult object."""
        return DeleteSessionTurnsResult(message=message, error=error, **kwargs)

    @staticmethod
    def create_delete_todos_result(
        message: str | None = "Todos deleted successfully",
        current_todos: list[TodoItem] | None = None,
        error: str | None = None,
        **kwargs,
    ) -> DeleteTodosResult:
        """Create a DeleteTodosResult object."""
        return DeleteTodosResult(
            message=message, current_todos=current_todos or [], error=error, **kwargs
        )

    @staticmethod
    def create_edit_todos_result(
        message: str | None = "Todos updated successfully",
        current_todos: list[TodoItem] | None = None,
        error: str | None = None,
        **kwargs,
    ) -> EditTodosResult:
        """Create an EditTodosResult object."""
        return EditTodosResult(
            message=message, current_todos=current_todos or [], error=error, **kwargs
        )

    @staticmethod
    def create_py_run_and_test_code_result(
        stdout: str | None = "Hello, World!",
        stderr: str | None = "",
        exit_code: int = 0,
        message: str | None = "Execution successful",
        error: str | None = None,
        **kwargs,
    ) -> PyRunAndTestCodeResult:
        """Create a PyRunAndTestCodeResult object."""
        return PyRunAndTestCodeResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            message=message,
            error=error,
            **kwargs,
        )

    @staticmethod
    def create_ts_run_and_test_code_result(
        stdout: str | None = "Hello from TypeScript",
        stderr: str | None = "",
        exit_code: int = 0,
        message: str | None = "Execution successful",
        error: str | None = None,
        **kwargs,
    ) -> TsRunAndTestCodeResult:
        """Create a TsRunAndTestCodeResult object."""
        return TsRunAndTestCodeResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            message=message,
            error=error,
            **kwargs,
        )

    @staticmethod
    def create_read_file_result(
        content: str | None = "test content",
        message: str | None = "File read successfully",
        error: str | None = None,
        **kwargs,
    ) -> ReadFileResult:
        """Create a ReadFileResult object."""
        return ReadFileResult(content=content, message=message, error=error, **kwargs)

    @staticmethod
    def create_replace_result(
        status: str = "success",
        message: str | None = "Replacement successful",
        diff: str | None = "--- a.py\n+++ b.py\n-old\n+new",
        error: str | None = None,
        **kwargs,
    ) -> ReplaceResult:
        """Create a ReplaceResult object."""
        return ReplaceResult(
            status=status, message=message, diff=diff, error=error, **kwargs
        )

    @staticmethod
    def create_run_shell_command_result(
        command: str | None = "ls -l",
        directory: str | None = "/tmp",
        stdout: str | None = "total 0",
        stderr: str | None = "",
        exit_code: int = 0,
        error: str | None = None,
        signal: str | None = "(none)",
        background_pids: str | None = "(none)",
        process_group_pgid: str | None = "(none)",
        **kwargs,
    ) -> RunShellCommandResult:
        """Create a RunShellCommandResult object."""
        return RunShellCommandResult(
            command=command,
            directory=directory,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            error=error,
            signal=signal,
            background_pids=background_pids,
            process_group_pgid=process_group_pgid,
            **kwargs,
        )

    @staticmethod
    def create_file_match_item(
        file_path: str | None = "src/main.py",
        line_number: int | None = 10,
        line_content: str | None = "def main():",
        error: str | None = None,
        **kwargs,
    ) -> FileMatchItem:
        """Create a FileMatchItem object."""
        return FileMatchItem(
            file_path=file_path,
            line_number=line_number,
            line_content=line_content,
            error=error,
            **kwargs,
        )

    @staticmethod
    def create_search_file_content_result(
        content: list[FileMatchItem] | str | None = None, **kwargs
    ) -> SearchFileContentResult:
        """Create a SearchFileContentResult object."""
        if content is None:
            content = [ResultFactory.create_file_match_item()]

        return SearchFileContentResult(content=content, **kwargs)

    @staticmethod
    def create_session_tree_node(
        session_id: str = "test-session",
        overview: SessionOverview | None = None,
        children: list[SessionTreeNode] | None = None,
        **kwargs,
    ) -> SessionTreeNode:
        """Create a SessionTreeNode object."""
        if overview is None:
            overview = ResultFactory.create_session_overview(session_id=session_id)
        return SessionTreeNode(
            session_id=session_id, overview=overview, children=children or [], **kwargs
        )

    @staticmethod
    def create_session_tree_result(
        sessions: dict[str, SessionOverview] | None = None,
        session_tree: list[SessionTreeNode] | None = None,
        **kwargs,
    ) -> SessionTreeResult:
        """Create a SessionTreeResult object."""
        if sessions is None:
            overview = ResultFactory.create_session_overview(session_id="test-session")
            sessions = {"test-session": overview}
        if session_tree is None:
            session_tree = [
                ResultFactory.create_session_tree_node(session_id="test-session")
            ]
        return SessionTreeResult(sessions=sessions, session_tree=session_tree, **kwargs)

    @staticmethod
    def create_web_fetch_result(
        message: str | None = "Web content fetched successfully",
        error: str | None = None,
        **kwargs,
    ) -> WebFetchResult:
        """Create a WebFetchResult object."""
        return WebFetchResult(message=message, error=error, **kwargs)

    @staticmethod
    def create_write_file_result(
        status: str = "success",
        message: str | None = "File written successfully",
        diff: str | None = "--- a.py\n+++ b.py\n-old\n+new",
        error: str | None = None,
        **kwargs,
    ) -> WriteFileResult:
        """Create a WriteFileResult object."""
        return WriteFileResult(
            status=status, message=message, diff=diff, error=error, **kwargs
        )
