#!/usr/bin/env python3
"""
Script to execute git commit with a message
"""

import argparse
import subprocess
import sys


def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Execute a command and return the result"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr}", file=sys.stderr)
        raise


def check_git_status() -> tuple[bool, str]:
    """Check git status for changes"""
    result = run_command(["git", "status", "--porcelain"])
    has_changes = bool(result.stdout.strip())
    return has_changes, result.stdout


def git_add_all() -> None:
    """Stage all changes"""
    run_command(["git", "add", "."])
    print("All changes staged.")


def git_commit(message: str) -> None:
    """Execute git commit"""
    run_command(["git", "commit", "-m", message])
    print(f"Committed: {message}")


def main():
    """Main process"""
    parser = argparse.ArgumentParser(description="Execute git commit with a message")
    parser.add_argument(
        "-m",
        "--message",
        required=True,
        help="Commit message",
    )
    parser.add_argument(
        "--no-add",
        action="store_true",
        help="Skip git add (only commit already staged changes)",
    )

    args = parser.parse_args()

    # Check git status
    has_changes, status = check_git_status()
    if not has_changes and not args.no_add:
        print("No changes to commit.", file=sys.stderr)
        sys.exit(1)

    # Execute git add (unless --no-add is specified)
    if not args.no_add:
        git_add_all()

    # Execute commit
    try:
        git_commit(args.message)
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    main()
