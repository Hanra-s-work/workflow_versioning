"""
    File in charge of containing the errors that can be raised by the program
"""


class MyBaseError(Exception):
    """
        Class in charge of defining the default error that can simplify the already simple process of raising errors.
    """

    def __init__(self, message: str = "", class_name: str = "") -> None:
        """ This is the base class that I have created

        Args:
            message (str, optional): The message to display to the user. Defaults to "".
            class_name (str, optional): The name of the class to be displayed in the error. Defaults to "".

        Returns:
            None
        """
        if isinstance(class_name, str) and len(class_name) > 0:
            self.class_name: str = class_name
        else:
            self.class_name: str = self.__class__.__name__
        self.message: str = f"({self.class_name}): {message}"
        super().__init__(self.message)

    def __str__(self) -> str:
        """
            Function used to return the description of the exception

            Args:
                None

            Returns:
                str: The concatenated version of the error for the user.
        """
        return self.message


class ProcessNotFound(MyBaseError):
    """
        This is the class that is in charge of raising an error when a process was attempted to be altered but does not exist anymore.
    """

    def __init__(self, message: str = "The process you have attempted to use could not be found in the list.", class_name: str = "") -> None:
        super().__init__(message, class_name)
