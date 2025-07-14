"""
    File containing the code for initializing the basic functions and elements that are used throughout the program.
"""

import os
from .display_tty import Disp, TOML_CONF
from . import constants as const
from .helper_functions import HelperFunctions


class Globals:
    """
        Class in charge of containing the globals that are used throughout the program.
    """

    def __init__(self):
        self.debug_mode = False  # Debug mode is disabled by default
        self.debug_mode_env = os.getenv("DEBUG_MODE", "False").lower(
        ) == "true"  # Check environment variable for debug mode
        # Set debug mode based on environment variable
        self.debug_mode = self.debug_mode or self.debug_mode_env
        self.hf: HelperFunctions = HelperFunctions(
            const.SUCCESS, const.ERROR)  # Initialize helper functions
        self.disp: Disp = Disp(
            toml_content=TOML_CONF,
            save_to_file=False,
            file_name="text_output_run.txt",
            file_descriptor=None,
            debug=False,
            logger=None,
            success=const.SUCCESS,
            error=const.ERROR,
            log_warning_when_present=False,
            log_errors_when_present=True
        )
