import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.turn import ToolResponseTurn
from pipe.core.repositories.settings_repository import SettingsRepository
from pipe.core.tools.read_many_files import read_many_files
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.utils.path import get_project_root


def test_mcp_conversion():
    os.environ["PIPE_SESSION_ID"] = "dummy"
    # Create a small result
    result = read_many_files(paths=["README.md"])

    # Simulate mcp_server logic
    if hasattr(result, "model_dump"):
        result_dict = result.model_dump()
    else:
        result_dict = result

    print(f"Result structure: {list(result_dict.keys())}")

    data_content = result_dict["data"]
    print(f"Data structure: {list(data_content.keys())}")

    formatted_response = data_content.copy()
    formatted_response["status"] = "succeeded"

    print(f"Formatted response keys: {list(formatted_response.keys())}")

    # Try to create ToolResponseTurn
    project_root = get_project_root()
    settings = SettingsRepository().load()
    factory = ServiceFactory(project_root, settings)
    session_service = factory.create_session_service()

    try:
        turn = ToolResponseTurn(
            type="tool_response",
            name="read_many_files",
            response=formatted_response,
            timestamp=get_current_timestamp(session_service.timezone_obj),
        )
        print("Successfully created ToolResponseTurn")
        print(f"JSON: {turn.model_dump_json(indent=2)[:500]}...")
    except Exception as e:
        print(f"Failed to create ToolResponseTurn: {e}")


if __name__ == "__main__":
    test_mcp_conversion()
