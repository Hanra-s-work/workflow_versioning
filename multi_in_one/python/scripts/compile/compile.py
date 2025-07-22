"""
    File in charge of compiling the program into a standalone executable.
"""

import os
import sys
import inspect
import platform
from typing import Literal, Union, List, Dict

from pathlib import Path
from ask_question import Ask_Question

HELP_ARGUMENTS: List[str] = ["h", "help", "?"]
BIN_NAME_ARGUMENTS: List[str] = ["name", "bin-name", "binary-name"]
SOURCE_DIRECTORY_ARGUMENTS: List[str] = ["src", "source-directory"]
SOURCE_FILE_ARGUMENTS: List[str] = ["srcf", "source-file"]
LOG_LEVEL_ARGUMENTS: List[str] = ["log", "log-level", "level"]
BUILD_LOCATION_ARGUMENTS: List[str] = ["build", "build-location"]
DIST_LOCATION_ARGUMENTS: List[str] = ["dist", "dist-location"]
BINARY_DEST_ONE_ARGUMENTS: List[str] = [
    "binary1", "binary-destination", "binary-destination1"
]
BINARY_DEST_TWO_ARGUMENTS: List[str] = [
    "binary2", "binary-destination2"
]
SINGLE_FILE_BINARY: List[str] = [
    "single", "single-binary", "onefile", "one-file"
]
LOG_LEVEL_TYPE = Literal[
    'TRACE', 'DEBUG', 'INFO', 'WARN', 'DEPRECATION', 'ERROR', 'FATAL'
]
AVAILABLE_LOG_LEVELS: List[str] = [
    'TRACE', 'DEBUG', 'INFO', 'WARN', 'DEPRECATION', 'ERROR', 'FATAL'
]


