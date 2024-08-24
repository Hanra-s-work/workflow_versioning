##
# EPITECH PROJECT, 2022
# Desktop_pet (Workspace)
# File description:
# colourise_output.py
##

"""
The file containing the code in charge of outputting
coloured text into the terminal.
This class follows the batch colour coding rules (from 0 to F for foreground and background)
"""

from typing import TextIO, Union
import os
import sys
import platform
try:
    import colorama as COC
except ImportError as e:
    msg = "Fatal Error (Colourise Output):"
    msg += "Failed to load Colorama, core dependency for Colourise Output."
    msg += " Aborting.\nImport error msg:"
    raise RuntimeError(msg) from e

ALL = "*"
BOLD = "bold"
DIM = "dim"
ITALIC = "italic"
UNDERLINE = "underline"
BLINK = "blink"
INVERT = "invert"
CONCEALED = "concealed"
STRIKE = "strike"


class HLHelloWorld:
    """
    The class in charge of displaying a hello world.
    """

    def __init__(self, hello_world: str = "Hello World !") -> None:
        self.__version__ = "1.0.0"
        self.author = "Henry Letellier"
        self.hello_world = hello_world

    def hw_string(self) -> str:
        """_summary_
            This is a function that will return the hello world string.
        """
        return self.hello_world

    def hw_print(self) -> None:
        """_summary_
            This is a function that will print the hello world string.
        """
        print(self.hw_string())

    def is_hello_world(self, string: str) -> bool:
        """_summary_
            This is a function that will return true if the string is hello world.

        Args:
            string (str): _description_: The string you wish to compare

        Returns:
            bool: _description_: The response, True if it is the case.
        """
        return string in (self.hello_world, f"{self.hello_world}\n")

    def test(self) -> None:
        """_summary_
            This is a function that will allow you to test if the hello-world class works.
        """
        print(self.hw_string())


if __name__ == '__main__':
    HWI = HLHelloWorld()
    HWI.test()
    print(f"Created by {HWI.author}")
