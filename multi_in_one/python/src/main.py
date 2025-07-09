"""
    File in charge of containing the entry point of the program.
"""

from display_tty import IDISP


def main() -> int:
    """Main function to execute the script."""
    IDISP.log_info("This is the main function in src/main.py")
    return 0
