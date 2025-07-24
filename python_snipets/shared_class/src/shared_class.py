"""
    File in charge of containing the code that will store pointer references to initialise elements that need to be accessed by different elements in the program.
"""

import weakref
import threading
from typing import Type, Union, Dict, Any
from datetime import datetime

from display_tty import Disp, TOML_CONF, SAVE_TO_FILE, FILE_DESCRIPTOR, FILE_NAME

try:
    from . import my_structs as MS
except ImportError:
    try:
        import my_structs as MS
    except ImportError as e:
        raise RuntimeError("Failed to import my_struct.") from e
try:
    from .flexible_dictionary import FlexibleDictionary as FD
except ImportError:
    try:
        from flexible_dictionary import FlexibleDictionary as FD
    except ImportError as e:
        raise RuntimeError("Failed to import FlexibleDictionary.") from e


class SharedInstance(FD):
    """
        Class in charge of managing instances throughout the runtime of the program.
    """
    _lock: threading.Lock = threading.Lock()
    _instance: Union['SharedInstance', None] = None
    _shared_instances: int = 0
    _initialised_loggers: weakref.WeakSet[Disp] = weakref.WeakSet()
    debug: bool = False
    error: int = 1
    success: int = 0
    initialized_time: Union[datetime, None] = None
    custom_log_levels: Union[MS.CustomLogLevels, None] = None

    def __new__(cls: Type['SharedInstance']) -> 'SharedInstance':
        """
            Function in charge of creating a global instance class that will contain shared elements.
            This function makes this class initialisation threadsafe.

        Args:
            cls (SharedInstance): The class to initialise.

        Returns:
            Self: The initialised class
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # super(SharedInstance, cls._instance).__init__()
                cls._instance.custom_log_levels = MS.CustomLogLevels()
                cls._instance.initialized_time = datetime.now()
                cls._instance._shared_instances = 0
            else:
                cls._shared_instances += 1
        return cls._instance

    def __del__(self) -> None:
        """
            Function in charge of decrementing the shared instances counter when an instance is lost.
        """
        with self._lock:
            self._shared_instances -= 1
            if self._shared_instances <= 0:
                self._instance = None

    def get_shared_instances(self) -> int:
        """
            Return the number of shared instances that are currently used throughout the program.
            This function is threadsafe.

        Returns:
            int: The number of active instances
        """
        with self._lock:
            return self._shared_instances

    def initialise_custom_loger(self, class_name: str = __name__) -> Disp:
        """
            Function in charge of initialising the display library, a library in charge of displaying/logging info on the terminal in a prettier way without having functions that are to complicated.

            Args:
                class_name (str, optional): This is the name of the class you with to assign to the underlying logging library.

            Returns:
                Disp: An initialised instance of the Display library.
        """

        logger_initialised: bool = False

        with self._lock:
            if isinstance(class_name, str) is False:
                class_name = self.__class__.__name__

            if len(self._initialised_loggers) > 0:
                logger_initialised = True

            node: Disp = Disp(
                toml_content=TOML_CONF,
                file_descriptor=FILE_DESCRIPTOR,
                save_to_file=SAVE_TO_FILE,
                file_name=FILE_NAME,
                debug=self.debug,
                logger=class_name
            )

        self._initialised_loggers.add(node)

        if logger_initialised is False and self.custom_log_levels is not None:
            item_nodes: Dict[str, Any] = self.custom_log_levels.level_details
            for key, value in item_nodes.items():
                node.add_custom_level(
                    level=value[self.custom_log_levels.level_key],
                    name=value[self.custom_log_levels.name_key],
                    colour_text=value[self.custom_log_levels.foreground_colour_key],
                    colour_bg=value[self.custom_log_levels.background_colour_key]
                )

        return node

    def toggle_debug(self, state: Union[bool, None] = None) -> None:
        """
            Function in charge of toggling the state of the debug variable.
            This function is threadsafe.

            Args:
                state (bool, optional): The state you wish to force upon the variable. Default: None
        """
        final_state: bool = False

        if isinstance(state, bool):
            final_state = state

        with self._lock:
            if final_state is None:
                final_state = not self.debug
            self.debug = final_state
            for index, item in enumerate(self._initialised_loggers):
                item.update_disp_debug(self.debug)
