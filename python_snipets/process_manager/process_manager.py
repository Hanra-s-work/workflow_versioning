"""
    File containing classes in charge of managing actions like starting a python element as a seperate process that can be running on a seperate processor core
"""

from datetime import datetime
from typing import Mapping, Iterable, Callable, Any, Union, List, Dict
from multiprocessing import Process
from exeptions import ProcessNotFound


class ProcessDetails:
    """
        Class in charge of acting like a structure so that the process it contains can be tracked and/or managed.
    """
    ID: int = 0
    NAME: str = ""
    ARGS: Union[Iterable, None] = None
    ALIVE: Union[object, None] = None
    DAEMON: bool = False
    KWARGS: Union[Mapping[str, Any], None] = None
    P_OBJECT: Union[Process, None] = None
    EXIT_CODE: Union[int, None] = None
    STARTED_TIME: Union[datetime, None] = None


class ProcessCommands:
    """
        Class containing utility functions to manage a given process
    """
    @staticmethod
    def is_defined(cls: ProcessDetails) -> bool:
        """
            Function in charge of saying if the class instance ProcessDetails has a defined process or not.

        Args:
            cls (ProcessDetails): This is the instance of the process you wish to interract with.

        Returns:
            bool: True if the process if defines, False otherwise.
        """

        if isinstance(cls.P_OBJECT, Process) and cls.P_OBJECT is not None:
            return True
        return False

    @staticmethod
    def name(cls: ProcessDetails) -> str:
        """
            Function in charge of returning the name fo the process (variable NAME in ProcessDetails)

            Args:
                cls (ProcessDetails): This is the instance of the process you wish to interract with.

            Returns:
                str: the name of the instance.
        """
        return cls.NAME

    @staticmethod
    def pname(cls: ProcessDetails) -> Union[str, None]:
        """
        Function in charge of returning the name of the process object.

        Args:
            cls (ProcessDetails): This is the instance of the process you wish to interract with.

        Returns:
            Union[str, None]: The name of the instance, None if the process is not defined.
        """
        if ProcessCommands.is_defined(cls):
            return cls.P_OBJECT.name
        return None

    @staticmethod
    def is_alive(cls: ProcessDetails) -> bool:
        """
        Function in charge of informing the user if the process is running or not.

        Args:
            cls (ProcessDetails): This is the instance of the process you wish to interract with.

        Returns:
            bool: True if running, False otherwise.
        """
        if ProcessCommands.is_defined(cls) is True:
            return cls.P_OBJECT.is_alive()
        return False

    @staticmethod
    def get_run_status(cls: ProcessDetails) -> Union[int, None]:
        """
        Function in charge of retuning the execution status.

        Args:
            cls (ProcessDetails): This is the instance of the process you wish to interract with.

        Returns:
            Union[int, None]: The execution status of the process, None if the process is still running.
        """
        if ProcessCommands.is_defined(cls) is False:
            cls.EXIT_CODE = None
            return None
        cls.EXIT_CODE = cls.P_OBJECT.exitcode
        return cls.EXIT_CODE

    @staticmethod
    def join(cls: ProcessDetails, timeout: Union[float, None] = 5) -> Union[int, None]:
        """
        Function in charge of joining a process.

        Args:
            cls (ProcessDetails): This is the instance of the process you wish to interract with.
            timeout (Union[float, None], optional): This is the delay that is allowed to the process before it is forcefully terminated. Defaults to 5.

        Returns:
            Union[int, None]: The execution status of the process, None if the process if not running.
        """
        if ProcessCommands.is_alive(cls) is True:
            cls.P_OBJECT.join(timeout=timeout)
            cls.STARTED_TIME = None
            return ProcessCommands.get_run_status(cls)
        return None

    @staticmethod
    def close(cls: ProcessDetails, timeout: Union[float, None] = 5) -> Union[int, None]:
        """
        Function in charge of closing a process.

        Args:
            cls (ProcessDetails): This is the instance of the process you wish to interract with.
            timeout (Union[float, None], optional): This is the delay that is allowed to the process before it is forcefully terminated. Defaults to 5.

        Returns:
            Union[int, None]: The execution status of the process, None if the process if not running.
        """
        status = None
        if ProcessCommands.is_alive(cls) is True:
            status = ProcessCommands.join(cls, timeout=timeout)
        if ProcessCommands.is_defined(cls) is True:
            cls.P_OBJECT.close()
            cls.P_OBJECT = None
        return status


