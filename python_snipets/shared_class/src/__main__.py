"""
    File in charge of making the folder executable.
    This also serves as a visual test
"""

from time import sleep

try:
    from .shared_class import SharedInstance
except ImportError:
    try:
        from shared_class import SharedInstance
    except ImportError as e:
        raise RuntimeError(
            "SharedInstance class not found. Aborting execution."
        ) from e

if __name__ == "__main__":
    import gc
    SI = SharedInstance()
    print(f"SI content: {dir(SI)}")
    SI2 = SharedInstance()
    print(f"SI2 content: {dir(SI2)}")
    print(f"SI is SI2: {SI is SI2}")
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