class Compile:
    """
    Class to handle the compilation of the program.
    """

    def __init__(self, debug: bool = True):
        self.argv: List[str] = sys.argv
        self.argc: int = len(self.argv)
        self.cwd = os.getcwd()
        self.debug = debug
        self.error = 1
        self.success = 0
        self.bin_name = "executable"
        self.source_directory = os.path.join(self.cwd, "src")
        self.source_file = os.path.join(self.source_directory, "__main__.py")
        self.log_level: str = "WARN"
        self.build_location: Union[str, None] = None
        self.dist_location: Union[str, None] = None
        self.binary_destination_one: Union[str, None] = None
        self.binary_destination_two: Union[str, None] = None
        self.single_file: bool = False
        self.confirm_replacement: bool = True
        self.compiler_binary: str = "pyinstaller"
        self.on_windows: bool = False
        if platform.system().lower() == "windows":
            self.on_windows = True
        self.ask_user_for_args: bool = True
        self.help_found: bool = False
        self.aqi: Ask_Question = Ask_Question(tui=False, allow_blank=True)
        self.questions: Dict[str, str] = {
            "Please enter the name of your binary: ": "str",
            "Please enter the path to the folder to compile: ": "str",
            "Please enter the name of the entrypoint file: ": "str",
            "Please enter the logging level of the program (TRACE, DEBUG, INFO, WARN, DEPRECATION, ERROR, FATAL): ": "str",
            "Please enter the build directory: ": "str",
            "Please enter the distribution directory: ": "str",
            "Please enter the first binary destination path: ": "str",
            "Please enter the second binary destination path: ": "str",
            "Build as a single file executable? (yes/no): ": "bool"
        }

    def print_debug(self, string: str) -> None:
        """_summary_
            Display the debug string only if self.debug is true.

        Args:
            string (str): _description_
        """
        if self.debug:
            func_name = inspect.currentframe()
            if hasattr(func_name, "f_back") and func_name.f_back is None:
                func_name = func_name.f_code.co_name
            else:
                func_name = func_name.f_back.f_code.co_name
            print(f"DEBUG: <{func_name}> {string}")

    def bool_to_human(self, status: bool = True) -> str:
        """_summary_

        Args:
            status (bool, optional): _description_. Defaults to True.

        Returns:
            str: _description_: Returns Yes if True, False otherwise.
        """
        if status:
            response = "Yes"
        else:
            response = "No"
        self.print_debug(f"status: {status}, response: {response}")
        return response

    def is_path_correct(self, path: str) -> bool:
        """
        Check if the given path string is valid on the target platform (default: current platform).
        Does not check for existence.
        """
        if not path or path.isspace():
            return False
        if '\x00' in path:
            return False
        try:
            p = Path(path)
            del p
            if platform.system().lower().startswith('win'):
                invalid_chars = r'<>:"/\\|?*'
                reserved_names = {
                    "CON", "PRN", "AUX", "NUL",
                    *(f"COM{i}" for i in range(1, 10)),
                    *(f"LPT{i}" for i in range(1, 10)),
                }
                basename = Path(path).name.upper().split('.')[0]
                if basename in reserved_names:
                    return False
                if any(c in path for c in invalid_chars):
                    return False
                if len(path) > 260:
                    return False
            else:
                if '/' in Path(path).name:
                    return False
                if any(len(part) > 255 for part in Path(path).parts):
                    return False
            return True
        except Exception:
            return False

    def is_pyinstaller_present(self) -> bool:
        """ Check if pyinstaller is present on the system """
        redirect = ">/dev/null 2>&1"
        if self.on_windows:
            redirect = ">nul"
        status = os.system(f"{self.compiler_binary} --version {redirect}")
        self.print_debug(f"redirect: {redirect}, status: {status}")
        if status != 0:
            return False
        return True

    def get_bin_name_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the user specified binary name.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        name = ""
        if "=" in self.argv[index]:
            name = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            name = self.argv[index+1]
        else:
            print("Binary name not found in the argument")
            return self.error
        self.print_debug(f"name: {name}")
        if len(name) == 0:
            print(
                f"No binary name provided, using default name '{self.bin_name}'")
        else:
            self.bin_name = name
        self.print_debug(f"self.bin_name = {self.bin_name}")
        return self.success

    def get_source_directory_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the user specified source directory path.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        source_directory = ""
        if "=" in self.argv[index]:
            source_directory = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            source_directory = self.argv[index+1]
        else:
            print("source directory not found in the argument")
            return self.error
        self.print_debug(f"source_directory: {source_directory}")
        if len(source_directory) == 0:
            print(
                f"No source directory provided, using default path '{self.source_directory}'")
        else:
            self.source_directory = source_directory
        self.print_debug(f"self.source_directory: {self.source_directory}")
        return self.success

    def get_source_file_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the user specified source file path.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        source_file = ""
        if "=" in self.argv[index]:
            source_file = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            source_file = self.argv[index+1]
        else:
            print("source file not found in the argument")
            return self.error
        self.print_debug(f"source_file: {source_file}")
        if len(source_file) == 0:
            print(
                f"No source file provided, using default path '{self.source_directory}'")
        else:
            self.source_file = source_file
        self.print_debug(f"self.source_file: {self.source_file}")
        return self.success

    def get_log_level_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the user log level of the compiler.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        log_level = ""
        if "=" in self.argv[index]:
            log_level = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            log_level = self.argv[index+1]
        else:
            print("source file not found in the argument")
            return self.error
        self.print_debug(f"log_level: {log_level}")
        if len(log_level) == 0:
            print(
                f"No source file provided, using default path '{self.source_directory}'")
        else:
            log_level = log_level.upper()
            if log_level in AVAILABLE_LOG_LEVELS:
                self.log_level = log_level
            else:
                print(
                    f"Log level not found in the level options: {", ".join(LOG_LEVEL_ARGUMENTS)}"
                )
            self.print_debug(f"self.log_level: {self.log_level}")
        return self.success

    def get_build_location_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the build location of the compiler.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        build_location = ""
        if "=" in self.argv[index]:
            build_location = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            build_location = self.argv[index+1]
        else:
            print("source file not found in the argument")
            return self.error
        self.print_debug(f"build_location: {build_location}")
        if len(build_location) == 0:
            print(
                f"No source file provided, using default path '{self.source_directory}'")
        else:
            self.build_location = build_location
        self.print_debug(f"self.build_location: {self.build_location}")
        return self.success

    def get_dist_location_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the dist location of the compiler.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        dist_location = ""
        if "=" in self.argv[index]:
            dist_location = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            dist_location = self.argv[index+1]
        else:
            print("source file not found in the argument")
            return self.error
        self.print_debug(f"dist_location: {dist_location}")
        if len(dist_location) == 0:
            print(
                f"No source file provided, using default path '{self.source_directory}'")
        else:
            self.dist_location = dist_location
        self.print_debug(f"self.dist_location: {self.dist_location}")
        return self.success

    def get_bin_dest_one_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the binary destination one of the compiler.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        binary_destination_one = ""
        if "=" in self.argv[index]:
            binary_destination_one = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            binary_destination_one = self.argv[index+1]
        else:
            print("source file not found in the argument")
            return self.error
        self.print_debug(f"binary_destination_one: {binary_destination_one}")
        if len(binary_destination_one) == 0:
            print(
                f"No source file provided, using default path '{self.source_directory}'")
        else:
            self.binary_destination_one = binary_destination_one
        self.print_debug(
            f"self.binary_destination_one: {self.binary_destination_one}")
        return self.success

    def get_bin_dest_two_from_arg(self, index: int) -> int:
        """ Function in charge of gathering the binary destination two of the compiler.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        binary_destination_two = ""
        if "=" in self.argv[index]:
            binary_destination_two = self.argv[index].split("=")[-1]
        elif index < self.argc - 1 and self.argv[index+1][0] not in ("-", "/"):
            binary_destination_two = self.argv[index+1]
        else:
            print("source file not found in the argument")
            return self.error
        self.print_debug(f"binary_destination_two: {binary_destination_two}")
        if len(binary_destination_two) == 0:
            print(
                f"No source file provided, using default path '{self.source_directory}'")
        else:
            self.binary_destination_two = binary_destination_two
        self.print_debug(
            f"self.binary_destination_two: {self.binary_destination_two}"
        )
        return self.success

    def get_onefile_from_arg(self, index: int) -> int:
        """ Function in charge of gathering if they need to create the binary as a single file.

        Args:
            index (int): _description_

        Returns:
            int: _description_
        """
        if index < self.argc:
            return self.error
        self.single_file = not self.single_file
        self.print_debug(f"self.single_file: {self.single_file}")
        return self.success

    def process_workpath(self) -> str:
        """ Function in charge of checking if the location of the compilation path (where generation data is stored) is to be the default or a user defines one """
        if self.build_location is None:
            self.build_location = os.path.join(self.cwd, "build")
        final = f"--workpath \"{self.build_location}\""
        self.print_debug(f"workpath: {final}")
        return final

    def process_distribution_path(self) -> str:
        """ Function in charge of checking if the location of the distribution path (where the final build will be located) is to be the default or a user defined one """
        if self.dist_location is None:
            self.dist_location = os.path.join(self.cwd, "dist")
        final = f"--distpath \"{self.dist_location}\""
        self.print_debug(f"distpath: {final}")
        return final

    def process_onefile(self) -> str:
        """ Function in charge of checking if the binary should be compiled as a single file or not """
        onefile = ""
        if self.single_file:
            onefile = "--onefile"
        self.print_debug(f"onefile: {onefile}")
        return onefile

    def process_no_confirm(self) -> str:
        """ Function in charge of checking if the binary should be compiled as a single file or not """
        no_confirm = ""
        if self.single_file:
            no_confirm = "--noconfirm"
        self.print_debug(f"no_confirm: {no_confirm}")
        return no_confirm

    def process_name(self) -> str:
        """ Function in charge of formating the name in a way that pyinstaller will understand """
        bin_name = f"--name \"{self.bin_name}\""
        self.print_debug(f"bin_name = {bin_name}")
        return bin_name

    def process_log_level(self) -> str:
        """ Function in charge of setting the logging level for the program """
        log_level = "--log-level \""
        self.print_debug(f"self.log_level = {self.log_level}")
        if self.log_level.upper() in LOG_LEVEL_ARGUMENTS:
            log_level += self.log_level.upper()
        else:
            log_level += "WARN"
        log_level += "\""
        self.print_debug(f"log_level: {log_level}")
        return log_level

    def process_confirm(self) -> str:
        """ Function in charge of confirming that we wish to replace the binary if that already exists """
        final = ""
        if self.confirm_replacement:
            final = "-y"
        self.print_debug(f"process_confirm: {final}")
        return final

    def commpile(self) -> int:
        """ Compile the program into an executable """
        if self.is_pyinstaller_present() is False:
            return self.error
        compilation_line = []
        compilation_line.append(self.compiler_binary)
        compilation_line.append(f"\"{self.source_file}\"")
        compilation_line.append(self.process_workpath())
        compilation_line.append(self.process_distribution_path())
        compilation_line.append(self.process_onefile())
        compilation_line.append(self.process_no_confirm())
        compilation_line.append(self.process_name())
        compilation_line.append(self.process_log_level())
        compilation_line.append(self.process_confirm())
        final_command = " ".join(compilation_line)
        self.print_debug(f"final command: {final_command}")
        status = os.system(final_command)
        self.print_debug(f"status: {status}")
        return status

    def display_help(self) -> None:
        """
            Function in charge of displaying the help for the arguments that are available for the program
        """
        print(f"Usage: python {sys.argv[0]} [options]")
        print("\nOptions:")
        print("  -h, --help, -? \t\t\t\tShow this help message and exit")
        print("  --name, --bin-name, --binary-name <name>", end="")
        print(
            f" \t\t\t\tSet the name of the output binary (default: {self.bin_name})"
        )
        print("  --src, --source-directory <dir>", end="")
        print(
            f" \t\t\t\tSet the source directory (default: {self.source_directory})"
        )
        print("  --srcf, --source-file <file>", end="")
        print(f" \t\t\t\tSet the source file (default: {self.source_file})")
        print("  --log, --log-level, --level <level>", end="")
        print(
            f" \t\t\t\tSet log level ({AVAILABLE_LOG_LEVELS}; default: {self.log_level})"
        )
        print("  --build, --build-location <dir>", end="")
        print(f" \t\t\t\tSet build directory (default: {self.cwd}/build)")
        print("  --dist, --dist-location <dir>", end="")
        print(
            f" \t\t\t\tSet distribution directory (default: {self.cwd}/dist)")
        print("  --binary1, --binary-destination, --binary-destination1 <path>", end="")
        print(" \t\t\t\tSet first binary destination path (default: None)")
        print("  --binary2, --binary-destination2 <path>", end="")
        print(" \t\t\t\tSet second binary destination path (default: None)")
        print("  --single, --single-binary, --onefile, --one-file", end="")
        tmp = self.bool_to_human(self.single_file)
        print(f" \t\t\t\tBuild as a single file executable (default: {tmp})")

    def clean_arg(self, arg: str) -> str:
        """Function in charge of removing elements from the beginning argument so that it is quicker to process

        Args:
            arg (str): _description_

        Returns:
            str: _description_
        """
        if arg[0] == "-":
            arg = arg[1:]
        if arg[0] == "-":
            arg = arg[1:]
        if arg[0] == "/":
            arg = arg[1:]
        if "=" in arg:
            arg = arg.split("=")[0]
        self.print_debug(f"arg_cleaned: {arg}")
        return arg

    def check_args(self) -> int:
        """ Check the user arguments to see if they correspond.

        Returns:
            int: _description_
        """
        if self.argc == 1 and not self.ask_user_for_args:
            self.ask_user_for_args = True
        else:
            i = 1
            while i < self.argc:
                status = self.success
                arg = self.clean_arg(self.argv[i].lower())
                if arg in HELP_ARGUMENTS:
                    self.display_help()
                    return self.success
                if arg in BIN_NAME_ARGUMENTS:
                    status = self.get_bin_name_from_arg(i)
                elif arg in SOURCE_DIRECTORY_ARGUMENTS:
                    status = self.get_source_directory_from_arg(i)
                elif arg in SOURCE_FILE_ARGUMENTS:
                    status = self.get_source_file_from_arg(i)
                elif arg in LOG_LEVEL_ARGUMENTS:
                    status = self.get_log_level_from_arg(i)
                elif arg in BUILD_LOCATION_ARGUMENTS:
                    status = self.get_build_location_from_arg(i)
                elif arg in DIST_LOCATION_ARGUMENTS:
                    status = self.get_dist_location_from_arg(i)
                elif arg in BINARY_DEST_ONE_ARGUMENTS:
                    status = self.get_bin_dest_one_from_arg(i)
                elif arg in BINARY_DEST_TWO_ARGUMENTS:
                    status = self.get_bin_dest_two_from_arg(i)
                elif arg in SINGLE_FILE_BINARY:
                    status = self.get_onefile_from_arg(i)
                else:
                    print(
                        f"Argument : '{arg}' not found in the available options."
                    )
                    return self.error
                if status != self.success:
                    return status
                i += 1
        self.print_debug(f"self.ask_user_fo_args: {self.ask_user_for_args}")

        return self.success

    def get_user_for_args(self) -> int:
        """ Because launch arguments where not provided, we will ask the user for them

        Returns:
            int: _description_
        """
        index = 0
        for question, question_type in self.questions.items():
            index += 1
            self.print_debug(
                f"question: '{question}', question_type: '{question_type}'"
            )
            if index == 1:
                e = self.aqi.ask_question(
                    f"{question} (default: {self.bin_name}) ", question_type)
                self.print_debug(f"e='{e}', self.bin_name={self.bin_name}")
                if isinstance(e, str) and e != "":
                    self.bin_name = e
                self.print_debug(f"e='{e}', self.bin_name={self.bin_name}")
            elif index == 2:
                dd = ""
                path_exists = False
                while path_exists is False:
                    dd = str(self.aqi.ask_question(
                        f"{question} (default: {self.source_directory}) ", question_type
                    ))
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.source_directory
                        continue
                    path_exists = os.path.exists(dd)
                    if path_exists is False:
                        print("Please enter a valid directory path.")
                self.source_directory = dd
                self.print_debug(
                    f"dd: '{dd}', self.source_directory: {self.source_directory}"
                )
            elif index == 3:
                dd = ""
                path_exists = False
                while path_exists is False:
                    dd = str(self.aqi.ask_question(
                        f"{question} (default: {self.source_file})", question_type
                    ))
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.source_file
                        continue
                    path_exists = os.path.exists(dd)
                    if path_exists is False:
                        print("Please enter a valid directory path.")
                self.source_file = dd
                self.print_debug(
                    f"dd: '{dd}', self.source_file: {self.source_file}"
                )
            elif index == 4:
                dd = ""
                path_exists = False
                while dd not in AVAILABLE_LOG_LEVELS:
                    dd = str(self.aqi.ask_question(
                        f"{question} (default: {self.log_level}) ", question_type
                    )).upper()
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.log_level
                        continue
                    if dd not in AVAILABLE_LOG_LEVELS:
                        print(
                            f"Please enter a log level present in {", ".join(AVAILABLE_LOG_LEVELS)}"
                        )
                self.log_level = dd
                self.print_debug(
                    f"dd: '{dd}', self.log_level: {self.log_level}"
                )
            elif index == 5:
                dd = ""
                path_exists = False
                while path_exists is False:
                    dd = str(self.aqi.ask_question(
                        f"{question} (default: ./build) ", question_type
                    ))
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.build_location
                        continue
                    path_exists = self.is_path_correct(str(dd))
                    if path_exists is False:
                        print("Please enter a valid directory path.")
                self.build_location = dd
                self.print_debug(
                    f"dd: '{dd}', self.build_location: {self.build_location}"
                )
            elif index == 6:
                dd = ""
                path_exists = False
                while path_exists is False:
                    dd = str(self.aqi.ask_question(
                        f"{question} (default: ./dist) ", question_type
                    ))
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.dist_location
                        continue
                    path_exists = self.is_path_correct(dd)
                    if path_exists is False:
                        print("Please enter a valid directory path.")
                self.dist_location = dd
                self.print_debug(
                    f"dd: '{dd}', self.dist_location: {self.dist_location}"
                )
            elif index == 7:
                dd = ""
                path_exists = False
                while path_exists is False:
                    dd = str(self.aqi.ask_question(
                        f"{question} (default: None) ", question_type)
                    )
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.binary_destination_one
                        continue
                    path_exists = self.is_path_correct(dd)
                    if path_exists is False:
                        print("Please enter a valid directory path.")
                self.binary_destination_one = dd
                self.print_debug(
                    f"dd: '{dd}', self.binary_destination_one: {self.binary_destination_one}"
                )
            elif index == 8:
                dd = ""
                path_exists = False
                while path_exists is False:
                    dd = self.aqi.ask_question(
                        f"{question} (default: None) ", question_type
                    )
                    self.print_debug(f"dd: '{dd}'")
                    if dd == "":
                        path_exists = True
                        dd = self.binary_destination_two
                        continue
                    path_exists = self.is_path_correct(str(dd))
                    if path_exists is False:
                        print("Please enter a valid directory path.")
                self.binary_destination_two = str(dd)
                self.print_debug(
                    f"dd: '{dd}', self.binary_destination_two: {self.binary_destination_two}"
                )
            elif index == 9:
                tmp = self.bool_to_human(self.single_file)
                e = self.aqi.ask_question(
                    f"{question} (default: {tmp}) ", question_type
                )
                self.print_debug(f"e: {e}")
                if isinstance(e, bool):
                    self.single_file = e
            else:
                print(
                    f"Option {question} of type {question_type} not supported."
                )
        return self.success

    def run(self):
        """
        Run the compilation process.
        """
        if self.argc == 0:
            print("No arguments are provided, using default options")
        status: int = self.check_args()
        if status != self.success:
            return status
        if self.help_found is True:
            return self.success
        if self.ask_user_for_args is True:
            status = self.get_user_for_args()
            if status != self.success:
                return status
        return self.commpile()
