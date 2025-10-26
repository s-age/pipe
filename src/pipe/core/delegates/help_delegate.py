"""
Delegate for handling the 'help' command.
"""
import argparse

def run(parser: argparse.ArgumentParser):
    """Prints the help message."""
    parser.print_help()
