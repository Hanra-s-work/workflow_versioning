##
# EPITECH PROJECT, 2024
# workflow_versioning (Workspace)
# File description:
# hl_hello_world.py
##


"""
The file containing the code for a perfect hello world library.
"""


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
