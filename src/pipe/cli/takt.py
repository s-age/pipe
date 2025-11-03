import argparse
import os
import sys
import warnings

from dotenv import load_dotenv
from pipe.core.dispatcher import dispatch
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_text_file, read_yaml_file
from pipe.core.validators.sessions import start_session as start_session_validator

# Ignore specific warnings from the genai library
warnings.filterwarnings(
    "ignore", message=".*there are non-text parts in the response.*"
)
# Ignore Pydantic warnings about 'Operation' class from google-genai
warnings.filterwarnings(
    "ignore", message='Field name ".*" shadows an attribute in parent "Operation";'
)


def check_and_show_warning(project_root: str) -> bool:
    """Checks for the warning file, displays it, and gets user consent."""
    sealed_path = os.path.join(project_root, "sealed.txt")
    unsealed_path = os.path.join(project_root, "unsealed.txt")

    if os.path.exists(unsealed_path):
        return True

    warning_content = read_text_file(sealed_path)
    if not warning_content:
        return True

    print("--- IMPORTANT NOTICE ---")
    print(warning_content)
    print("------------------------")

    while True:
        try:
            response = (
                input("Do you agree to the terms above? (yes/no): ").lower().strip()
            )
            if response == "yes":
                os.rename(sealed_path, unsealed_path)
                print("Thank you. Proceeding...")
                return True
            elif response == "no":
                print("You must agree to the terms to use this tool. Exiting.")
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled. Exiting.")
            return False


def _parse_arguments():
    parser = argparse.ArgumentParser(
        description="A task-oriented chat agent for context engineering."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and print the prompt without executing.",
    )
    parser.add_argument(
        "--session",
        type=str,
        help="The ID of the session to continue, edit, or compress.",
    )
    parser.add_argument(
        "--purpose", type=str, help="The overall purpose of the new session."
    )
    parser.add_argument(
        "--background", type=str, help="The background context for the new session."
    )
    parser.add_argument(
        "--roles",
        type=str,
        help="Comma-separated paths to role files for the new session.",
    )
    parser.add_argument("--parent", type=str, help="The ID of the parent session.")
    parser.add_argument(
        "--instruction", type=str, help="The specific instruction for the current task."
    )
    parser.add_argument(
        "--references", type=str, help="Comma-separated paths to reference files."
    )
    parser.add_argument(
        "--references-persist",
        type=str,
        help="Comma-separated paths to persistent reference files.",
    )
    parser.add_argument(
        "--artifacts", type=str, help="Comma-separated paths to artifact files."
    )
    parser.add_argument("--procedure", type=str, help="Path to the procedure file.")
    parser.add_argument(
        "--multi-step-reasoning",
        action="store_true",
        help="Include multi-step reasoning process in the prompt.",
    )
    parser.add_argument(
        "--fork", type=str, metavar="SESSION_ID", help="The ID of the session to fork."
    )
    parser.add_argument(
        "--at-turn",
        type=int,
        metavar="TURN_INDEX",
        help="The 1-based turn number to fork from. Required with --fork.",
    )
    parser.add_argument(
        "--api-mode",
        type=str,
        help="Specify the API mode (e.g., gemini-api, gemini-cli).",
    )

    args = parser.parse_args()
    return args, parser


def main():
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    if not check_and_show_warning(project_root):
        sys.exit(1)

    load_dotenv()
    config_path = os.path.join(project_root, "setting.yml")
    if not os.path.exists(config_path):
        config_path = os.path.join(project_root, "setting.default.yml")

    settings_dict = read_yaml_file(config_path)
    settings = Settings(**settings_dict)

    parsed_args, parser = _parse_arguments()
    args = TaktArgs.from_parsed_args(parsed_args)

    if args.api_mode:
        settings.api_mode = args.api_mode

    session_service = ServiceFactory(project_root, settings).create_session_service()

    try:
        # Validate arguments for a new session at the endpoint
        if not args.session and args.instruction:
            start_session_validator.validate(args.purpose, args.background)

        dispatch(args, session_service, parser)
    except (ValueError, FileNotFoundError, IndexError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
