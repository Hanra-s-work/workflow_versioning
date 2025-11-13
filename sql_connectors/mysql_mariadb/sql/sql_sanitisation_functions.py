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
# FILE: sql_sanitisation_functions.py
# CREATION DATE: 11-10-2025
# LAST Modified: 13:8:24 13-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File in charge of cleaning and sanitising sql queries before they are submitted to the database.
# // AR
# +==== END AsperHeader =================+
"""

import re
from typing import List, Dict, Any, Union, Optional, Tuple

from display_tty import Disp, initialise_logger

from . import sql_constants as SCONST
from .sql_time_manipulation import SQLTimeManipulation


class SQLSanitiseFunctions:
    """Provide functions to sanitize SQL queries before execution.

    This class contains methods to clean and escape SQL queries, ensuring
    they are safe to execute and free from injection vulnerabilities.

    Attributes:
        disp (Disp): Logger instance for debugging and error reporting.
        risky_keywords (List[str]): List of risky SQL keywords to sanitize.
        keyword_logic_gates (List[str]): List of logical operators to handle.
        none_value (str): Default value for NULL representation.
        sql_time_manipulation (SQLTimeManipulation): Handles time-related SQL operations.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the SQLSanitiseFunctions instance.

        Args:
            success (int, optional): Numeric success code. Defaults to 0.
            error (int, optional): Numeric error code. Defaults to 84.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.error: int = error
        self.debug: bool = debug
        self.success: int = success
        # --------------------------- logger section ---------------------------
        self.disp.update_disp_debug(self.debug)
        # ----------------- Database risky keyword sanitising  -----------------
        self.risky_keywords: List[str] = SCONST.RISKY_KEYWORDS
        self.keyword_logic_gates: List[str] = SCONST.KEYWORD_LOGIC_GATES
        # ---------------------- Time manipulation class  ----------------------
        self.sql_time_manipulation: SQLTimeManipulation = SQLTimeManipulation(
            self.debug
        )
        self.none_value: str = "NULL"

    def protect_sql_cell(self, cell: Optional[str]) -> str:
        """Escape characters in a SQL cell to prevent query breaking.

        Args:
            cell (Optional[str]): The cell to sanitize.

        Returns:
            str: Sanitized string safe for SQL queries.
        """
        if cell is None:
            return self.none_value
        result = ""
        for char in cell:
            if char in ("'", '"', "\\", '\0', "\r"):
                self.disp.log_info(
                    f"Escaped character '{char}' in '{cell}'.",
                    "protect_sql_cell"
                )
                result += "\\"+char
            else:
                result += char
        return result

    def escape_risky_column_names(self, columns: Union[List[str], str]) -> Union[List[str], str]:
        """Escape risky column names to prevent SQL injection.

        Args:
            columns (Union[List[str], str]): Column names to sanitize.

        Returns:
            Union[List[str], str]: Sanitized column names.
        """
        title = "_escape_risky_column_names"
        self.disp.log_debug("Escaping risky column names.", title)
        if isinstance(columns, str):
            data = [columns]
        else:
            data = columns
        for index, item in enumerate(data):
            if "=" in item:
                key, value = item.split("=", maxsplit=1)
                self.disp.log_debug(f"key = {key}, value = {value}", title)
                if key.lower() in self.risky_keywords:
                    self.disp.log_warning(
                        f"Escaping risky column name '{key}'.",
                        "_escape_risky_column_names"
                    )
                    data[index] = f"`{key}`={value}"
            elif item.lower() in self.risky_keywords:
                self.disp.log_warning(
                    f"Escaping risky column name '{item}'.",
                    "_escape_risky_column_names"
                )
                data[index] = f"`{item}`"
            else:
                continue
        self.disp.log_debug("Escaped risky column names.", title)
        if isinstance(columns, str):
            return data[0]
        return columns

    def _protect_value(self, value: Optional[str]) -> str:
        """Ensure a value is safely passed as a string in an SQL query.

        Args:
            value (Optional[str]): The value to protect.

        Returns:
            str: Protected value safe for SQL queries.
        """
        title = "_protect_value"
        self.disp.log_debug(f"protecting value: {value}", title)
        if value is None:
            self.disp.log_debug("Value is none, thus returning NULL", title)
            return self.none_value

        if isinstance(value, str) is False:
            self.disp.log_debug("Value is not a string, converting", title)
            value = str(value)

        if len(value) == 0:
            self.disp.log_debug("Value is empty, returning ''", title)
            return "''"

        if value[0] == '`' and value[-1] == '`':
            self.disp.log_debug(
                "string has special backtics, skipping.", title
            )
            return value

        if value[0] == "'":
            self.disp.log_debug(
                "Value already has a single quote at the start, removing", title
            )
            value = value[1:]
        if value[-1] == "'":
            self.disp.log_debug(
                "Value already has a single quote at the end, removing", title
            )
            value = value[:-1]

        self.disp.log_debug(
            f"Value before quote escaping: {value}", title
        )
        protected_value = value.replace("'", "''")
        self.disp.log_debug(
            f"Value after quote escaping: {protected_value}", title
        )

        protected_value = f"'{protected_value}'"
        self.disp.log_debug(
            f"Value after being converted to a string: {protected_value}.",
            title
        )
        return protected_value

    def escape_risky_column_names_where_mode(self, columns: Union[List[str], str]) -> Union[List[str], str]:
        """Escape risky column names in WHERE mode.

        Args:
            columns (Union[List[str], str]): Column names to sanitize.

        Returns:
            Union[List[str], str]: Sanitized column names.
        """
        title = "_escape_risky_column_names_where_mode"
        self.disp.log_debug(
            "Escaping risky column names in where mode.", title
        )

        if isinstance(columns, str):
            data = [columns]
        else:
            data = columns

        for index, item in enumerate(data):
            if "=" in item:
                key, value = item.split("=", maxsplit=1)
                self.disp.log_debug(f"key = {key}, value = {value}", title)

                protected_value = self._protect_value(value)
                if key.lower() not in self.keyword_logic_gates and key.lower() in self.risky_keywords:
                    self.disp.log_warning(
                        f"Escaping risky column name '{key}'.", title
                    )
                    data[index] = f"`{key}`={protected_value}"
                else:
                    data[index] = f"{key}={protected_value}"

            elif item.lower() not in self.keyword_logic_gates and item.lower() in self.risky_keywords:
                self.disp.log_warning(
                    f"Escaping risky column name '{item}'.",
                    title
                )
                protected_value = self._protect_value(item)
                data[index] = protected_value

        self.disp.log_debug("Escaped risky column names in where mode.", title)

        if isinstance(columns, str):
            return data[0]
        return data

    def check_sql_cell(self, cell: Union[str, int, float, None], raw: bool = True) -> Union[str, Union[str, int, float, None]]:
        """Check and sanitize a SQL cell value.

        Args:
            cell (Union[str, int, float, None]): The cell value to check.
            raw (bool, optional): Whether to process raw values. Defaults to True.

        Returns:
            Union[str, Union[str, int, float, None]]: Sanitized cell value.
        """
        title: str = "check_sql_cell"
        cell_cleaned = None
        if raw and isinstance(cell, (float, int)):
            return cell
        if raw and cell is None:
            return cell
        if isinstance(cell, (str, float, int)) is True:
            cell_cleaned = str(cell)
        if isinstance(cell, str) is False:
            msg = "The expected type of the input is a string,"
            msg += f"but got {type(cell)}"
            self.disp.log_error(msg, title)
            return str(cell)
        cell = self.protect_sql_cell(cell_cleaned)
        tmp = cell.lower()
        if tmp in ("now", "now()"):
            tmp = self.sql_time_manipulation.get_correct_now_value()
        elif tmp in ("current_date", "current_date()"):
            tmp = self.sql_time_manipulation.get_correct_current_date_value()
        else:
            tmp = str(cell)
        if ";base" not in tmp:
            self.disp.log_debug(f"result = {tmp}", title)
        return f"\"{str(tmp)}\""

    def beautify_table(self, column_names: List[str], table_content: List[List[Any]]) -> Union[List[Dict[str, Any]], int]:
        """Convert raw table rows to a list of dictionaries keyed by column.

        Args:
            column_names (List[str]): Column descriptors (name as first item).
            table_content (List[List[Any]]): Raw rows as sequences.

        Returns:
            Union[List[Dict[str, Any]], int]: Beautified table or error code.
        """
        data: List[Dict[str, Any]] = []
        v_index: int = 0
        if len(column_names) == 0:
            self.disp.log_error(
                "There are no provided table column names.",
                "_beautify_table"
            )
            return self.error
        if len(table_content) == 0:
            self.disp.log_error(
                "There is no table content.",
                "_beautify_table"
            )
            return self.error
        column_length = len(column_names)
        for i in table_content:
            cell_length = len(i)
            if cell_length != column_length:
                self.disp.log_warning(
                    "Table content and column lengths do not correspond.",
                    "_beautify_table"
                )
            data.append({})
            for index, items in enumerate(column_names):
                if index == cell_length:
                    self.disp.log_warning(
                        "Skipping the rest of the tuple because it is shorter than the column names.",
                        "_beautify_table"
                    )
                    break
                data[v_index][items[0]] = i[index]
            v_index += 1
        self.disp.log_debug(f"beautified_table = {data}", "_beautify_table")
        return data

    def compile_update_line(self, line: List, column: List, column_length: int) -> str:
        """Compile the line required for an SQL update to work.

        Args:
            line (List): Data line to compile.
            column (List): Column names.
            column_length (int): Number of columns.

        Returns:
            str: Compiled SQL update line.
        """
        title = "compile_update_line"
        final_line = ""
        self.disp.log_debug("Compiling update line.", title)
        for i in range(0, column_length):
            cell_content = self.check_sql_cell(line[i])
            final_line += f"{column[i]} = {cell_content}"
            if i < column_length - 1:
                final_line += ", "
            if i == column_length:
                break
        self.disp.log_debug(f"line = {final_line}", title)
        return final_line

    def _process_single_sql_line(self, line: List[Union[str, int, float, None]], column_length: int) -> Tuple[str, List[Union[str, int, float, None]]]:
        """Process a single SQL value line while preserving column logic.

        Args:
            line (List[Union[str, int, float, None]]): Data line to process.
            column_length (int): Number of columns.

        Returns:
            Tuple[str, List[Union[str, int, float, None]]]: Placeholder string and values.
        """
        title: str = "_process_single_sql_line"
        if not isinstance(line, list):
            line = [line]
        line_length = len(line)

        placeholders: List[str] = []
        values: List[Union[str, int, float, None]] = []

        if self.debug and ";base" not in str(line):
            self.disp.log_debug(f"line = {line}", title)

        for i in range(column_length):
            if i >= line_length:
                msg = (
                    f"Line shorter than expected (columns={column_length}, data={line_length}). "
                    f"Missing columns will not be inserted beyond index {i}."
                )
                self.disp.log_warning(msg, title)
                break

            checked_value = self.check_sql_cell(line[i], raw=True)
            values.append(checked_value)
            placeholders.append("%s")

            if i == column_length - 1 and line_length > column_length:
                msg = (
                    f"The line is longer than the number of columns ({line_length} > {column_length}), "
                    f"truncating excess values."
                )
                self.disp.log_warning(msg, title)
                break

        line_placeholder = "(" + ", ".join(placeholders) + ")"

        if self.debug:
            msg = f"line_placeholder = '{line_placeholder}', type = {type(line_placeholder)}"
            self.disp.log_debug(msg, title)
            self.disp.log_debug(f"values = {values}", title)

        tuple_version = [line_placeholder, values]
        return tuple(tuple_version)

    def process_sql_line(self, line: Union[str, int, float, List[Union[str, int, float, None]], List[List[Union[str, int, float, None]]], None], column: List[str], column_length: int = -1) -> Tuple[str, List[Union[str, int, float, None]]]:
        """Convert a dataset to MySQL/MariaDB-safe placeholders.

        Args:
            line (Union[str, int, float, List, None]): Data to process.
            column (List[str]): Column names.
            column_length (int, optional): Number of columns. Defaults to -1.

        Returns:
            Tuple[str, List[Union[str, int, float, None]]]: Placeholder string and values.
        """
        title: str = "process_sql_line"

        if column_length == -1:
            column_length = len(column)

        if not isinstance(line, list):
            line = [line]

        results: List[str] = []
        all_values: List[Union[str, int, float, None]] = []

        processed_list_instances: int = 0

        # Case 1: multi-row data (list of lists)
        if isinstance(line, list) and len(line) > 0 and isinstance(line[0], list):
            for row in line:
                if isinstance(row, list):
                    placeholders, vals = self._process_single_sql_line(
                        row, column_length
                    )
                    results.append(placeholders)
                    all_values.extend(vals)
                    processed_list_instances += 1
                else:
                    raise RuntimeError(
                        "Incorrect data format, aborting process")
            line_final: str = ", ".join(results)
            if self.debug:
                self.disp.log_debug(
                    f"Final placeholder string = '{line_final}'", title)
                self.disp.log_debug(f"Total values = {len(all_values)}", title)

            return line_final, all_values

        #  Case 2: single-row data
        if isinstance(line, list) and not isinstance(line[0], list):
            buffer: str = "("
            for index, row in enumerate(line):
                if self.debug and ";base" not in str(row):
                    self.disp.log_debug(f"row = {row}", title)

                if not isinstance(row, list):
                    checked_value = self.check_sql_cell(row, raw=True)
                    all_values.append(checked_value)
                    buffer += "%s"
                else:
                    raise RuntimeError(
                        "Incorrect data format, aborting process"
                    )

                if index - processed_list_instances < column_length - 1:
                    buffer += ", "

                if index - processed_list_instances == column_length - 1:
                    if index - processed_list_instances < len(line) - 1:
                        msg = (
                            "The line is longer than the number of columns, truncating."
                        )
                        self.disp.log_warning(msg, title)
                    break

            buffer += ")"
            if buffer not in ("()", ""):
                results.append(buffer)

        line_final: str = ", ".join(results)

        if self.debug:
            self.disp.log_debug(
                f"Final placeholder string = '{line_final}'", title
            )
            self.disp.log_debug(f"Total values = {len(all_values)}", title)

        return line_final, all_values

    def _check_for_double_query_in_trigger(self, sql: str, table_name: str) -> Union[int, str]:
        """Check for double queries in a trigger.

        Args:
            sql (str): SQL trigger statement.
            table_name (str): Name of the table.

        Returns:
            Union[int, str]: Validated SQL trigger or error code.
        """
        title: str = "_check_for_double_query"
        # --- Safety validation layer ---
        normalized_lower = sql.lower()

        # 1. Only one CREATE TRIGGER allowed
        if len(re.findall(r"\bcreate\s+trigger\b", normalized_lower)) > 1:
            self.disp.log_error(
                "Multiple CREATE TRIGGER statements detected.", title
            )
            return self.error

        # 2. Disallow dangerous DDL keywords (basic whitelist)
        for keyword in SCONST.SQL_RISKY_DDL_TRIGGER_KEYWORDS:
            if keyword in normalized_lower:
                self.disp.log_error(
                    f"Unsafe keyword '{keyword.strip()}' detected in trigger SQL.", title
                )
                return self.error

        # 3. Ensure trigger table isn't a system schema
        if re.match(r"(?i)^(mysql|information_schema|performance_schema|sys)\.", table_name):
            self.disp.log_error(
                "Trigger cannot be created on system schema tables.", title)
            return self.error

        # 4. Check BEGIN/END pairing (simple count balance)
        begin_count = normalized_lower.count("begin")
        end_count = normalized_lower.count("end")
        if begin_count != end_count:
            self.disp.log_error(
                f"Unbalanced BEGIN/END block ({begin_count} BEGIN vs {end_count} END).", title
            )
            return self.error

        # 5. Warn if multiple statements outside BEGIN...END
        if begin_count == 0 and sql.count(";") > 1:
            self.disp.log_warning(
                "Multiple SQL statements found outside BEGIN/END. "
                "MySQL triggers only support one statement unless wrapped.",
                title
            )

        # --- Final shape sanity check ---
        if not re.match(r"(?i)^CREATE\s+TRIGGER\s+[`\"\w]+", sql):
            self.disp.log_error("Malformed CREATE TRIGGER statement.", title)
            return self.error
        return sql

    def clean_trigger_creation(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> Union[str, int]:
        """Clean and validate SQL trigger creation.

        Args:
            trigger_name (str): Name of the trigger.
            table_name (str): Name of the table.
            timing_event (str): Timing event for the trigger.
            body (str): Trigger body.

        Returns:
            Union[str, int]: Validated SQL trigger or error code.
        """
        title = "clean_trigger_creation"

        if not all([trigger_name, table_name, timing_event, body]):
            self.disp.log_error("All parameters must be provided.", title)
            return self.error

        sql = body.strip()
        self.disp.log_debug(f"Raw trigger SQL received: {sql[:200]}...", title)

        # --- Detect if user already passed a full CREATE TRIGGER ---
        if not re.match(r"(?i)^\s*CREATE\s+TRIGGER\b", sql):
            # Auto-wrap body inside CREATE TRIGGER template
            sql = (
                f"CREATE TRIGGER `{trigger_name}` "
                f"{timing_event} ON `{table_name}` "
                f"FOR EACH ROW {sql}"
            )
            self.disp.log_debug(
                f"Wrapped raw body into CREATE TRIGGER template:\n{sql}", title
            )

        # --- Normalize and clean syntax ---
        # 1. Remove unsupported IF NOT EXISTS
        sql = re.sub(
            r"(?i)\bCREATE\s+TRIGGER\s+IF\s+NOT\s+EXISTS\b",
            "CREATE TRIGGER",
            sql
        )

        # 2. Remove MySQL CLI delimiters like DELIMITER // or DELIMITER ;;
        sql = re.sub(r"(?im)^\s*DELIMITER\s+\S+\s*$", "", sql)

        # 3. Normalize END delimiters like END$$ or END// to END;
        sql = re.sub(r"(?s)\s*END\s*[\$;/]+\s*$", "END;", sql)

        # 4. Collapse multiple spaces
        sql = re.sub(r"[ \t]+", " ", sql).strip()

        # 5. Sanity check final structure
        if not re.match(r"(?i)^CREATE\s+TRIGGER\s+[`\"\w]+", sql):
            self.disp.log_error(
                f"Malformed trigger SQL after cleaning → {sql[:80]}", title
            )
            return self.error

        self.disp.log_debug(f"Normalized trigger SQL:\n{sql}", title)

        return self._check_for_double_query_in_trigger(sql, table_name)
