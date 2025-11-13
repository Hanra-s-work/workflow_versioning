""" 
# +==== BEGIN AsperHeader =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperHeader
# FILE: sql_time_manipulation.py
# CREATION DATE: 11-10-2025
# LAST Modified: 13:12:2 13-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File in charge of containing the functions that allow for time conversion between datetime and strings.
# // AR
# +==== END AsperHeader =================+
"""


from datetime import datetime

from display_tty import Disp, initialise_logger

from . import sql_constants as SCONST


class SQLTimeManipulation:
    """Handle time conversion between datetime objects and strings.

    This class provides methods to convert datetime objects to strings and
    vice versa, with support for SQL-compatible formats.

    Attributes:
        debug (bool): Debug mode flag.
        date_only (str): Format string for date-only conversion.
        date_and_time (str): Format string for date and time conversion.
        disp (Disp): Logger instance for debugging and error reporting.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, debug: bool = False) -> None:
        """Initialize the SQLTimeManipulation instance.

        Args:
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.debug: bool = debug
        # ----------------------- Inherited from SCONST  -----------------------
        self.date_only: str = SCONST.DATE_ONLY
        self.date_and_time: str = SCONST.DATE_AND_TIME
        # --------------------------- logger section ---------------------------
        self.disp.update_disp_debug(self.debug)

    def datetime_to_string(self, datetime_instance: datetime, date_only: bool = False, sql_mode: bool = False) -> str:
        """Convert a datetime object to a formatted string.

        Args:
            datetime_instance (datetime): Datetime to format.
            date_only (bool, optional): Return only the date portion. Defaults to False.
            sql_mode (bool, optional): Include millisecond precision for SQL. Defaults to False.

        Raises:
            ValueError: If the input is not a datetime instance.

        Returns:
            str: Formatted datetime string.
        """
        if not isinstance(datetime_instance, datetime):
            self.disp.log_error(
                "The input is not a datetime instance.",
                "datetime_to_string"
            )
            raise ValueError("Error: Expected a datetime instance.")
        if date_only:
            return datetime_instance.strftime(self.date_only)
        converted_time = datetime_instance.strftime(self.date_and_time)
        if sql_mode:
            microsecond = datetime_instance.strftime("%f")[:3]
            return f"{converted_time}.{microsecond}"
        return converted_time

    def string_to_datetime(self, datetime_string_instance: str, date_only: bool = False) -> datetime:
        """Convert a formatted string to a datetime object.

        Args:
            datetime_string_instance (str): Formatted datetime string.
            date_only (bool, optional): Parse using the date-only format. Defaults to False.

        Raises:
            ValueError: If the input is not a string instance.

        Returns:
            datetime: Parsed datetime object.
        """
        if not isinstance(datetime_string_instance, str):
            self.disp.log_error(
                "The input is not a string instance.",
                "string_to_datetime"
            )
            raise ValueError("Error: Expected a string instance.")
        if date_only:
            return datetime.strptime(datetime_string_instance, self.date_only)
        return datetime.strptime(datetime_string_instance, self.date_and_time)

    def get_correct_now_value(self) -> str:
        """Get the current date and time in the correct format for the database.

        Returns:
            str: Formatted current date and time.
        """
        current_time = datetime.now()
        return current_time.strftime(self.date_and_time)

    def get_correct_current_date_value(self) -> str:
        """Get the current date in the correct format for the database.

        Returns:
            str: Formatted current date.
        """
        current_time = datetime.now()
        return current_time.strftime(self.date_only)
