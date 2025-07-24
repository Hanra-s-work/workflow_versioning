"""
    File in charge of containing python classes that act like c structures while using the python revisited dictionnary logic.
"""

from typing import Any, Dict

from display_tty import LoggerColours

try:
    from .flexible_dictionary import FlexibleDictionary
except ImportError:
    try:
        from flexible_dictionary import FlexibleDictionary
    except ImportError as e:
        raise RuntimeError("Failed to import FlexibleDictionary.") from e


class CustomLogLevels(FlexibleDictionary[str, Any]):
    """
    This is a class in charge of containing the codes for the custom levels

    Args:
        FlexibleDictionary (_type_): _description_
    """
    # These are the keys for the Dictionary so that the custom level definitions can be injected automatically
    level_key: str = "level"
    name_key: str = "name"
    foreground_colour_key: str = "fg"
    background_colour_key: str = "bg"
    # The id for the custom level to allow you to access
    log_success: int = 2
    # This is the dictionary that will contain the actual configuration for your level
    level_details: Dict = {
        log_success: {
            level_key: log_success,
            name_key: "success",
            foreground_colour_key: LoggerColours.BOLD_LIGHT_GREEN,
            background_colour_key: LoggerColours.BLACK
        }
    }
