"""
    File in charge of making the folder executable.
    This also serves as a visual test
"""

from time import sleep
import json
from display_tty import Disp

try:
    from .shared_class import SharedInstance, FD
except ImportError:
    try:
        from shared_class import SharedInstance, FD
    except ImportError as e:
        raise RuntimeError(
            "SharedInstance class not found. Aborting execution."
        ) from e

if __name__ == "__main__":
    import gc
    FDI = FD()
    FDI["e"] = "e"
    print(f"FlexiDict: {FDI}")
    SI: SharedInstance = SharedInstance()
    print(f"SI content: {dir(SI)}")
    SI2: SharedInstance = SharedInstance()
    print(f"SI2 content: {dir(SI2)}")
    SI3: SharedInstance = SharedInstance()
    print(f"SI3 content: {dir(SI3)}")
    print(f"SI is SI2: {SI is SI2}")
    print(f"SI is SI3: {SI is SI3}")
    print(f"SI2 is SI3: {SI2 is SI3}")
    print(f"shared instances: {SI.get_shared_instances()}")
    print("Removing SI2")
    del SI2
    print(f"gc.collect(): {gc.collect()}")
    sleep(0.1)
    print(f"shared instances: {SI.get_shared_instances()}")
    DSI = SI.initialise_custom_loger("Test logger")
    DSI2 = SI.initialise_custom_loger("Test2 logger")
    DSI.log_info("Hello world")
    if SI.custom_log_levels is not None:
        DSI.log_custom_level(
            SI.custom_log_levels.log_success,
            "Success string"
        )
    DSI2.log_info("Hello world")
    if SI.custom_log_levels is not None:
        DSI2.log_custom_level(
            SI.custom_log_levels.log_success,
            "Success string"
        )
    print("Testing the proxy")
    print("Point setting SI.a")
    SI.a = "a"
    print("Creating a new instance")
    SI4: SharedInstance = SharedInstance()
    print(f"SI4 content: {dir(SI4)}")
    print(f"SI is SI4: {SI is SI4}")
    print(f"SI.a: {SI.a}, SI3.a: {SI3.a}, SI4.a: {SI4.a}")
    print(f"SI: {SI}, SI3: {SI3}, SI4: {SI4}")
    print(
        f"SI.dumps(): {SI.dumps()}, SI3.dumps(): {SI3.dumps()}, SI4.dumps(): {SI4.dumps()}"
    )
    print(
        f"json.dumps(SI,cls=SI.FlexibleJSONEncoder): {json.dumps(SI, cls=SI.FlexibleJSONEncoder)}, json.dumps(SI3,cls=SI.FlexibleJSONEncoder): {json.dumps(SI3, cls=SI.FlexibleJSONEncoder)}, json.dumps(SI4,cls=SI.FlexibleJSONEncoder): {json.dumps(SI4, cls=SI.FlexibleJSONEncoder)}"
    )

    print("Declaring the TestClass")

    class TestClass:
        """
            This is a class in charge of checking how the shared instance behaves in a class.
        """

        def __init__(self) -> None:
            self.si: SharedInstance = SharedInstance()
            self.disp: Disp = self.si.initialise_custom_loger(
                self.__class__.__name__)
            self.disp.log_custom_level(
                self.si.custom_log_levels.log_success,
                "Test class initialised"
            )

        def test(self) -> None:
            """
                Function in charge of making sure that the children of TestClass are accessible.
            """
            self.disp.log_custom_level(
                self.si.custom_log_levels.log_success,
                "Test function called"
            )

    print("Initialising TestClass")
    TCI = TestClass()
    print("Calling the test function")
    TCI.test()
