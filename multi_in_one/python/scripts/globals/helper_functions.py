"""
    File in charge of containing general functions that can be used to handle elements like debug mode
"""

import os


class HelperFunctions:
    """
    Helper functions for various tasks.
    """

    def __init__(self, success: int = 0, error: int = 1):
        """
        Initialize the HelperFunctions class.
        """
        self.success = success
        self.error = error

    @staticmethod
    def run_command(command: str) -> int:
        """
        @brief Run a command in the terminal.
        @param command: The command to run.
        @return: The return code of the command.
        """
        return os.system(command)

    @staticmethod
    def prompt(text: str = "Please enter a command: ") -> str:
        """
        @brief Prompt the user for input.
        @return: The user input.
        """
        return input(text)
