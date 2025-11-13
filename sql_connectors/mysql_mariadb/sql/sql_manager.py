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
# FILE: sql_manager.py
# CREATION DATE: 11-10-2025
# LAST Modified: 13:24:50 13-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE:
# File in charge of containing the interfacing between an sql library and the program.
# This contains functions that simplify the process of interracting with databases as well as check for injection attempts.
# /STOP
# // AR
# +==== END AsperHeader =================+

"""

from typing import Optional, Union, List, Dict, Tuple, Literal, Any, overload

from datetime import datetime

from display_tty import Disp, initialise_logger

from .sql_time_manipulation import SQLTimeManipulation
from .sql_connections import SQLManageConnections
from .sql_query_boilerplates import SQLQueryBoilerplates


class SQL:
    """Manage database access and provide high-level query helpers.

    This class wraps a low-level connection manager and exposes convenience
    methods for common operations. Call :py:meth:`create` to build a
    fully-initialized instance ready for usage.

    Attributes:
        disp (Disp): Logger instance for debugging and error reporting.
        sql_manage_connections (SQLManageConnections): Manages database connections.
        sql_time_manipulation (SQLTimeManipulation): Handles time-related SQL operations.
        sql_query_boilerplates (SQLQueryBoilerplates): Provides query boilerplates.
        debug (bool): Debug mode flag.
        success (int): Numeric success code.
        error (int): Numeric error code.
        url (str): Database URL.
        port (int): Database port.
        username (str): Database username.
        password (str): Database password.
        db_name (str): Database name.
    """

    # --------------------------------------------------------------------------
    # STATIC CLASS VALUES
    # --------------------------------------------------------------------------

    # -------------- Initialise the logger globally in the class. --------------
    disp: Disp = initialise_logger(__qualname__, False)

    # ------------------ Runtime error for undefined elements ------------------
    _runtime_error_string: str = "SQLQueryBoilerplates method not initialized"

    # Docstring wrapper notice
    _wrapper_notice_begin: str = "(Wrapper) Delegates to SQLQueryBoilerplates."
    _wrapper_notice_end: str = "\n\nOriginal docstring:\n"

    # --------------------------------------------------------------------------
    # CONSTRUCTOR & DESTRUCTOR
    # --------------------------------------------------------------------------

    def __init__(self, url: str, port: int, username: str, password: str, db_name: str, success: int = 0, error: int = 84, debug: bool = False):
        """Initialize the SQL facade instance.

        Args:
            url (str): Database URL.
            port (int): Database port.
            username (str): Database username.
            password (str): Database password.
            db_name (str): Database name.
            success (int, optional): Numeric success code. Defaults to 0.
            error (int, optional): Numeric error code. Defaults to 84.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.url: str = url
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.db_name: str = db_name

        self.sql_time_manipulation = SQLTimeManipulation(
            self.debug
        )
        self._get_correct_now_value = self.sql_time_manipulation.get_correct_now_value
        self._get_correct_current_date_value = self.sql_time_manipulation.get_correct_current_date_value
        # --------------------------- debug section  ---------------------------
        # Note: pool initialisation is  Use the factory `create` to
        # obtain a fully-initialized SQL instance.
        self.sql_manage_connections = SQLManageConnections(
            url=self.url,
            port=self.port,
            username=self.username,
            password=self.password,
            db_name=self.db_name,
            success=self.success,
            error=self.error,
            debug=self.debug
        )

        # ---------------------------- Time logger  ----------------------------
        self.sql_time_manipulation = SQLTimeManipulation(
            self.debug
        )
        self._get_correct_now_value = self.sql_time_manipulation.get_correct_now_value
        self._get_correct_current_date_value = self.sql_time_manipulation.get_correct_current_date_value
        # --------------------------- debug section  ---------------------------
        # Note: pool initialisation is  Use the factory `create` to
        # obtain a fully-initialized SQL instance.
        self.sql_manage_connections.show_connection_info("__init__")
        # sql_query_boilerplates will be created by the factory once the
        # connection pool is initialised.
        self.sql_query_boilerplates: Optional[SQLQueryBoilerplates] = None

    def __del__(self) -> None:
        """Best-effort cleanup invoked when the instance is garbage-collected.

        This releases references to internal helpers so external resources
        can be freed by the event loop later. Avoid ng inside
        destructors.
        """
        if self.sql_manage_connections is not None:
            del self.sql_manage_connections
            self.sql_manage_connections = None
        if self.sql_time_manipulation is not None:
            del self.sql_time_manipulation
            self.sql_time_manipulation = None
        if self.sql_query_boilerplates is not None:
            del self.sql_query_boilerplates
            self.sql_query_boilerplates = None

    # --------------------------------------------------------------------------
    # WRAPPER DEFINITIONS
    # --------------------------------------------------------------------------

    def datetime_to_string(self, datetime_instance: datetime, date_only: bool = False, sql_mode: bool = False) -> str:
        """(Wrapper) Delegates to SQLTimeManipulation.datetime_to_string

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Format a :class:`datetime` to the project's string representation.

        Args:
            datetime_instance (datetime): Datetime to format.
            date_only (bool): When True, return only the date portion.
            sql_mode (bool): When True, include millisecond precision suitable
                for insertion into SQL text fields.

        Raises:
            ValueError: If ``datetime_instance`` is not a :class:`datetime`.

        Returns:
            str: Formatted date/time string.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.datetime_to_string(datetime_instance, date_only, sql_mode)

    def string_to_datetime(self, datetime_string_instance: str, date_only: bool = False) -> datetime:
        """(Wrapper) Delegates to SQLTimeManipulation.string_to_datetime

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Parse a formatted date/time string into a :class:`datetime`.

        Args:
            datetime_string_instance (str): The string to parse.
            date_only (bool): When True, parse using the date-only format.

        Raises:
            ValueError: If the input is not a string or cannot be parsed.

        Returns:
            datetime: Parsed :class:`datetime` instance.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.string_to_datetime(datetime_string_instance, date_only)

    def get_correct_now_value(self) -> str:
        """(Wrapper) Delegates to SQLTimeManipulation.get_correct_now_value

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the current date/time formatted using the project's pattern.

        Returns:
            str: Formatted current date/time string.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.get_correct_now_value()

    def get_correct_current_date_value(self) -> str:
        """(Wrapper) Delegates to SQLTimeManipulation.get_correct_current_date_value

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the current date formatted using the project's date-only pattern.

        Returns:
            str: Formatted current date string.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.get_correct_current_date_value()

    def get_database_version(self) -> Optional[Tuple[int, int, int]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.create_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Fetch and parse the database version.

        Returns:
            Optional[Tuple[Union[int, str], ...]]:
                A tuple representing the database version, or None if the query fails.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_database_version()

    def get_table_column_names(self, table_name: str) -> Union[List[str], int]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_table_column_names

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the list of column names for ``table_name``.

        Args:
            table_name (str): Name of the table to inspect.

        Returns:
            Union[List[str], int]: List of column names on success, or
            ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_table_column_names(table_name)

    def get_table_names(self) -> Union[int, List[str]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_table_names

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a list of non-internal table names in the database.

        Returns:
            Union[int, List[str]]: List of table names or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_table_names()

    def get_triggers(self) -> Union[int, Dict[str, str]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_triggers

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a dictionary of all triggers and their SQL definitions.

        Returns:
            Union[int, Dict[str, str]]: Dict of {trigger_name: sql_definition}, or ``self.error``.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_triggers()

    def get_trigger(self, trigger_name: str) -> Union[int, str]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a dictionary of all triggers and their SQL definitions.

        Returns:
            Union[int, Dict[str, str]]: Dict of {trigger_name: sql_definition}, or ``self.error``.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_trigger(trigger_name)

    def get_trigger_names(self) -> Union[int, List[str]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_trigger_names

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a list of non-internal trigger names in the database.

        Returns:
            Union[int, List[str]]: List of trigger names, or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_trigger_names()

    def describe_table(self, table: str) -> Union[int, List[Any]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.describe_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Fetch the schema description for a table.

        This returns rows similar to SQLite's PRAGMA table_info but is
        transformed so the first element is the column name (to remain
        compatible with previous MySQL-style DESCRIBE results).

        Args:
            table (str): Name of the table to describe.

        Raises:
            RuntimeError: On critical SQLite errors (re-raised as RuntimeError).

        Returns:
            Union[int, List[Any]]: Transformed description rows on success,
            or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.describe_table(table)

    def create_table(self, table: str, columns: List[Tuple[str, str]]) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.create_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Create a new table in the SQLite database.

        Args:
            table (str): Name of the new table.
            columns (List[Tuple[str, str]]): List of (column_name, column_type) pairs.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to create a basic ``users`` table:

            .. code-block:: python

                # Define the table name and column definitions
                table_name = "users"
                columns = [
                    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                    ("username", "TEXT NOT NULL UNIQUE"),
                    ("email", "TEXT NOT NULL"),
                    ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                ]

                # Create the table ronously
                result = self.create_table(table_name, columns)

                # Check if the operation succeeded
                if result == self.success:
                    print(f"Table '{table_name}' created successfully.")
                else:
                    print(f"Failed to create table '{table_name}'.")

        Notes:
            - This method automatically checks for SQL injection attempts using :class:`SQLInjection` before executing the query.
            - Single quotes in table or column names are escaped defensively.
            - The query uses ``CREATE TABLE IF NOT EXISTS`` to avoid errors if the table already exists.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.create_table(table, columns)

    def create_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert (create) a new SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.insert_trigger(trigger_name, table_name, timing_event, body)

    def insert_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert (create) a new SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.insert_trigger(trigger_name, table_name, timing_event, body)

    def insert_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: Union[List[str], None] = None) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_data_into_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert one or multiple rows into ``table``.

        Args:
            table (str): Table name.
            data (Union[List[List[str]], List[str]]): Row data. Either a
                single row (List[str]) or a list of rows (List[List[str]]).
            column (List[str] | None): Optional list of columns to insert into.

        Returns:
            int: ``self.success`` on success or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.insert_data_into_table(table, data, column)

    @overload
    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        beautify: Literal[True] = True,
    ) -> Union[int, List[Dict[str, Any]]]: ...

    @overload
    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        beautify: Literal[False] = False,
    ) -> Union[int, List[Tuple[Any, Any]]]: ...

    def get_data_from_table(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "", beautify: bool = True) -> Union[int, Union[List[Dict[str, Any]], List[Tuple[Any, Any]]]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_data_from_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Query rows from ``table`` and optionally return them in a beautified form.

        Args:
            table (str): Table name.
            column (Union[str, List[str]]): Column name(s) or '*' to select.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions. Defaults to empty string.
            beautify (bool, optional): If True, convert rows to list of dicts
                keyed by column names. Defaults to True.

        Returns:
            Union[int, List[Dict[str, Any]], List[Tuple[str, Any]]]: Beautified list of Dictionaries on success and if beautify is True, otherwise, a list of tuples is beautify is set to False, or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_data_from_table(table, column, where, beautify)

    def get_table_size(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "") -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_table_size

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the number of rows matching the optional WHERE clause.

        Args:
            table (str): Table name.
            column (Union[str, List[str]]): Column to COUNT over (often '*').
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions. Defaults to empty string.

        Returns:
            int: Number of matching rows, or ``SCONST.GET_TABLE_SIZE_ERROR`` on error.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.get_table_size(table, column, where)

    def update_data_in_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: List[str], where: Union[str, List[str]] = "") -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.update_data_in_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Update rows in ``table`` matching ``where`` with values from ``data``.

        Args:
            table (str): Table name.
            data (List[str]): New values to set.
            column (List): Column names corresponding to data.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions. Defaults to empty string.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.update_data_in_table(table, data, column, where)

    def insert_or_update_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], columns: Union[List[str], None] = None) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_or_update_data_into_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert new rows or update existing rows for ``table``.

        This method determines column names if not provided and delegates
        to the appropriate INSERT/UPDATE boilerplate.

        Args:
            table (str): Table name.
            data (Union[List[List[str]], List[str]]): Data to insert or update.
            columns (List[str] | None, optional): Column names. Defaults to None.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.insert_or_update_data_into_table(table, data, columns)

    def insert_or_update_trigger(self,  trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_or_update_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert (create) or update an SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.insert_or_update_trigger(trigger_name, table_name, timing_event, body)

    def remove_data_from_table(self, table: str, where: Union[str, List[str]] = "") -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_data_from_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Delete rows from ``table`` matching ``where``.

        Args:
            table (str): Table name to delete rows from.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions to filter rows. If empty, all rows are deleted.

        Returns:
            int: ``self.success`` on success or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.remove_data_from_table(table, where)

    def drop_data_from_table(self, table: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_data_from_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Delete rows from ``table`` matching ``where``.

        Args:
            table (str): Table name to delete rows from.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions to filter rows. If empty, all rows are deleted.

        Returns:
            int: ``self.success`` on success or ``self.error`` on failure.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        # alias for remove_data_from_table to preserve API consistency
        return self.sql_query_boilerplates.remove_data_from_table(table)

    def remove_table(self, table: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove (delete) a table from the SQLite database.

        Args:
            table (str): Name of the table to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to drop the ``users`` table:

            .. code-block:: python

                table_name = "users"
                result = self.drop_table(table_name)

                if result == self.success:
                    print(f"Table '{table_name}' dropped successfully.")
                else:
                    print(f"Failed to drop table '{table_name}'.")

        Notes:
            - The method performs SQL injection detection on the table name.
            - If the table does not exist, no error is raised (uses ``DROP TABLE IF EXISTS`` internally).
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.remove_table(table)

    def drop_table(self, table: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove (delete) a table from the SQLite database.

        Args:
            table (str): Name of the table to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to drop the ``users`` table:

            .. code-block:: python

                table_name = "users"
                result = self.drop_table(table_name)

                if result == self.success:
                    print(f"Table '{table_name}' dropped successfully.")
                else:
                    print(f"Failed to drop table '{table_name}'.")

        Notes:
            - The method performs SQL injection detection on the table name.
            - If the table does not exist, no error is raised (uses ``DROP TABLE IF EXISTS`` internally).
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.remove_table(table)

    def remove_trigger(self, trigger_name: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove an existing SQL trigger if it exists.

        Args:
            trigger_name (str): Name of the trigger to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.remove_trigger(trigger_name)

    def drop_trigger(self, trigger_name: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove an existing SQL trigger if it exists.

        Args:
            trigger_name (str): Name of the trigger to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        if self.sql_query_boilerplates is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_query_boilerplates.remove_trigger(trigger_name)

    # --------------------------------------------------------------------------
    # FACTORY + CLEANUP
    # --------------------------------------------------------------------------
    @classmethod
    def create(cls, url: str, port: int, username: str, password: str, db_name: str, success: int = 0, error: int = 84, debug: bool = False) -> 'SQL':
        """factory to create and initialise an SQL instance.

        This factory completes ronous initialisation steps that the
        synchronous constructor cannot perform (notably the connection
        pool initialisation). After this call returns the instance is ready
        for usage and convenience callables are bound on the
        instance.

        Args:
            url (str): DB host or file path (for sqlite this is a filename).
            port (int): DB port (unused for sqlite but retained for API
                compatibility).
            username (str): DB username (unused for sqlite).
            password (str): DB password (unused for sqlite).
            db_name (str): Database name or sqlite filename.
            success (int, optional): numeric success code used across the
                sql helpers. Defaults to 0.
            error (int, optional): numeric error code used across the sql
                helpers. Defaults to 84.
            debug (bool, optional): enable debug logging. Defaults to False.

        Returns:
            SQL: Initialized SQL instance ready for operations.

        Raises:
            RuntimeError: If the connection pool cannot be initialised.

        Example:
            sql = SQL.create('db.sqlite', 0, '', '', 'db.sqlite')
            sql.get_data_from_table('my_table')
        """

        self = cls(
            url,
            port,
            username,
            password,
            db_name,
            success=success,
            error=error,
            debug=debug
        )
        # Initialise the connection pool
        # static checkers see `sql_manage_connections` as Optional; assert
        # it's available to narrow the type for the following calls.
        assert self.sql_manage_connections is not None
        assert self.disp is not None
        if self.sql_manage_connections.initialise_pool() != self.success:
            msg = "Failed to initialise the connection pool."
            self.disp.log_critical(msg, "create")
            raise RuntimeError(f"Error: {msg}")
        # Create the query helper now that the pool is ready
        self.sql_query_boilerplates = SQLQueryBoilerplates(
            sql_pool=self.sql_manage_connections, success=self.success,
            error=self.error, debug=self.debug
        )
        return self

    def close(self) -> None:
        """Cleanly close resources like the connection pool."""
        if self.sql_manage_connections is not None:
            try:
                self.sql_manage_connections.destroy_pool()
            except Exception as e:
                if self.disp:
                    self.disp.log_error(
                        f"Error while closing connection pool: {e}"
                    )
        # Clean up all references
        self.sql_manage_connections = None
        self.sql_query_boilerplates = None
        self.sql_time_manipulation = None