class ProcessWrapper:
    """
        Class in charge of containing the logic code for tracking and handling multiple independent processes.
    """

    def __init__(self, debug: bool = False, default_timeout: int = 5) -> None:
        self.debug: bool = debug
        self.processes: List[ProcessDetails] = []
        self.cmd: ProcessCommands = ProcessCommands
        self.timeout: int = default_timeout  # seconds
        self.number_of_initialised_processes: int = len(self.processes)
        self.number_of_alive_processes: int = 0

    def print_debug(self, string: str) -> None:
        """
        Function in charge of displaying a debug message on the terminal.

        Args:
            string (str): The string to display if we are in debug mode.
        """
        if self.debug:
            print(f"DEBUG: {string}")

    def _locate_process(self, process_id: Union[int, ProcessDetails]) -> ProcessDetails:
        """
            Function in charge of locating a process in the class and return it's internal pointer.

            Args:
                process_id (Union[int, ProcessDetails]): The id or instance of the process to locate.

            Returns:
                The ProcessDetails object so that it can be directly handled

            Raises:
                ProcessNotFound: This informs the user that the expected process does not exist
                TypeError: This informs the user that the type they provided does not match the expected ones.
        """
        node: ProcessDetails = None
        if isinstance(process_id, int):
            for i in self.processes:
                if i.ID == process_id:
                    node = i
                    break
        elif isinstance(process_id, ProcessDetails):
            for i in self.processes:
                if i is process_id:
                    node = i
                    break
        else:
            raise TypeError(
                f"Expected an instance of ProcessDetails or int but got {type(process_id).__name__}"
            )
        if node is None:
            raise ProcessNotFound
        return node

    def __del__(self) -> None:
        """
            Function in charge of stopping all the processes in case the program closes in any shape or form (unless violently killed, ex: SIGTERM)
        """
        self.number_of_alive_processes = 0
        self.number_of_initialised_processes = 0
        for index, item in enumerate(self.processes):
            self.print_debug(f"Checking process: {index}:{item.NAME}")
            if self.cmd.is_alive(item):
                self.cmd.join(item, self.timeout)
                self.cmd.close(item)

    def start_a_process(self, function: Callable, args: Iterable[Any] = (), kwargs: Mapping[str, Any] = {}, name: Union[str, None] = None, daemon: bool = True, start: bool = True) -> ProcessDetails:
        """
            Start a process on a seperate Thread so that the main can be used for other tasks

        Args:
            function (Callable): The function you wish to launch.
            args (Iterable[Any], optional): The arguments you wish to provide to the function when launching it. Defaults to ().
            kwargs (Mapping[str, Any], optional): The option to pass vairables while explicitly specifying their name when launching the process. Defaults to {}.
            name (Union[str, None], optional): The identifier of the process. Defaults to None.
            daemon (bool, optional): Wether to run it in the background. Defaults to True.
            start (bool, optional): Wether to start the process whe it is created or not. Defaults to True.

        Returns:
            ProcessDetails: A pointer to the object so that it can be directly handled.
        """
        # Initialised the capsule
        instance: ProcessDetails = ProcessDetails()

        # Assign the arguments
        instance.NAME = name
        instance.ARGS = args
        instance.KWARGS = kwargs
        instance.DAEMON = daemon

        # Initialise the process
        instance.P_OBJECT = Process(
            group=None,
            target=function,
            name=instance.NAME,
            args=instance.ARGS,
            kwargs=instance.KWARGS,
            daemon=instance.DAEMON
        )

        # Update the alive check
        instance.ALIVE = instance.P_OBJECT.is_alive

        # Update the ID
        if len(self.processes) > 0:
            instance.ID = self.processes[-1].ID + 1
        else:
            instance.ID = 0

        # Add the capsule to the list
        self.processes.append(instance)

        if start is True:
            instance.P_OBJECT.start()
            instance.STARTED_TIME = datetime.now()
        return self.processes[-1]

    def join(self, process_id: Union[int, ProcessDetails], timeout: Union[int, None] = None) -> Union[int, None]:
        """
            Function in charge of joining a process.

            Args:
                process_id (Union[int, ProcessDetails]): This is the identifier of the process you wish to interrupt.
                timeout (Union[int, None]): This is the delay that is allowed to the process before it is forcefully terminated.

            Returns:
                Union[int, None]: The execution status of the process or None if it is not running.

            Raises:
                ProcessNotFound; This informs the user that the expected process does not exist.
                TypeError: This informs the user that the type they provided does not match the expected ones.
        """
        process_item: ProcessDetails = self._locate_process(process_id)
        return self.cmd.join(process_item, timeout)

    def join_exception_safe(self, process_id: Union[int, ProcessDetails], timeout: Union[int, None] = None) -> Union[int, None, str]:
        """
            Function in charge of joining a process.

            Args:
                process_id (Union[int, ProcessDetails]): This is the identifier of the process you wish to interrupt.
                timeout (Union[int, None]): This is the delay that is allowed to the process before it is forcefully terminated.

            Returns:
                Unioon[int, None, str]: The execution status of the process or None if it is not running.

            Raises:
                ProcessNotFound; This informs the user that the expected process does not exist.
                TypeError: This informs the user that the type they provided does not match the expected ones.
        """
        try:
            return self.join(process_id, timeout)
        except (ProcessNotFound, TypeError) as e:
            return str(e)

    def close(self, process_id: Union[int, ProcessDetails], timeout: Union[int, None] = None) -> Union[int, None]:
        """
            Function in charge of closing a process.

            Args:
                process_id (Union[int, ProcessDetails]): This is the identifier of the process you wish to interrupt.
                timeout (Union[int, None]): This is the delay that is allowed to the process before it is forcefully terminated.

            Returns:
                Union[int, None]: The execution status of the process or None if it is not running.

            Raises:
                ProcessNotFound; This informs the user that the expected process does not exist.
                TypeError: This informs the user that the type they provided does not match the expected ones.
        """
        process_item: ProcessDetails = self._locate_process(process_id)
        return self.cmd.close(process_item, timeout)

    def close_exception_safe(self, process_id: Union[int, ProcessDetails], timeout: Union[int, None] = None) -> Union[int, None, str]:
        """
            Function in charge of closing a process.

            Args:
                process_id (Union[int, ProcessDetails]): This is the identifier of the process you wish to interrupt.
                timeout (Union[int, None]): This is the delay that is allowed to the process before it is forcefully terminated.

            Returns:
                Unioon[int, None, str]: The execution status of the process or None if it is not running.

            Raises:
                ProcessNotFound; This informs the user that the expected process does not exist.
                TypeError: This informs the user that the type they provided does not match the expected ones.
        """
        try:
            return self.close(process_id, timeout)
        except (ProcessNotFound, TypeError) as e:
            return str(e)

    def clear(self) -> List[Dict[str, Union[int, str, None]]]:
        """
            Function in charge of clearing the pool.
            This function will go through all the processes it has stored, end the running ones, clear the list.

        Returns:
            List[Dict[str, Union[int, None]]]: A list of dictionaries containing the name of the instance as well as their exit code.
            The first code (key: global_status) is reference to the overall execution, 0 if no processes exited with an error, None otherwise.

        Example:
            Here is an example of what the final result might look like:
            `[{"name":"global_status", "status":0}, {"name":"process1", "status": 0}]`
        """
        name_key: str = "name"
        status_key: str = "status"
        overall: List[Dict[str, Union[str, int, None]]] = [
            {name_key: "global_status", status_key: 0}
        ]
        for index, item in enumerate(self.processes):
            self.print_debug(f"Checking process: {index}:{item.NAME}")
            status: Union[int, None] = None
            if self.cmd.is_alive(item) is True:
                status = self.cmd.join(item, self.timeout)
                self.cmd.close(item)
            if status is not None and status != 0:
                overall[0][status_key] = None
            overall.append({name_key: item.NAME, status_key: status})
        self.processes.clear()
        self.number_of_alive_processes = 0
        self.number_of_initialised_processes = len(self.processes)
        return overall


if __name__ == "__main__":
    PWI = ProcessWrapper(debug=True)
    PWI.print_debug("Hello world !")
