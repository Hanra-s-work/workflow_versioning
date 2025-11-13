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
# FILE: sql_connections.py
# CREATION DATE: 11-10-2025
# LAST Modified: 13:3:54 13-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File in charge of containing the class that will manage the sql connections.
# // AR
# +==== END AsperHeader =================+
"""


from typing import Union, Any, List, Optional
from threading import RLock

import mysql
import mysql.connector
import mysql.connector.cursor
from display_tty import Disp, initialise_logger

from . import sql_constants as SCONST
from ..components import constants as CONST


class SQLManageConnections:
    """
    Async connection manager for SQL using `mysql`.

    Provides a small, async-friendly facade around an
    :class:`mysql.Pool` instance. Access is serialized using an

    Attributes:
        disp (Disp): Logger instance for debugging and error reporting.
        error (int): Numeric error code.
        success (int): Numeric success code.
        debug (bool): Debug mode flag.
        url (str): Host or URL string.
        port (int): Port number.
        username (str): Username for the database.
        password (str): Password for the database.
        db_name (str): Name of the database to connect to.
        pool_parameters (dict): Configuration for the connection pool.
        pool (Optional[mysql.connector.pooling.MySQLConnectionPool]): Connection pool instance.
    """

    # Initialise the logger globally in the class.
    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(
        self,
        url: str,
        port: int,
        username: str,
        password: str,
        db_name: str,
        success: int = 0,
        error: int = 84,
        debug: bool = False,
    ) -> None:
        """
        Initialize the connection manager instance.

        Args:
            url (str): Host or URL string.
            port (int): Port number.
            username (str): Username for the database.
            password (str): Password for the database.
            db_name (str): Name of the database to connect to.
            success (int, optional): Success return code. Defaults to 0.
            error (int, optional): Error return code. Defaults to 84.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        # -------------------------- Inherited values --------------------------
        self.error: int = error
        self.debug: bool = debug
        self.success: int = success
        self.url: str = url
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.db_name: str = db_name
        # --------------------------- logger section ---------------------------
        self.disp.update_disp_debug(self.debug)
        # ------------------------ thread lock tracker  ------------------------
        self._lock: RLock = RLock()
        # -------------------------- Pool parameters  --------------------------
        self.pool_parameters = {
            "pool_name": CONST.DATABASE_POOL_NAME,
            "pool_size": CONST.DATABASE_MAX_POOL_CONNECTIONS,
            "pool_reset_session": CONST.DATABASE_RESET_POOL_NODE_CONNECTION,
            "user": self.username,
            "password": self.password,
            "host": self.url,
            "port": self.port,
            "database": self.db_name,
            "collation": CONST.DATABASE_COLLATION,
            "connection_timeout": CONST.DATABASE_CONNECTION_TIMEOUT,
            "allow_local_infile": CONST.DATABASE_LOCAL_INFILE,
            "init_command": CONST.DATABASE_INIT_COMMAND,
            "option_files": CONST.DATABASE_DEFAULT_FILE,  # type error
            "autocommit": CONST.DATABASE_AUTOCOMMIT,
            "ssl_disabled": not CONST.DATABASE_SSL,
            "ssl_key": CONST.DATABASE_SSL_KEY,
            "ssl_cert": CONST.DATABASE_SSL_CERT,
            "ssl_ca": CONST.DATABASE_SSL_CA,
            "ssl_cipher": CONST.DATABASE_SSL_CIPHER,
            "ssl_verify_cert": CONST.DATABASE_SSL_VERIFY_CERT
        }
        # ---------------- variables containing the connection  ----------------
        self.pool: Union[
            None,
            mysql.connector.pooling.MySQLConnectionPool
        ] = None

    def show_connection_info(self, func_name: str = "show_connection_info") -> None:
        """
        Log connection metadata for debugging.

        This method does not perform any I/O; it only logs the configured
        connection information (database filename, host/url, and port) via the
        project's logging helper.

        Args:
            func_name (str): Optional title used in the logger.
        """
        msg = "\n"
        for key, value in self.pool_parameters.items():
            msg += f"{key} = '{value}': Type: {type(value)}\n"
        self.disp.log_debug(msg, func_name)

    def initialise_pool(self) -> int:
        """
        Initialize a connection pool for the database.

        Raises:
            RuntimeError: If the pool initialization fails.

        Returns:
            int: `self.success` if the function succeeds, otherwise raises an error.
        """
        title = "initialise_pool"
        self.disp.log_debug("Initialising the connection pool.", title)
        try:
            self.pool_parameters = {
                "pool_name": CONST.DATABASE_POOL_NAME,
                "pool_size": CONST.DATABASE_MAX_POOL_CONNECTIONS,
                "pool_reset_session": CONST.DATABASE_RESET_POOL_NODE_CONNECTION,
                "user": self.username,
                "password": self.password,
                "host": self.url,
                "port": self.port,
                "database": self.db_name,
                "collation": CONST.DATABASE_COLLATION,
                "connection_timeout": CONST.DATABASE_CONNECTION_TIMEOUT,
                "allow_local_infile": CONST.DATABASE_LOCAL_INFILE,
                "init_command": CONST.DATABASE_INIT_COMMAND,
                "option_files": CONST.DATABASE_DEFAULT_FILE,  # type error
                "autocommit": CONST.DATABASE_AUTOCOMMIT,
                "ssl_disabled": not CONST.DATABASE_SSL,
                "ssl_key": CONST.DATABASE_SSL_KEY,
                "ssl_cert": CONST.DATABASE_SSL_CERT,
                "ssl_ca": CONST.DATABASE_SSL_CA,
                "ssl_cipher": CONST.DATABASE_SSL_CIPHER,
                "ssl_verify_cert": CONST.DATABASE_SSL_VERIFY_CERT
            }
            for i in SCONST.UNWANTED_ARGUMENTS:
                if i in self.pool_parameters and self.pool_parameters[i] is None:
                    self.disp.log_debug(
                        f"Removed '{i}' from the pool parameters.", title
                    )
                    self.pool_parameters.pop(i)
            self.show_connection_info(title)
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                **self.pool_parameters
            )
            return self.success
        except mysql.connector.errors.ProgrammingError as pe:
            msg = "ProgrammingError: The pool could not be initialized."
            msg += f"Original error: {str(pe)}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from pe
        except mysql.connector.errors.IntegrityError as ie:
            msg = "IntegrityError: Integrity issue while initializing the pool."
            msg += f" Original error: {str(ie)}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from ie
        except mysql.connector.errors.OperationalError as oe:
            msg = "OperationalError: Operational error occurred during pool initialization."
            msg += f" Original error: {str(oe)}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = "MySQL Error: An unexpected error occurred during pool initialization."
            msg += f"Original error: {str(e)}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e

    def get_connection(self) -> mysql.connector.pooling.PooledMySQLConnection:
        """
        Retrieve a connection from the pool.

        Returns:
            mysql.connector.pooling.PooledMySQLConnection: A pooled connection instance.

        Raises:
            RuntimeError: If the connection pool is not initialized or an error occurs.
        """
        title = "get_connection"
        if self.pool is None:
            raise RuntimeError("Connection pool is not initialized.")
        try:
            self.disp.log_debug("Getting an sql connection", title)
            return self.pool.get_connection()
        except mysql.connector.errors.OperationalError as oe:
            msg = "OperationalError: Could not retrieve a connection from the pool."
            msg += f" Original error: {str(oe)}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = "MySQL Error: An unexpected error occurred while getting the connection."
            msg += f" Original error: {str(e)}"
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e

    def get_cursor(self, connection: mysql.connector.pooling.PooledMySQLConnection) -> mysql.connector.cursor.MySQLCursor:
        """
        Retrieve a cursor from the given connection.

        Args:
            connection (mysql.connector.pooling.PooledMySQLConnection): The active connection.

        Returns:
            mysql.connector.cursor.MySQLCursor: The cursor object.

        Raises:
            RuntimeError: If the connection is not active.
        """
        if not self.is_connection_active(connection):
            raise RuntimeError("Cannot get cursor, connection is not active.")
        return connection.cursor()

    def close_cursor(self, cursor: mysql.connector.cursor.MySQLCursor) -> int:
        """
        Close the given cursor.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): The cursor to close.

        Returns:
            int: `self.success` if the cursor is closed successfully, otherwise `self.error`.
        """
        title = "close_cursor"
        self.disp.log_debug("Closing cursor, if it is open.", title)
        if self.is_cursor_active(cursor):
            self.disp.log_debug("Closing cursor", title)
            if cursor.close():
                return self.success
            return self.error
        self.disp.log_error(
            "The cursor did not have an active connection.", title
        )
        return self.error

    def return_connection(self, connection: mysql.connector.pooling.PooledMySQLConnection) -> int:
        """
        Return a connection to the pool by closing it.

        Args:
            connection (mysql.connector.pooling.PooledMySQLConnection): The connection to close.

        Returns:
            int: `self.success` if the connection is closed successfully, otherwise `self.error`.
        """
        title = "return_connection"
        self.disp.log_debug("Closing a database connection.", title)
        if self.is_connection_active(connection):
            self.disp.log_debug("Connection has been closed.", title)
            connection.close()
            return self.success
        self.disp.log_error(
            "Connection was not open in the first place.", title
        )
        return self.error

    def destroy_pool(self) -> int:
        """
        Destroy the connection pool.

        Returns:
            int: `self.success` if the pool is destroyed successfully, otherwise `self.error`.
        """
        title = "destroy_pool"
        self.disp.log_debug("Destroying pool, if it exists.", title)
        if self.pool is not None:
            self.disp.log_debug("Destroying pool.", title)
            del self.pool
            self.pool = None
        self.disp.log_warning("There was no pool to be destroyed.", title)
        return self.success

    def release_connection_and_cursor(self, connection: Union[mysql.connector.pooling.PooledMySQLConnection, None], cursor: Union[mysql.connector.cursor.MySQLCursor, None] = None) -> None:
        """
        Release both the connection and cursor.

        Args:
            connection (Optional[mysql.connector.pooling.PooledMySQLConnection]): The connection to release.
            cursor (Optional[mysql.connector.cursor.MySQLCursor]): The cursor to release.
        """
        title = "release_connection_and_cursor"
        msg = "Connections have ended with status: "
        self.disp.log_debug("Closing cursor.", title)
        if cursor is not None:
            status = self.close_cursor(cursor)
            msg += f"cursor = {status}, "
        self.disp.log_debug("Closing connection.", title)
        if connection is not None:
            status = self.return_connection(connection)
            msg += f"connection = {status}"
        self.disp.log_debug(msg, title)

    def run_and_commit(self, query: str, values: Optional[List[Union[str, int, float, None]]] = None, cursor: Union[mysql.connector.cursor.MySQLCursor, None] = None) -> int:
        """
        Execute a query and commit changes.

        Args:
            query (str): The SQL query to execute.
            values (Optional[List[Union[str, int, float, None]]]): Values to bind to the query.
            cursor (Optional[mysql.connector.cursor.MySQLCursor]): The cursor to use for execution.

        Returns:
            int: `self.success` if the query executes successfully, otherwise `self.error`.
        """
        title = "run_and_commit"
        self.disp.log_debug("Running and committing sql query.", title)
        if cursor is None:
            self.disp.log_debug("No cursor found, generating one.", title)
            connection = self.get_connection()
            if connection is None:
                self.disp.log_critical(SCONST.CONNECTION_FAILED, title)
                return self.error
            internal_cursor = self.get_cursor(connection)
            if internal_cursor is None:
                self.disp.log_critical(SCONST.CURSOR_FAILED, title)
                return self.error
        else:
            self.disp.log_debug("Cursor found, using it.", title)
            internal_cursor = cursor
        try:
            self.disp.log_debug(f"Executing query: {query}.", title)
            internal_cursor.execute(query, params=values)
            self.disp.log_debug("Committing content.", title)
            con: Optional[mysql.connector.MySQLConnection] = getattr(
                internal_cursor, "_connection", None)
            if con:
                con.commit()
            else:
                self.disp.log_warning(
                    "No internal cursor found, skipping manual commit.", title
                )
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            return self.success
        except mysql.connector.errors.ProgrammingError as pe:
            msg = "ProgrammingError: Failed to execute the query."
            msg += f" Original error: {str(pe)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from pe
        except mysql.connector.errors.IntegrityError as ie:
            msg = "IntegrityError: Integrity constraint issue occurred during query execution."
            msg += f" Original error: {str(ie)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from ie
        except mysql.connector.errors.OperationalError as oe:
            msg = "OperationalError: Operational error occurred during query execution."
            msg += f" Original error: {str(oe)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = "MySQL Error: An unexpected error occurred during query execution."
            msg += f" Original error: {str(e)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from e

    def run_and_fetch_all(self, query: str, values: Optional[List[Union[str, int, float]]] = None, cursor: Union[mysql.connector.cursor.MySQLCursor, None] = None) -> Union[int, Any]:
        """
        Execute a SELECT-style query and return fetched rows.

        Args:
            query (str): The SQL SELECT statement to execute.
            values (Optional[List[Union[str, int, float]]]): Values to bind to the query.
            cursor (Optional[mysql.connector.cursor.MySQLCursor]): The cursor to use for execution.

        Returns:
            Union[int, Any]: The fetched rows (usually a List[tuple]) or `self.error` on failure.
        """
        title = "run_and_fetchall"
        if cursor is None:
            connection = self.get_connection()
            if connection is None:
                self.disp.log_critical(SCONST.CONNECTION_FAILED, title)
                return self.error
            internal_cursor = self.get_cursor(connection)
            if internal_cursor is None:
                self.disp.log_critical(SCONST.CURSOR_FAILED, title)
                return self.error
        else:
            internal_cursor = cursor
        try:
            self.disp.log_debug(
                f"Executing query: {query}, values: {values}.", title)
            internal_cursor.execute(query, params=values)
            if internal_cursor is None or internal_cursor.description is None:
                self.disp.log_error(
                    "Failed to gather data from the table, cursor is invalid.", title
                )
                if cursor is None:
                    self.disp.log_debug(
                        "The cursor was generated by us, releasing.", title
                    )
                    self.release_connection_and_cursor(
                        connection, internal_cursor
                    )
                else:
                    self.disp.log_debug(
                        "The cursor was provided, not releasing.", title
                    )
                return self.error
            self.disp.log_debug(
                "Storing a copy of the content of the cursor.", title
            )
            raw_data = internal_cursor.fetchall()
            self.disp.log_debug(f"Raw gathered data {raw_data}", title)
            data = raw_data.copy()
            self.disp.log_debug(f"Data gathered: {data}.", title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            return data
        except mysql.connector.errors.ProgrammingError as pe:
            msg = "ProgrammingError: Failed to execute the query."
            msg += f" Original error: {str(pe)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from pe
        except mysql.connector.errors.IntegrityError as ie:
            msg = "IntegrityError: Integrity constraint issue occurred during query execution."
            msg += f" Original error: {str(ie)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from ie
        except mysql.connector.errors.OperationalError as oe:
            msg = "OperationalError: Operational error occurred during query execution."
            msg += f" Original error: {str(oe)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = "MySQL Error: An unexpected error occurred during query execution."
            msg += f" Original error: {str(e)}"
            self.disp.log_error(msg, title)
            if cursor is None:
                self.disp.log_debug(
                    "The cursor was generated by us, releasing.", title
                )
                self.release_connection_and_cursor(connection, internal_cursor)
            else:
                self.disp.log_debug(
                    "The cursor was provided, not releasing.", title
                )
            raise RuntimeError(msg) from e

    def run_editing_command(self, sql_query: str, values: Optional[List[Union[str, int, float, None]]] = None, table: str = "<not_specified>", action_type: str = "update") -> int:
        """
        Execute an editing command (e.g., INSERT, UPDATE, DELETE).

        Args:
            sql_query (str): The SQL query to execute.
            values (Optional[List[Union[str, int, float, None]]]): Values to bind to the query.
            table (str): The name of the table being modified.
            action_type (str): The type of action being performed (e.g., "update").

        Returns:
            int: `self.success` if the command executes successfully, otherwise `self.error`.
        """
        title = "_run_editing_command"
        try:
            resp = self.run_and_commit(query=sql_query, values=values)
            if resp != self.success:
                self.disp.log_error(
                    f"Failed to {action_type} data in '{table}'.", title
                )
                return self.error
            self.disp.log_debug("command ran successfully.", title)
            return self.success
        except mysql.connector.Error as e:
            self.disp.log_error(
                f"Failed to {action_type} data in '{table}': {str(e)}", title
            )
            return self.error

    def __del__(self) -> None:
        """_summary_
            Destructor
        """
        self.destroy_pool()

    def is_pool_active(self) -> bool:
        """
        Check if the connection pool is active.

        Returns:
            bool: True if the pool is active, False otherwise.
        """
        title = "is_pool_active"
        self.disp.log_debug("Checking if the connection is active.", title)
        resp = self.pool is not None
        if resp:
            self.disp.log_debug("The connection is active.", title)
            return True
        self.disp.log_error("The connection is not active.", title)
        return False

    def is_connection_active(self, connection: mysql.connector.pooling.PooledMySQLConnection) -> bool:
        """
        Check if the connection is active.

        Args:
            connection (mysql.connector.pooling.PooledMySQLConnection): The connection to check.

        Returns:
            bool: True if the connection is active, False otherwise.
        """
        title = "is_connection_active"
        self.disp.log_debug(
            "Checking if the connection is active.", title
        )
        try:
            if connection:
                connection.ping(reconnect=False)
                self.disp.log_debug("The connection is active.", title)
                return True
        except (mysql.connector.Error, mysql.connector.errors.Error):
            self.disp.log_error("The connection is not active.", title)
            return False
        self.disp.log_error("The connection is not active.", title)
        return False

    def is_cursor_active(self, cursor: mysql.connector.cursor.MySQLCursor) -> bool:
        """
        Check if the cursor is active.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): The cursor to check.

        Returns:
            bool: True if the cursor is active, False otherwise.
        """
        title = "is_cursor_active"
        self.disp.log_debug(
            "Checking if the provided cursor is active.", title
        )
        self.disp.log_debug(f"Content of the cursor: {dir(cursor)}.", title)
        con = getattr(cursor, "_connection", None)
        resp = cursor is not None and con is not None
        if resp:
            self.disp.log_debug("The cursor is active.", title)
            return True
        self.disp.log_error("The cursor is not active.", title)
        return False
