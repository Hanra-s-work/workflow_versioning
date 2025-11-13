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
# FILE: sql_injection.py
# CREATION DATE: 11-10-2025
# LAST Modified: 12:25:32 10-11-2025
# DESCRIPTION:
# SQL injection detection module for backend connectors.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Detect, log, and prevent SQL injection attempts.
# // AR
# +==== END AsperHeader =================+
"""

import re
import base64
import binascii
from typing import Union, List, Dict, Any, Callable, Sequence, overload

from display_tty import Disp, initialise_logger

from .sql_constants import RISKY_KEYWORDS, KEYWORD_LOGIC_GATES


class SQLInjection:
    """Helpers to detect likely SQL injection attempts.

    The class exposes small predicate helpers that scan strings (or
    nested lists of strings) for symbols, keywords or logical operators
    typically used in SQL injections. Callers should treat a ``True``
    return value as an indication the input is potentially dangerous.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """Initialize the SQLInjection helper.

        Args:
            error (int): Numeric error code returned by helper predicates.
            success (int): Numeric success code (unused by predicates).
            debug (bool): Enable debug logging when True.
        """
        # ---------------------------- Status codes ----------------------------
        self.debug: bool = debug
        self.error: int = error
        self.success: int = success
        # ---------------------------- Logging data ----------------------------
        self.disp.update_disp_debug(self.debug)
        # --------------------- Injection status variables ---------------------
        self.injection_err: int = (-1)
        self.injection_message: str = "Injection attempt detected"
        # ------------------------ base64 trigger check ------------------------
        self.base64_key: str = ";base64"
        # ----------------------- compiled regex indexes -----------------------
        self.all_key: str = "all"
        self.symbols_key: str = "symbols"
        self.keywords_key: str = "keywords"
        self.logic_gates_key: str = "logic_gates"
        # ------------------ Injection checking related data  ------------------
        _base_symbols: List[str] = [
            ';', '--', '/*', '*/',
            '#', '@@', '@', "'", '"', '`', '||'
        ]
        _base_keywords: List[str] = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE',
            'DROP', 'CREATE', 'ALTER', 'TABLE', 'UNION', 'JOIN', 'WHERE'
        ]
        _base_keywords.extend(RISKY_KEYWORDS)
        _base_logic_gates: List[str] = ['OR', 'AND', 'NOT']
        _base_logic_gates.extend(KEYWORD_LOGIC_GATES)
        # --------------------- Sanitise checking material ---------------------
        self.symbols = self._sanitize_class_checking_material(_base_symbols)
        self.keywords = self._sanitize_class_checking_material(_base_keywords)
        self.command: List[str] = self.keywords
        self.logic_gates = self._sanitize_class_checking_material(
            _base_logic_gates
        )
        # -------------------------- Process regexes  --------------------------
        self.regex_map: Dict[str, Any] = {
            self.symbols_key: self._compile_patterns(self.symbols),
            self.keywords_key: self._compile_patterns(self.keywords),
            self.logic_gates_key: self._compile_patterns(self.logic_gates),
        }
        # ------- Create an instance containing all the sanitised checks -------
        self.all: List[str] = []
        self.all.extend(self.symbols)
        self.all.extend(self.keywords)
        self.all.extend(self.logic_gates)
        self.regex_map[self.all_key] = self._compile_patterns(self.all)
        # ------------------- Negative (safe) test patterns  -------------------
        self.safe_patterns = [
            r"order\s?by\s?(asc|desc)?",    # legitimate ORDER BY use
            r"selective",                   # word containing 'select'
            r"unionized",                   # word containing 'union'
        ]
        self.safe_regexes: List[re.Pattern] = []
        for pat in self.safe_patterns:
            self.safe_regexes.append(re.compile(pat, re.IGNORECASE))

    # ============================== UTILITIES ============================== #

    @overload
    def _sanitize_class_checking_material(
        self,
        material_raw: str
    ) -> str: ...

    @overload
    def _sanitize_class_checking_material(
        self,
        material_raw: List[str]
    ) -> List[str]: ...

    def _sanitize_class_checking_material(self, material_raw: Union[List[str], str]) -> Union[List[str], str]:
        if isinstance(material_raw, list):
            result = []
            for i in material_raw:
                if isinstance(i, str):
                    result.append(i.lower())
                else:
                    result.append(i)
            return result
        if isinstance(material_raw, str):
            return material_raw.lower()
        return material_raw

    @overload
    def _sanitize_usr_input(
        self,
        material_raw: str
    ) -> str: ...

    @overload
    def _sanitize_usr_input(
        self,
        material_raw: List[str]
    ) -> List[str]: ...

    def _sanitize_usr_input(self, material_raw: Union[List[str], str]) -> Union[List[str], str]:
        if isinstance(material_raw, list):
            result = []
            for i in material_raw:
                if isinstance(i, str):
                    result.append(i.lower())
                else:
                    result.append(i)
            return result
        if isinstance(material_raw, str):
            return material_raw.lower()
        return material_raw

    def _compile_patterns(self, tokens: List[str]) -> List[re.Pattern]:
        """Precompile regex patterns with heuristics for boundary usage."""
        patterns = []
        for token in tokens:
            escaped = re.escape(token)
            has_special = False
            for c in token:
                if c in r".*+?|{}[]()^$\"'\\":
                    has_special = True
            if token.isalnum() or token.replace("_", "").isalnum():
                pattern = rf"\b{token}\b"
            elif has_special:
                pattern = escaped
            else:
                pattern = token
            patterns.append(re.compile(pattern, re.IGNORECASE))
        return patterns

    def _is_safe_pattern(self, string: str) -> bool:
        """Check if string matches known safe patterns (negative testing)."""
        for r in self.safe_regexes:
            if r.search(string):
                return True
        return False

    def _is_base64(self, string: str) -> bool:
        """Return True if ``string`` is valid base64.

        Args:
            string (str): Candidate string.

        Returns:
            bool: True if ``string`` decodes as base64, False otherwise.
        """
        try:
            base64.b64decode(string, validate=True)
            return True
        except (binascii.Error, ValueError):
            return False

    # ============================== SCANNERS ============================== #

    def _scan_compiled(self, needle: str, regex_list: List[re.Pattern], parent_function: str) -> bool:
        for regex in regex_list:
            if regex.search(needle):
                if not self._is_safe_pattern(needle):
                    self.disp.log_debug(
                        f"Failed for {needle}, pattern {regex.pattern} matched.",
                        parent_function
                    )
                    return True
        return False

    def _is_numeric(self, s: str) -> bool:
        """Return True if string is purely numeric."""
        return bool(re.fullmatch(r'\d+(\.\d+)?', s))

    # ============================== CHECKERS ============================== #

    def check_if_symbol_sql_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """Detect injection-like symbols in the input.

        This looks for characters or sequences commonly used in SQL
        injection payloads (for example ``;`` or ``--``). If ``string`` is a
        list, each element is checked recursively.

        Args:
            string (Union[str, List[str]]): String or list of strings to scan.

        Returns:
            bool: True when an injection-like symbol is detected, False
                otherwise.
        """
        if string is None:
            return False
        if isinstance(string, list):
            for i in string:
                if self.check_if_symbol_sql_injection(i):
                    return True
            return False
        string = self._sanitize_usr_input(str(string))
        if self._is_numeric(string):
            return False
        if self.base64_key in string:
            return not self._is_base64(string)
        return self._scan_compiled(string, self.regex_map[self.symbols_key], "check_if_symbol_sql_injection")

    def check_if_command_sql_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """Detect SQL keywords in the input.

        This checks for common SQL command keywords (SELECT, DROP, UNION,
        etc.). If ``string`` is a list, each element is checked recursively.

        Args:
            string (Union[str, List[str]]): String or list of strings to scan.

        Returns:
            bool: True when an SQL keyword is found, False otherwise.
        """
        if self.debug:
            msg = "(check_if_command_sql_injection) string = "
            msg += f"'{string}', type(string) = '{type(string)}'"
            self.disp.disp_print_debug(msg)
        if isinstance(string, list):
            for i in string:
                if self.check_if_command_sql_injection(i):
                    return True
            return False
        if string is None:
            return False
        string = self._sanitize_usr_input(str(string))
        if self._is_numeric(string):
            return False
        if self.base64_key in string:
            return not self._is_base64(string)
        return self._scan_compiled(string, self.regex_map[self.keywords_key], "check_if_command_sql_injection")

    def check_if_logic_gate_sql_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """Detect logical operators (AND/OR/NOT) in the input.

        Useful to catch attempts that combine conditions to bypass simple
        filters. Accepts a string or list of strings.

        Args:
            string (Union[str, List[str]]): String or list of strings to scan.

        Returns:
            bool: True when a logic gate is present, False otherwise.
        """
        if string is None:
            return False
        if isinstance(string, list):
            for i in string:
                if self.check_if_logic_gate_sql_injection(i):
                    return True
            return False
        string = self._sanitize_usr_input(str(string))
        if self._is_numeric(string):
            return False
        if self.base64_key in string:
            return not self._is_base64(string)
        return self._scan_compiled(string, self.regex_map[self.logic_gates_key], "check_if_logic_gate_sql_injection")

    def check_if_symbol_and_command_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """Combined check for symbol- or keyword-based injection patterns.

        Args:
            string (Union[str, List[str]]): Input to scan.

        Returns:
            bool: True when either symbol- or keyword-based injection is found.
        """
        is_symbol = self.check_if_symbol_sql_injection(string)
        is_command = self.check_if_command_sql_injection(string)
        if is_symbol or is_command:
            return True
        return False

    def check_if_symbol_and_logic_gate_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """Combined check for symbol- or logic-gate-based injection patterns.

        Args:
            string (Union[str, List[str]]): Input to scan.

        Returns:
            bool: True when symbol- or logic-gate-based injection is found.
        """
        is_symbol = self.check_if_symbol_sql_injection(string)
        is_logic_gate = self.check_if_logic_gate_sql_injection(string)
        if is_symbol or is_logic_gate:
            return True
        return False

    def check_if_command_and_logic_gate_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """Combined check for keyword- or logic-gate-based injection patterns.

        Args:
            string (Union[str, List[str]]): Input to scan.

        Returns:
            bool: True when a command or logic-gate-based injection is found.
        """
        is_command = self.check_if_command_sql_injection(string)
        is_logic_gate = self.check_if_logic_gate_sql_injection(string)
        if is_command or is_logic_gate:
            return True
        return False

    def check_if_sql_injection(self, string: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]]]) -> bool:
        """High-level SQL injection detection using all configured checks.

        This method runs a combined scan (symbols, keywords and logic gates)
        and returns True if any of the component checks considers the input
        dangerous.

        Args:
            string (Union[str, List[str]]): Input to scan; may be a string or a
                list (including nested lists).

        Returns:
            bool: True when an injection-like pattern is detected, False
                otherwise.
        """
        if string is None:
            return False
        if isinstance(string, list):
            for i in string:
                if self.check_if_sql_injection(i):
                    return True
            return False
        string = self._sanitize_usr_input(str(string))
        if self._is_numeric(string):
            return False
        if self.base64_key in string:
            return not self._is_base64(string)
        return self._scan_compiled(string, self.regex_map['all'], "check_if_sql_injection")

    def check_if_injections_in_strings(self, array_of_strings: Union[Union[str, None, int, float], Sequence[Union[str, None, int, float]], Sequence[Sequence[Union[str, None, int, float]]]]) -> bool:
        """Scan an array (possibly nested) of strings for injection patterns.

        This convenience function accepts a string, a list of strings, or a
        nested list of strings and returns True if any element appears to be
        an injection.

        Args:
            array_of_strings (Union[str, List[str], List[List[str]]]): Item(s) to scan.

        Returns:
            bool: True when an injection-like value is detected.
        """
        if array_of_strings is None:
            return False
        if isinstance(array_of_strings, list):
            for i in array_of_strings:
                if isinstance(i, list):
                    if self.check_if_injections_in_strings(i) is True:
                        return True
                    continue
                if self.check_if_sql_injection(i):
                    return True
            return False
        strings = self._sanitize_usr_input(str(array_of_strings))
        if self._is_numeric(strings):
            return False
        if self.check_if_sql_injection(strings):
            return True
        return False

    # ============================== TESTING ============================== #

    def run_test(self, title: str, array: List[Any], function: Callable[[Any], bool], expected_response: bool = False, global_status: int = 0) -> int:
        """Run a small functional test over the injection-checker functions.

        This helper is used by :meth:`test_injection_class` and not by the
        production code path. It calls ``function`` for each element in
        ``array`` and compares the result to ``expected_response``.

        Args:
            title (str): Short test title printed to stdout.
            array (List[Any]): Items to test (may be strings or nested lists).
            function (Callable[[Any], bool]): Function to call for each item.
            expected_response (bool): Expected boolean response for each call.
            global_status (int): Running global status to update.

        Returns:
            int: Updated global status (``0`` for success, error code otherwise).
        """
        err = 84
        global_response = global_status
        print(f"{title}", end="")
        for i in array:
            print(".", end="")
            if function(i) != expected_response:
                print("[error]")
                global_response = err
        print("[success]")
        return global_response

    def test_injection_class(self) -> int:
        """Run a small suite of self-tests for the injection checks.

        Returns:
            int: ``0`` on success, non-zero error code if any test fails.
        """
        success = 0
        global_status = success
        test_sentences = [
            "SHOW TABLES;",
            "SHOW Databases;",
            "DROP TABLES;",
            "SHOW DATABASE;",
            "SELECT * FROM table;",
            "ORDER BY ASC"
        ]
        global_status = self.run_test(
            title="Logic gate test:",
            array=self.logic_gates,
            function=self.check_if_logic_gate_sql_injection,
            expected_response=True,
            global_status=global_status
        )
        global_status = self.run_test(
            title="Keyword check:",
            array=self.keywords,
            function=self.check_if_command_sql_injection,
            expected_response=True,
            global_status=global_status
        )
        global_status = self.run_test(
            title="Symbol check:",
            array=self.symbols,
            function=self.check_if_symbol_sql_injection,
            expected_response=True,
            global_status=global_status
        )
        global_status = self.run_test(
            title="All injections:",
            array=self.all,
            function=self.check_if_sql_injection,
            expected_response=True,
            global_status=global_status
        )
        global_status = self.run_test(
            title="Array check:",
            array=[self.all],
            function=self.check_if_injections_in_strings,
            expected_response=True,
            global_status=global_status
        )
        global_status = self.run_test(
            title="Double array check:",
            array=[self.all, self.all],
            function=self.check_if_injections_in_strings,
            expected_response=True,
            global_status=global_status
        )
        global_status = self.run_test(
            title="SQL sentences:",
            array=test_sentences,
            function=self.check_if_sql_injection,
            expected_response=True,
            global_status=global_status
        )
        return global_status


if __name__ == "__main__":
    DEBUG: bool = True
    II = SQLInjection(debug=DEBUG)
    res = II.test_injection_class()
    print(f"test status = {res}")
