"""
    File in charge of containing the code to manage a set of processes while staying centralised.
"""

try:
    from .process_manager import ProcessWrapper, ProcessCommands, ProcessDetails, ProcessNotFound
except ImportError:
    try:
        from process_manager import ProcessWrapper, ProcessCommands, ProcessDetails, ProcessNotFound
    except ImportError as e:
        raise RuntimeError(
            "ProcessWrapper class (or one of it's class components) not found. Aborting execution."
        ) from e

if __name__ == "__main__":
    PWI = ProcessWrapper(debug=False)
    PWI.print_debug("Hello world !")
