"""
    File in charge of containing the code that will store pointer references to initialise elements that need to be accessed by different elements in the program.
"""

import copy
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


class _SharedInstanceProxy:
    """
    A proxy class that delegates attribute access, modification, and deletion to a wrapped instance.
    This allows for controlled access to a shared instance, potentially with additional handle-based logic.

    Args:
        instance (object): The object instance to proxy.
        handle (Any): An optional handle or identifier associated with the proxy.

    Methods:
        __getattr__(item): Delegates attribute access to the wrapped instance.
        __setattr__(key, value): Delegates attribute assignment to the wrapped instance.
        __delattr__(item): Delegates attribute deletion to the wrapped instance.
        __dir__(): Returns the list of attributes of the wrapped instance.
        __repr__(): Returns the string representation of the wrapped instance.
        __str__(): Returns the informal string representation of the wrapped instance.
        __eq__(other): Compares the wrapped instance with another object or proxy.
        __hash__(): Returns the hash of the wrapped instance.
    """

    def __init__(self, instance, handle):
        """
        Initialize the proxy with the given instance and handle.

        Args:
            instance (object): The object to be proxied.
            handle (Any): An optional handle or identifier.
        """
        self.__dict__['_instance'] = instance
        self.__dict__['_handle'] = handle

    def __getattr__(self, item):
        """
        Delegate attribute access to the wrapped instance.

        Args:
            item (str): The attribute name.

        Returns:
            Any: The value of the requested attribute.
        """
        inst = object.__getattribute__(self, "_instance")
        return getattr(inst, item)

    def __setattr__(self, key, value):
        """
        Delegate attribute assignment to the wrapped instance.

        Args:
            key (str): The attribute name.
            value (Any): The value to assign.
        """
        inst = object.__getattribute__(self, "_instance")
        return setattr(inst, key, value)

    def __delattr__(self, item):
        """
        Delegate attribute deletion to the wrapped instance.

        Args:
            item (str): The attribute name to delete.
        """
        inst = object.__getattribute__(self, "_instance")
        return delattr(inst, item)

    def __dir__(self):
        """
        Return the list of attributes of the wrapped instance.

        Returns:
            list: List of attribute names.
        """
        inst = object.__getattribute__(self, "_instance")
        return sorted(set(dir(inst)) - {"_instance", "_handle"})

    def __repr__(self):
        """
        Return the string representation of the wrapped instance.

        Returns:
            str: The string representation.
        """
        inst = object.__getattribute__(self, "_instance")
        # tried the direct call, the semi direct call
        return repr(inst)

    def __str__(self):
        """
        Return the informal string representation of the wrapped instance.

        Returns:
            str: The informal string representation.
        """
        inst = object.__getattribute__(self, "_instance")
        # tried the direct call, the semi-direct call
        return str(inst)

    def __eq__(self, other):
        """
        Compare the wrapped instance with another object or proxy.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        inst = object.__getattribute__(self, "_instance")
        if isinstance(other, _SharedInstanceProxy):
            return inst is object.__getattribute__(other, "_instance")
        return inst == other

    def __hash__(self):
        """
        Return the hash of the wrapped instance.

        Returns:
            int: The hash value.
        """
        inst = object.__getattribute__(self, "_instance")
        return hash(inst)

    def __copy__(self):
        inst = object.__getattribute__(self, "_instance")
        return inst

    def __deepcopy__(self, memo):
        inst = object.__getattribute__(self, "_instance")
        return copy.deepcopy(inst, memo)

    def __getstate__(self):
        inst = object.__getattribute__(self, "_instance")
        return inst.__getstate__() if hasattr(inst, "__getstate__") else inst.__dict__

    def __setstate__(self, state):
        inst = object.__getattribute__(self, "_instance")
        if hasattr(inst, "__setstate__"):
            inst.__setstate__(state)
        else:
            inst.__dict__.update(state)


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

    def __new__(cls: Type['SharedInstance']) -> '_SharedInstanceProxy':
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
            return _SharedInstanceProxy(cls._instance, handle)

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
