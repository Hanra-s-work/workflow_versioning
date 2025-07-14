##
# EPITECH PROJECT, 2022
# Desktop_pet (Workspace)
# File description:
# ask_question.py
##

"""
The file containing the code to speed up the boiling
process that occurs when a question is asked.
This module is provided as if and without any warranty
Crediting the author is appreciated.
"""

__Version__ = "1.2.0"
__Author__ = "(c) Henry Letellier"

from string import printable
from typing import Union, Dict


class AskQuestion:
    """ An advanced function that contains boiling to gain time when asking a question """

    def __init__(self, human_type: Dict = {}, illegal_characters_nb: str = "") -> None:
        """ The globals for the class """
        self.__version__ = "1.2.0"
        self.human_type = human_type
        self.illegal_characters_nb = illegal_characters_nb
        self.author = "(c) Henry Letellier"
        self.version = self.__version__
        self.usr_answer = ""
        self.answer_was_found = True
        self.answer_was_not_found = False
        self.check_load()

    def check_load(self) -> None:
        """ Check that the ressources are present """
        if isinstance(self.human_type, dict) is False:
            self.human_type = {
                "int": "whole number (-1, 0, 1, 2, 3, etc...)",
                "float": "floating number (-1.2, 0.1, 1.2, etc...)",
                "uint": "whole positive number (0, 1, 2, etc...)",
                "ufloat": "whole positive floating number (0.1, 1.2, etc ...)",
                "num": "numeric (numbers from 0 onwards)",
                "alnum": "alphanumeric (only numbers and the alphabet)",
                "isalpha": "alphabet (from a to z and A to Z)",
                "char": "alphabet (from a to z and A to Z)",
                "ascii": "ascii Table",
                "str": "string (any character you can type)",
                "version": "version (numbers separated by '.' characters)",
                "ver": "version (numbers separated by '.' characters)",
                "bool": "boolean (yes/True/1 or no/False/0 answer type)",
            }
        if self.illegal_characters_nb == "":
            self.illegal_characters_nb = printable.replace("-", "")
            self.illegal_characters_nb = self.illegal_characters_nb.replace(
                ".",
                ""
            )
            self.illegal_characters_nb = self.illegal_characters_nb.replace(
                ",",
                ""
            )
            self.illegal_characters_nb = self.illegal_characters_nb.replace(
                "+",
                ""
            )
            self.illegal_characters_nb = self.illegal_characters_nb.replace(
                "0123456789",
                ""
            )

    def is_empty(self, string: str) -> bool:
        """ Check if the string is not empty """
        if len(string) == 0:
            return True
        return False

    def is_version(self, string: str) -> bool:
        """ Check if the given string is a version """
        string_length = len(string)-1
        for i in enumerate(string):
            if i[1].isdigit() is False:
                if i[0] == string_length and (i[1] == '.' or i[1] == ','):
                    return False
                if i[1] != "." and i[1] != ",":
                    return False
        return True

    def is_float(self, number: str) -> bool:
        """ Check if the given string is a float """
        try:
            float(number)
            return True
        except ValueError:
            return False

    def contains_illegal_characters(self, string: str, illegal_characters: str) -> bool:
        """ Check if there are no forbidden characters in a string destined to be converted to a number """
        for i in string:
            if i in illegal_characters:
                return True
        return False

    def remove_char_overflow(self, string: str, char: str, presence_tolerance: int = 1, case_sensitive: bool = False) -> str:
        """ Remove the number of times a specific character appears in a string after the allowed number of times """
        result = ""
        for i in string:
            if case_sensitive is False:
                if i.lower() == char:
                    if presence_tolerance > 0:
                        result += i
                        presence_tolerance -= 1
                else:
                    result += i
            else:
                if i == char:
                    if presence_tolerance > 0:
                        result += i
                        presence_tolerance -= 1
                else:
                    result += i
        return result

    def clean_number(self, string: str, char: str = ".", tolerance: int = 1, case_sensitive: bool = False) -> str:
        """ Remove content that should not be in a number input """
        if " " in string:
            string = string.replace(" ", "")
        if "," in string:
            string = string.replace(",", ".")
        if string.count(char) > tolerance:
            string = self.remove_char_overflow(
                string, char, tolerance, case_sensitive)
        return string

    def test_input(self, input_answer: str, answer_type: str) -> Union[str, int, float, bool]:
        """ The function in charge of ensuring that the user's response corresponds to the programmer's expectations """
        if self.is_empty(input_answer) is False and input_answer.isspace() is False and input_answer.isprintable() is True:
            contains_illegal_characters = self.contains_illegal_characters(
                input_answer,
                self.illegal_characters_nb
            )
            if input_answer.isalnum() is True and "alnum" in answer_type:
                self.usr_answer = input_answer
                return self.answer_was_found
            if input_answer.isalpha() is True and "char" in answer_type:
                self.usr_answer = input_answer
                return self.answer_was_found
            if input_answer.isdigit() is True and "num" in answer_type:
                self.usr_answer = float(input_answer)
                return self.answer_was_found
            if input_answer.isascii() is True and ("ascii" in answer_type or "str" in answer_type):
                self.usr_answer = input_answer
                return self.answer_was_found
            if "up" in answer_type:
                self.usr_answer = input_answer.upper()
                return self.answer_was_found
            if "low" in answer_type or "down" in answer_type:
                self.usr_answer = input_answer.lower()
                return self.answer_was_found
            if "version" in answer_type or "ver" in answer_type and self.is_version(input_answer) is True:
                self.usr_answer = input_answer
                return self.answer_was_found
            if "uint" in answer_type and input_answer.isdigit() is True:
                self.usr_answer = int(self.clean_number(
                    input_answer, ".", 0, False))
                return self.answer_was_found
            if "ufloat" in answer_type and contains_illegal_characters is False:
                if input_answer[0] == "-":
                    self.usr_answer = ""
                    return self.answer_was_not_found
                self.usr_answer = float(
                    self.clean_number(input_answer, ".", 1, False)
                )
                return self.answer_was_found
            if "bool" in answer_type:
                answer_l = input_answer.lower()
                if "y" in answer_l or "t" in answer_l or "1" in answer_l:
                    self.usr_answer = True
                    return self.answer_was_found
                if "n" in answer_l or "f" in answer_l or "0" in answer_l:
                    self.usr_answer = False
                    return self.answer_was_found
                self.usr_answer = None
                return self.answer_was_not_found
            if "int" in answer_type and "uint" not in answer_type and contains_illegal_characters is False:
                input_answer = self.clean_number(input_answer, ".", 0, False)
                input_answer = self.remove_char_overflow(
                    input_answer, "-", 1, False)
                try:
                    self.usr_answer = int(input_answer)
                    return self.answer_was_found
                except TypeError:
                    self.usr_answer = ""
                    return self.answer_was_not_found
                except BaseException:
                    self.usr_answer = ""
                    return self.answer_was_not_found
            if "float" in answer_type and "ufloat" not in answer_type and contains_illegal_characters is False:
                input_answer = self.clean_number(input_answer, ".", 1, False)
                input_answer = self.remove_char_overflow(
                    input_answer,
                    "-",
                    1,
                    False
                )
                try:
                    self.usr_answer = float(input_answer)
                    return self.answer_was_found
                except TypeError:
                    self.usr_answer = ""
                    return self.answer_was_not_found
                except BaseException:
                    self.usr_answer = input_answer
                    return self.answer_was_not_found
            res = "Please enter a response of type '"
            res += f"{self.human_type[answer_type]}'"
            print(res)
            self.usr_answer = ""
            return self.answer_was_not_found
        print(
            "Response must not be empty or only contain spaces or any non visible character."
        )
        self.usr_answer = ""
        return self.answer_was_not_found

    def ask_question(self, question: str, answer_type: str) -> Union[str, int, float, bool]:
        """ Ask a question and continue asking until type met """
        answer_found = False
        usr_answer = ""
        self.usr_answer = ""
        while answer_found is False:
            usr_answer = input(str(question))
            answer_found = self.test_input(usr_answer, answer_type)
        return self.usr_answer

    def pause(self, pause_message: str = "Press enter to continue...") -> None:
        """ Act like the windows batch pause function """
        empty = ""
        pause_response = input(pause_message)
        empty += pause_response


if __name__ == "__main__":
    AQI = AskQuestion({}, "")
    answer = AQI.ask_question("How old are you?", "uint")
    ADD_S = ""
    if isinstance(answer, int) and answer > 1:
        ADD_S = "s"
    print(f"You are {answer} year{ADD_S} old")
    answer = AQI.ask_question("Enter a ufloat:", "ufloat")
    print(f"You entered {answer}")
    AQI.pause()
