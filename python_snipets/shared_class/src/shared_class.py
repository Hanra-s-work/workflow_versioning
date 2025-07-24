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


class _SIReferenceHandle:
    """Dummy object used to track live references to SharedInstance."""

    def __del__(self) -> None:
        print("Handle collected")


class SharedInstance(FD):
    """
        Class in charge of managing instances throughout the runtime of the program.
    """
    _lock: threading.Lock = threading.Lock()
    _instance: Union['SharedInstance', None] = None
    _live_references: weakref.WeakSet = weakref.WeakSet()
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
                print("cls._instance: None")
                cls._instance = super().__new__(cls)
                cls._instance.custom_log_levels = MS.CustomLogLevels()
                cls._instance.initialized_time = datetime.now()

            # Create a handle object to track logical usage
            handle = _SIReferenceHandle()
            cls._live_references.add(handle)

            # Attach handle to the instance for GC tracking
            # instance = cls._instance
            # object.__setattr__(instance, "_ref_handle", handle)

            # instance = cls._instance

            # # Attach per-access handle to instance, stored in a set to allow multiple
            # if not hasattr(instance, "_ref_handles"):
            #     instance._ref_handles = set()
            # instance._ref_handles.add(handle)
            return cls._instance

    def __del__(self) -> None:
        """
            Function in charge of decrementing the shared instances counter when an instance is lost.
        """
        print("In del")
        print("Out of del")

    def get_shared_instances(self) -> int:
        """
            Return the number of shared instances that are currently used throughout the program.
            This function is threadsafe.

        Returns:
            int: The number of active instances
        """
        with self._lock:
            return len(self._live_references)

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

        # Set the custom logging levels if any
        if self.custom_log_levels is not None:
            # If the logger has not been initialised, create the levels from scratch
            if logger_initialised is False:
                item_nodes: Dict[
                    str, Any
                ] = self.custom_log_levels.level_details
                for key, value in item_nodes.items():
                    node.add_custom_level(
                        level=value[self.custom_log_levels.level_key],
                        name=value[self.custom_log_levels.name_key],
                        colour_text=value[self.custom_log_levels.foreground_colour_key],
                        colour_bg=value[self.custom_log_levels.background_colour_key]
                    )
            # If there is at least one logger that has been initialised, just set the colours (because they most likely did not persist)
            else:
                item_nodes: Dict[
                    str, Any
                ] = self.custom_log_levels.level_details
                for key, value in item_nodes.items():
                    node.update_logging_colour_background(
                        colour=value[self.custom_log_levels.background_colour_key],
                        level_name=value[self.custom_log_levels.level_key],
                        logger_instance=node.logger
                    )
                    node.update_logging_colour_text(
                        colour=value[self.custom_log_levels.foreground_colour_key],
                        level_name=value[self.custom_log_levels.level_key],
                        logger_instance=node.logger
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
