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
# FILE: sql_query_boilerplates.py
# CREATION DATE: 11-10-2025
# LAST Modified: 13:20:19 13-11-2025
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


from typing import List, Dict, Union, Any, Tuple, Optional, Literal, overload

import mysql
import mysql.connector
from display_tty import Disp, initialise_logger


from . import sql_constants as SCONST
from .sql_injection import SQLInjection
from .sql_connections import SQLManageConnections
from .sql_sanitisation_functions import SQLSanitiseFunctions


class SQLQueryBoilerplates:
    """Provide reusable SQL query templates and helpers.

    This class contains methods for generating common SQL queries, such as
    creating tables, inserting data, and fetching results. It simplifies
    database interactions by abstracting repetitive query patterns.

    Attributes:
        disp (Disp): Logger instance for debugging and error reporting.
        sql_pool (SQLManageConnections): Connection manager for database operations.
        error (int): Numeric error code.
        success (int): Numeric success code.
        debug (bool): Debug mode flag.
        db_version (Optional[Tuple[int, int, int]]): Parsed database version.
        sql_injection (SQLInjection): SQL injection protection utility.
        sanitize_functions (SQLSanitiseFunctions): SQL sanitization utility.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, sql_pool: SQLManageConnections, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the query helper.

        Args:
            sql_pool (SQLManageConnections): Async connection manager used to run queries and commands.
            success (int, optional): Numeric success code. Defaults to 0.
            error (int, optional): Numeric error code. Defaults to 84.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        # -------------------------- Inherited values --------------------------
        self.sql_pool: SQLManageConnections = sql_pool
        self.error: int = error
        self.debug: bool = debug
        self.success: int = success
        # --------------------------- logger section ---------------------------
        self.disp.update_disp_debug(self.debug)
        # ------------------------ SQL Database version ------------------------
        self.db_version: Optional[Tuple[int, int, int]] = None
        self.db_version_major: Optional[int] = None
        self.db_version_minor: Optional[int] = None
        self.db_version_retro: Optional[int] = None
        if self.sql_pool.is_pool_active():
            self.get_database_version()
        # ---------------------- The anty injection class ----------------------
        self.sql_injection: SQLInjection = SQLInjection(
            self.error,
            self.success,
            self.debug
        )
        # -------------------- Keyword sanitizing functions --------------------
        self.sanitize_functions: SQLSanitiseFunctions = SQLSanitiseFunctions(
            success=self.success, error=self.error, debug=self.debug
        )

    def _normalize_cell(self, cell: object) -> Union[str, None, int, float]:
        """Normalize a cell value for parameter binding.

        Converts special tokens (e.g., 'now', 'current_date') and preserves numeric
        types. Returns None for null-like inputs.

        Args:
            cell (object): The cell value to normalize.

        Returns:
            Union[str, None, int, float]: Normalized cell value.
        """
        if cell is None:
            return None
        if isinstance(cell, (int, float)):
            return cell
        s = str(cell)
        sl = s.lower()
        if sl in ("now", "now()"):
            return self.sanitize_functions.sql_time_manipulation.get_correct_now_value()
        if sl in ("current_date", "current_date()"):
            return self.sanitize_functions.sql_time_manipulation.get_correct_current_date_value()
        return s

    def get_database_version(self) -> Optional[Tuple[int, int, int]]:
        """Fetch and parse the database version.

        Returns:
            Optional[Tuple[int, int, int]]: A tuple representing the database version,
            or None if the query fails.
        """
        _query: str = "SELECT VERSION()"
        resp = self.sql_pool.run_and_fetch_all(_query)
        if isinstance(resp, int):
            return None
        if not resp or not isinstance(resp, list):
            return None
        if not resp[0] or not isinstance(resp[0], tuple):
            return None
        if not resp[0][0] or not isinstance(resp[0][0], str):
            return None
        vers = resp[0][0]
        version_parts = vers.split('.')
        parsed_version = []
        for part in version_parts:
            if part.isdigit():
                parsed_version.append(int(part))
            else:
                parsed_version.append(part)
        self.db_version = tuple(parsed_version)
        self.db_version_major = self.db_version[0]
        self.db_version_minor = self.db_version[1]
        self.db_version_retro = self.db_version[2]
        return self.db_version

    def get_table_column_names(self, table_name: str) -> Union[List[str], int]:
        """Return the list of column names for a given table.

        Args:
            table_name (str): Name of the table to retrieve column names from.

        Returns:
            Union[List[str], int]: List of column names on success, or `self.error` on failure.
        """
        title = "get_table_column_names"
        try:
            columns = self.describe_table(table_name)
            if isinstance(columns, int) is True:
                self.disp.log_error(
                    f"Failed to describe table {table_name}.",
                    title
                )
                return self.error
            data = []
            if isinstance(columns, List):
                for i in columns:
                    data.append(i[0])
            return data
        except RuntimeError as e:
            msg = "Error: Failed to get column names of the tables.\n"
            msg += f"\"{str(e)}\""
            self.disp.log_error(msg, "get_table_column_names")
            return self.error

    def get_table_names(self) -> Union[int, List[str]]:
        """Retrieve the names of all tables in the database.

        Returns:
            Union[int, List[str]]: List of table names on success, or `self.error` on failure.
        """
        title = "get_table_names"
        self.disp.log_debug("Getting table names.", title)
        resp = self.sql_pool.run_and_fetch_all(query="SHOW TABLES")
        if isinstance(resp, int) is True:
            self.disp.log_error(
                "Failed to fetch the table names.",
                title
            )
            return self.error
        data = []
        if isinstance(resp, (List, Dict, Tuple)):
            for i in resp:
                data.append(i[0])
        self.disp.log_debug("Tables fetched", title)
        return data

    def get_triggers(self) -> Union[int, Dict[str, str]]:
        """Retrieve all triggers and their SQL definitions.

        Returns:
            Union[int, Dict[str, str]]: Dictionary of {trigger_name: sql_definition},
            or `self.error` on failure.
        """
        title = "get_triggers"
        self.disp.log_debug(
            "Fetching all triggers and their SQL definitions.", title
        )

        query = "SHOW TRIGGERS;"
        resp = self.sql_pool.run_and_fetch_all(query=query, values=[])

        if isinstance(resp, int):
            self.disp.log_error("Failed to fetch triggers.", title)
            return self.error

        data: Dict[str, str] = {}
        for row in resp:
            if len(row) >= 2 and row[0] and row[1]:
                data[row[0]] = row[1]

        self.disp.log_debug(f"Triggers fetched: {list(data.keys())}", title)
        return data

    def get_trigger(self, trigger_name: str, db_name: Optional[str] = None) -> Union[int, str]:
        """Retrieve the SQL definition of a specific trigger.

        Args:
            trigger_name (str): The trigger name to fetch.
            db_name (Optional[str], optional): Database name. Defaults to None.

        Returns:
            Union[int, str]: The SQL definition, or `self.error` on failure.
        """
        title = "get_trigger"
        self.disp.log_debug(
            f"Getting trigger definition for '{trigger_name}'", title
        )

        if not trigger_name:
            self.disp.log_error("Trigger name cannot be empty.", title)
            return self.error

        to_check: List[str] = [trigger_name]
        if db_name:
            to_check.append(db_name)

        if self.sql_injection.check_if_injections_in_strings(to_check):
            self.disp.log_error(
                "SQL Injection detected in trigger name.", title)
            return self.error

        if db_name:
            query = f"SHOW CREATE TRIGGER `{db_name}`.`{trigger_name}`"
        else:
            query = f"SHOW CREATE TRIGGER `{trigger_name}`"

        resp = self.sql_pool.run_and_fetch_all(query=query, values=None)

        if isinstance(resp, int) or not resp:
            self.disp.log_error(
                f"Failed to retrieve trigger '{trigger_name}'.", title
            )
            return self.error

        sql_definition = None
        if resp and len(resp[0]) > 2:
            sql_definition = resp[0][2]
        if not sql_definition:
            self.disp.log_error(
                f"No SQL definition found for trigger '{trigger_name}'.", title
            )
            return self.error

        self.disp.log_debug(
            f"SQL for trigger '{trigger_name}':\n{sql_definition}", title
        )
        return sql_definition

    def get_trigger_names(self, db_name: Optional[str] = None) -> Union[int, List[str]]:
        """Return a list of trigger names in the current or specified MySQL database.

        Args:
            db_name (Optional[str], optional):
                Name of the database/schema to query.
                Defaults to None, which uses the currently selected database.

        Returns:
            Union[int, List[str]]: List of trigger names, or ``self.error`` on failure.
        """
        title = "get_trigger_names"
        self.disp.log_debug("Getting trigger names.", title)
        if db_name:
            if self.sql_injection.check_if_injections_in_strings([db_name]):
                self.disp.log_error(
                    "SQL Injection detected in database name.", title
                )
                return self.error

            query = (
                "SELECT TRIGGER_NAME "
                "FROM information_schema.triggers "
                "WHERE TRIGGER_SCHEMA = %s "
                "ORDER BY TRIGGER_NAME;"
            )
            values: List[Union[str, int, float]] = [db_name]
        else:
            query = (
                "SELECT TRIGGER_NAME "
                "FROM information_schema.triggers "
                "WHERE TRIGGER_SCHEMA = DATABASE() "
                "ORDER BY TRIGGER_NAME;"
            )
            values: List[Union[str, int, float]] = []

        # --------------------------------------------------------------------------
        # Execute the query
        # --------------------------------------------------------------------------
        self.disp.log_debug(f"Running query: {query}", title)
        response = self.sql_pool.run_and_fetch_all(query=query, values=values)

        if isinstance(response, int):
            self.disp.log_error("Failed to fetch trigger names.", title)
            return self.error

        if not response:
            self.disp.log_debug(
                "No triggers found in the selected database.", title)
            return []

        # --------------------------------------------------------------------------
        # Extract trigger names
        # --------------------------------------------------------------------------
        trigger_names: List[str] = []
        for row in response:
            if row and row[0]:
                trigger_names.append(row[0])

        self.disp.log_debug(f"Triggers fetched: {trigger_names}", title)
        return trigger_names

    def describe_table(self, table: str) -> Union[int, List[Any]]:
        """Fetch the headers (description) of a table from the database.

        Args:
            table (str): The name of the table to describe.

        Returns:
            Union[int, List[Any]]: A list containing the description of the table, or self.error if an error occurs.
        """
        title = "describe_table"
        self.disp.log_debug(f"Describing table {table}", title)
        if self.sql_injection.check_if_sql_injection(table) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        try:
            resp = self.sql_pool.run_and_fetch_all(query=f"DESCRIBE {table}")
            if isinstance(resp, int) is True:
                self.disp.log_error(
                    f"Failed to describe table  {table}", title
                )
                return self.error
            return resp
        except mysql.connector.errors.ProgrammingError as pe:
            msg = f"ProgrammingError: The table '{table}'"
            msg += "does not exist or the query failed."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from pe
        except mysql.connector.errors.IntegrityError as ie:
            msg = "IntegrityError: There was an integrity constraint "
            msg += f"issue while describing the table '{table}'."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from ie
        except mysql.connector.errors.OperationalError as oe:
            msg = "OperationalError: There was an operational error "
            msg += f"while describing the table '{table}'."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = "MySQL Error: An unexpected error occurred while "
            msg += f"describing the table '{table}'."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e
        except RuntimeError as e:
            msg = "A runtime error occurred during the table description process."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e

    def create_table(self, table: str, columns: List[Tuple[str, str]]) -> int:
        """Create a new table in the MySQL database, compatible with MySQL 5.0+.

        Args:
            table (str): Name of the new table.
            columns (List[Tuple[str, str]]): List of (column_name, column_type) pairs.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            .. code-block:: python

                table_name = "users"
                columns = [
                    ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                    ("username", "VARCHAR(255) NOT NULL UNIQUE"),
                    ("email", "VARCHAR(255) NOT NULL"),
                    ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                ]

                result = self.create_table(table_name, columns)
                if result == self.success:
                    print(f"Table '{table_name}' created successfully.")
                else:
                    print(f"Failed to create table '{table_name}'.")

        Notes:
            - Protects against SQL injection using :class:`SQLInjection`.
            - Escapes table and column names with backticks for MySQL.
            - Includes version-aware fallback for MySQL 5.0 compatibility.
        """
        title = "create_table"
        self.disp.log_debug(f"Creating table '{table}'", title)

        # --- SQL injection protection ---
        if self.sql_injection.check_if_injections_in_strings([table]):
            self.disp.log_error("Injection detected in table name.", title)
            return self.error

        try:
            # --- Escape table name ---
            table_safe = table.replace("`", "``")

            # --- Build column definitions safely ---
            _tmp = []
            for name, col_type in columns:
                safe_name = name.replace("`", "``")

                # Fallback for old MySQL versions (5.0–5.5)
                if (
                    "DEFAULT CURRENT_TIMESTAMP" in col_type.upper()
                    and (
                        not self.db_version_major or self.db_version_major <= 5
                    )
                ):
                    self.disp.log_warning(
                        f"MySQL 5.0 does not support 'DEFAULT CURRENT_TIMESTAMP' "
                        f"on DATETIME columns. Downgrading '{safe_name}' definition.",
                        title,
                    )
                    col_type = col_type.upper().replace(
                        "DEFAULT CURRENT_TIMESTAMP", "NULL"
                    )

                _tmp.append(f"`{safe_name}` {col_type}")

            columns_def = ", ".join(_tmp)
            query = f"CREATE TABLE IF NOT EXISTS `{table_safe}` ({columns_def}) ENGINE=InnoDB;"

            self.disp.log_debug(f"Executing SQL: {query}", title)

            result = self.sql_pool.run_and_commit(query=query, values=[])

            if isinstance(result, int) and result == self.error:
                self.disp.log_error(f"Failed to create table '{table}'", title)
                return self.error

            self.disp.log_info(f"Table '{table}' created successfully.", title)
            return self.success

        except mysql.connector.OperationalError as oe:
            msg = f"MySQL OperationalError while creating table '{table}': {oe}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = f"MySQL Error while creating table '{table}': {e}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Unexpected error while creating table '{table}': {e}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e

    def insert_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: Union[List[str], None] = None) -> int:
        """Insert data into a table.

        Args:
            table (str): Name of the table.
            data (Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]]): Data to insert.
            column (Union[List[str], None], optional): List of column names. Defaults to None.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        title = "insert_data_into_table"
        self.disp.log_debug("Inserting data into the table.", title)
        if column is None:
            column = []
        check_data: Union[
            List[List[Union[str, None, int, float]]],
            List[Union[str, None, int, float]]
        ] = [table]
        if column is not None:
            check_data.extend(column)
        if isinstance(data, List):
            for i in data:
                if isinstance(i, List):
                    check_data.extend(i)
                else:
                    check_data.append(i)
        if self.sql_injection.check_if_injections_in_strings(check_data) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error

        if isinstance(column, List) and len(column) == 0:
            column_raw = self.get_table_column_names(table)
            if column_raw is None:
                return self.error
            if isinstance(column_raw, list):
                column = column_raw

        if column is None:
            return self.error
        column_checked: Union[List[str], str] = column

        column_checked = self.sanitize_functions.escape_risky_column_names(
            column_checked
        )

        column_str = ", ".join(column)
        column_length = len(column)

        try:
            cleaned_lines: Tuple[
                str, List[Union[str, int, float, None]]
            ] = self.sanitize_functions.process_sql_line(data, column, column_length)
            line = cleaned_lines[0]
            values = cleaned_lines[1]
            sql_query = f"INSERT INTO {table} ({column_str}) VALUES {line}"
            self.disp.log_debug(
                f"sql_query = '{sql_query}', values = '{values}'", title
            )
            return self.sql_pool.run_editing_command(sql_query, values, table, "insert")
        except RuntimeError as e:
            self.disp.log_error(
                f"Failed to check and clean the data needed to be inserted: {e}"
            )
            return self.error

    def insert_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """Insert (create) a new SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        title = "insert_trigger"

        # --- Sanity checks ---
        if not all([trigger_name, table_name, timing_event, body]):
            self.disp.log_error("All parameters must be provided.", title)
            return self.error

        self.disp.log_debug(f"Inserting trigger: {trigger_name}", title)
        # --- SQL injection prevention ---
        if self.sql_injection.check_if_injections_in_strings([trigger_name, table_name]):
            self.disp.log_error("SQL injection detected.", title)
            return self.error

        if self.sql_injection.check_if_symbol_and_logic_gate_injection(timing_event):
            self.disp.log_error("SQL injection detected", title)
            return self.error

        # --- Build the SQL ---
        sql_query = self.sanitize_functions.clean_trigger_creation(
            trigger_name, table_name, timing_event, body)
        self.disp.log_debug(f"Trigger SQL:\n{sql_query}", title)
        if sql_query != self.success or not isinstance(sql_query, str):
            self.disp.log_error("Sql trigger query is invalid.", title)
            return self.error

        # --- Drop existing trigger (MySQL has no CREATE TRIGGER IF NOT EXISTS) ---
        response: int = self.remove_trigger(trigger_name)
        if response != self.success:
            self.disp.log_warning(
                f"Could not drop trigger '{trigger_name}' (may not exist).", title
            )

        # --- Execute trigger creation ---
        result = self.sql_pool.run_editing_command(
            sql_query, [], trigger_name, "create_trigger"
        )
        if result != self.success:
            self.disp.log_error(
                f"Failed to create trigger '{trigger_name}'", title
            )
            return self.error

        self.disp.log_info(
            f"Trigger '{trigger_name}' successfully created.", title
        )
        return self.success

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
        """_summary_

        Args:
            table (str): _description_
            column (Union[str, List[str]]): _description_
            where (Union[str, List[str]]): _description_

        Returns:
            Union[int, List[Dict[str, Any]]]: _description_: Will return the data you requested, self.error otherwise
        """
        title = "get_data_from_table"
        self.disp.log_debug(f"fetching data from the table {table}", title)
        if self.sql_injection.check_if_injections_in_strings([table, column]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if isinstance(column, list) is True:
            column = self.sanitize_functions.escape_risky_column_names(column)
            column = ", ".join(column)
        sql_command = f"SELECT {column} FROM {table}"
        if isinstance(where, (str, List)) is True:
            where = self.sanitize_functions.escape_risky_column_names_where_mode(
                where
            )
        if isinstance(where, List) is True:
            where = " AND ".join(where)
        if where != "":
            sql_command += f" WHERE {where}"
        self.disp.log_debug(f"sql_query = '{sql_command}'", title)
        resp = self.sql_pool.run_and_fetch_all(query=sql_command, values=[])
        if isinstance(resp, int):
            if resp != self.success:
                self.disp.log_error(
                    "Failed to fetch the data from the table.", title
                )
                return self.error
            resp_list = []
        else:
            resp_list = resp
        self.disp.log_debug(f"Queried data: {resp}", title)
        if beautify is False:
            return resp_list
        data = self.describe_table(table)
        if isinstance(data, int):
            return self.error
        return self.sanitize_functions.beautify_table(data, resp_list)

    def get_table_size(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "") -> int:
        """_summary_
            Get the size of a table.

        Args:
            table (str): _description_
            column (Union[str, List[str]]): _description_
            where (Union[str, List[str]]): _description_

        Returns:
            int: _description_: Return the size of the table, -1 if an error occurred.
        """
        title = "get_table_size"
        self.disp.log_debug(f"fetching data from the table {table}", title)
        if self.sql_injection.check_if_injections_in_strings([table, column]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return SCONST.GET_TABLE_SIZE_ERROR
        if isinstance(column, list) is True:
            column = ", ".join(column)
        sql_command = f"SELECT COUNT({column}) FROM {table}"
        if isinstance(where, (str, List)) is True:
            where = self.sanitize_functions.escape_risky_column_names_where_mode(
                where
            )
        if isinstance(where, List) is True:
            where = " AND ".join(where)
        if where != "":
            sql_command += f" WHERE {where}"
        self.disp.log_debug(f"sql_query = '{sql_command}'", title)
        resp = self.sql_pool.run_and_fetch_all(query=sql_command)
        if isinstance(resp, int):
            if resp != self.success:
                self.disp.log_error(
                    "Failed to fetch the data from the table.", title
                )
                return SCONST.GET_TABLE_SIZE_ERROR
            resp_list = []
        else:
            resp_list = resp
        if len(resp_list) == 0:
            self.disp.log_error(
                "There was no data returned by the query.", title
            )
            return SCONST.GET_TABLE_SIZE_ERROR
        if isinstance(resp_list[0], tuple) is False:
            self.disp.log_error("The data returned is not a tuple.", title)
            return SCONST.GET_TABLE_SIZE_ERROR
        return resp_list[0][0]

    def update_data_in_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: List[str], where: Union[str, List[str]] = "") -> int:
        """_summary_
            Update the data contained in a table.

        Args:
            table (str): _description_
            data (Union[List[List[str]], List[str]]): _description_
            column (List): _description_

        Returns:
            int: _description_
        """
        title = "update_data_in_table"
        msg = f"Updating the data contained in the table: {table}"
        self.disp.log_debug(msg, title)
        if column is None:
            column = ""

        # Only check table/column names for injection — data is parameterized
        check_items = [table]
        if isinstance(column, list):
            check_items.extend([str(c) for c in column])
        else:
            check_items.append(str(column))
        if self.sql_injection.check_if_injections_in_strings(check_items) or self.sql_injection.check_if_symbol_and_command_injection(where):
            self.disp.log_error("Injection detected.", "sql")
            return self.error

        if column == "":
            columns_raw = self.get_table_column_names(table)
            if isinstance(columns_raw, int):
                return self.error
            column = columns_raw

        # Ensure column is a List[str] for subsequent operations
        _tmp_cols2: Union[List[str], str] = self.sanitize_functions.escape_risky_column_names(
            column
        )
        if isinstance(_tmp_cols2, list):
            column = _tmp_cols2
        else:
            column = [str(_tmp_cols2)]

        if isinstance(column, str) and isinstance(data, str):
            data = [data]
            column = [column]
            column_length = len(column)

        column_length = len(column)
        self.disp.log_debug(
            f"data = {data}, column = {column}, length = {column_length}",
            title
        )

        where_sanitized = self.sanitize_functions.escape_risky_column_names_where_mode(
            where
        )
        if isinstance(where_sanitized, list):
            where = " AND ".join(where_sanitized)
        else:
            where = where_sanitized

        # Build SET clause with placeholders and parameter list
        set_parts: List[str] = []
        params: List[Union[str, None, int, float]] = []
        for i in range(column_length):
            set_parts.append(f"{column[i]} = ?")
            if i < len(data):
                v = data[i]
            else:
                v = None
            normalised_cell: Union[
                int,
                str,
                float,
                None
            ] = self._normalize_cell(v)
            self.disp.log_debug(f"Normalised cell: {normalised_cell}")
            params.append(normalised_cell)

        update_line = ", ".join(set_parts)
        sql_query = f"UPDATE {table} SET {update_line}"

        if where != "":
            sql_query += f" WHERE {where}"

        self.disp.log_debug(f"sql_query = '{sql_query}'", title)

        return self.sql_pool.run_editing_command(sql_query, params, table, "update")

    def insert_or_update_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], columns: Union[List[str], None] = None) -> int:
        """_summary_
            Insert or update data into a given table.

        Args:
            table (str): Table name.
            data (Union[List[List[str]], List[str]]): Data to insert or update.
            columns (Union[List[str], None], optional): Column names. Defaults to None.

        Returns:
            int: Success or error code.
        """
        title = "insert_or_update_data_into_table"
        self.disp.log_debug(
            "Inserting or updating data into the table.", title
        )

        check_list = [table]
        if columns:
            check_list.extend(columns)
        if self.sql_injection.check_if_injections_in_strings(check_list):
            self.disp.log_error("SQL Injection detected.", "sql")
            return self.error

        if columns is None:
            cols_raw = self.get_table_column_names(table)
            if isinstance(cols_raw, int):
                return self.error
            columns = cols_raw

        # ensure columns is a concrete list for downstream calls
        if columns is not None and not isinstance(columns, list):
            try:
                columns = list(columns)
            except Exception:
                columns = [str(columns)]

        table_content = self.get_data_from_table(
            table=table, column=columns, where="", beautify=False
        )
        # ensure table_content is iterable
        if isinstance(table_content, int):
            if table_content != self.success:
                self.disp.log_critical(
                    f"Failed to retrieve data from table {table}", title
                )
                return self.error
        table_content_list = table_content
        # table_content_list is now safe to iterate over (ensure runtime type for static checkers)
        if not isinstance(table_content_list, list):
            self.disp.log_error(
                f"Unexpected table content type for table {table}", title
            )
            return self.error

        if isinstance(data, list) and data and isinstance(data[0], list):
            self.disp.log_debug("Processing double data List", title)
            table_content_dict = {}
            for line in table_content_list:
                table_content_dict[str(line[0])] = line

            for line in data:
                if not line:
                    self.disp.log_warning("Empty line, skipping.", title)
                    continue
                # narrow type for the linter/typing
                if isinstance(line, str):
                    line_list: List = [line]
                elif not isinstance(line, list):
                    line_list: List = [line]
                else:
                    line_list = line
                node0 = str(line_list[0])
                if node0 in table_content_dict:
                    self.update_data_in_table(
                        table,
                        line_list,
                        columns,
                        f"{columns[0]} = {node0}"
                    )
                else:
                    # ensure column arg is a concrete list
                    if isinstance(columns, list):
                        cols: List = columns
                    else:
                        cols: List = [columns]
                    self.insert_data_into_table(table, line_list, cols)
            # finished processing multiple rows
            return self.success

        # Single-row processing
        if isinstance(data, list):
            self.disp.log_debug("Processing single data List", title)
            if not data:
                self.disp.log_warning("Empty data List, skipping.", title)
                return self.success

            node0 = str(data[0])
            # If a row with the same first-column key exists, update it
            for line in table_content_list:
                if str(line[0]) == node0:
                    return self.update_data_in_table(
                        table, data, columns, f"{columns[0]} = {node0}"
                    )

            # No existing row found — insert as new row
            if isinstance(columns, list):
                cols = columns
            else:
                cols = [columns]
            return self.insert_data_into_table(table, data, cols)

        # If we reach here, the input type was unexpected
        self.disp.log_error(
            "Data must be of type List[str] or List[List[str]]", title
        )
        return self.error

    def insert_or_update_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """Insert (create) or update an SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        title = "insert_or_update_trigger"
        self.disp.log_debug(
            f"Creating or replacing trigger: {trigger_name}", title
        )
        # --- SQL injection prevention ---
        if self.sql_injection.check_if_injections_in_strings([trigger_name, table_name]):
            self.disp.log_error("SQL injection detected.", title)
            return self.error

        if self.sql_injection.check_if_symbol_and_logic_gate_injection(timing_event):
            self.disp.log_error("SQL injection detected", title)
            return self.error
        # First, drop the existing trigger (if any)
        drop_result = self.remove_trigger(trigger_name)
        if drop_result not in (self.success, self.error):
            self.disp.log_warning(
                f"Unexpected drop_trigger result: {drop_result}", title
            )

        # Insert the new one
        return self.insert_trigger(trigger_name, table_name, timing_event, body)

    def remove_data_from_table(self, table: str, where: Union[str, List[str]] = "") -> int:
        """_summary_
            Remove the data from a table.
        Args:
            table (str): _description_
            data (List): _description_
            column (List): _description_

        Returns:
            int: _description_
        """
        self.disp.log_debug(
            f"Removing data from table {table}",
            "remove_data_from_table"
        )
        if self.sql_injection.check_if_sql_injection(table) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error

        if isinstance(where, List) is True:
            where = " AND ".join(where)

        sql_query = f"DELETE FROM {table}"

        if where != "":
            sql_query += f" WHERE {where}"

        self.disp.log_debug(
            f"sql_query = '{sql_query}'",
            "remove_data_from_table"
        )

        return self.sql_pool.run_editing_command(sql_query, [], table, "delete")

    def remove_table(self, table: str) -> int:
        """Drop/Remove (delete) a table from the SQLite database.

        Args:
            table (str): Name of the table to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to drop the ``users`` table:

            .. code-block:: python

                table_name = "users"
                result = await self.drop_table(table_name)

                if result == self.success:
                    print(f"Table '{table_name}' dropped successfully.")
                else:
                    print(f"Failed to drop table '{table_name}'.")

        Notes:
            - The method performs SQL injection detection on the table name.
            - If the table does not exist, no error is raised (uses ``DROP TABLE IF EXISTS`` internally).
        """
        title = "drop_table"
        self.disp.log_debug(f"Dropping table '{table}'", title)

        # --- SQL injection protection ---
        if self.sql_injection.check_if_injections_in_strings([table]):
            self.disp.log_error("Injection detected in table name.", title)
            return self.error

        try:
            # Escape quotes for safety
            table_safe = table.replace("'", "''")
            query = f"DROP TABLE IF EXISTS '{table_safe}';"
            self.disp.log_debug(f"Executing SQL: {query}", title)

            result = self.sql_pool.run_and_commit(query=query, values=[])
            if isinstance(result, int) and result == self.error:
                self.disp.log_error(f"Failed to drop table '{table}'", title)
                return self.error

            self.disp.log_info(f"Table '{table}' dropped successfully.", title)
            return self.success

        except mysql.connector.PoolError as oe:
            msg = f"OperationalError while dropping table '{table}': {oe}"
            self.disp.log_critical(msg, title)
            return self.error
        except mysql.connector.ProgrammingError as e:
            msg = f"SQL Error while dropping table '{table}': {e}"
            self.disp.log_critical(msg, title)
            return self.error
        except Exception as e:
            msg = f"Unexpected error while dropping table '{table}': {e}"
            self.disp.log_critical(msg, title)
            return self.error

    def remove_trigger(self, trigger_name: str) -> int:
        """Drop/Remove an existing SQL trigger if it exists.

        Args:
            trigger_name (str): Name of the trigger to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        title = "drop_trigger"
        self.disp.log_debug(f"Dropping trigger: {trigger_name}", title)

        if not trigger_name:
            self.disp.log_error("Trigger name cannot be empty.", title)
            return self.error

        # Sanitize to prevent injections
        if self.sql_injection.check_if_injections_in_strings([trigger_name]):
            self.disp.log_error(
                "SQL Injection detected in trigger name.", title
            )
            return self.error

        sql_query = f"DROP TRIGGER IF EXISTS {trigger_name};"
        self.disp.log_debug(f"Executing SQL:\n{sql_query}", title)

        result = self.sql_pool.run_editing_command(
            sql_query, [], trigger_name, "drop_trigger")
        if result != self.success:
            self.disp.log_error(
                f"Failed to drop trigger '{trigger_name}'.", title
            )
            return self.error

        self.disp.log_info(
            f"Trigger '{trigger_name}' dropped successfully.", title
        )
        return self.success
