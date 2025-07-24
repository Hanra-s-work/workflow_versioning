"""
    File in charge of making the folder executable.
    This also serves as a visual test
"""

try:
    from .flexible_dictionary import FlexibleDictionary
except ImportError:
    try:
        from flexible_dictionary import FlexibleDictionary
    except ImportError as e:
        raise RuntimeError(
            "FlexibleDictionary class not found. Aborting execution."
        ) from e

if __name__ == "__main__":
    import json
    from typing import Any
    FI = FlexibleDictionary()
    print(f"Parent class content example: {FI}")
    print("Adding variables a and b")
    FI.a = "a"
    FI.b = "b"
    print(f"Parent class content example: {FI}")

    class ExampleHeritage(FlexibleDictionary[str, Any]):
        """_summary_
            This is an example dictionnary class that uses the FlexibleDictionary class as a parent.

        Args:
            FlexibleDictionary (_type_): _description_
        """
        element1: str = "element1"
        element2: str = "element2"

    EHI = ExampleHeritage()
    print(f"Example Heritage class content example: {FI}")
    print("Altering variable element1")
    EHI.element1 = "Modified Element 1"
    print(f"Example Heritage class content example (after edit): {FI}")
    # getattr
    print("Testing the getattribute function:")
    print("Fetching variable a for FlexibleDictionary")
    print(f"Value of a: {getattr(FI, 'a')}")
    print("Fetching variable element2 for ExampleHeritage")
    print(f"Value of element2: {getattr(EHI, 'element2')}")
    # setattr
    print("Testing the setattribute function:")
    print("Setting variable c for FlexibleDictionary")
    print(f"Value of c: {setattr(FI, 'c', 'c')}")
    print(f"Content of FlexibleDictionary: {FI}")
    print("Setting variable element3 for ExampleHeritage")
    print(f"Value of element3: {setattr(EHI, 'element3', 'element3')}")
    print(f"Content of ExampleHeritage: {EHI}")
    # getitem
    print("Testing the getitem function:")
    print("getting item by key (c) for FlexibleDictionary")
    print(f"Value of c: {FI['c']}")
    print("getting item by key (element3) for ExampleHeritage")
    print(f"Value of element3: {EHI['element3']}")
    # setitem
    print("Testing the setitem function:")
    print("Setting variable d for FlexibleDictionary")
    FI["d"] = 'd'
    print(f"Value of d: {FI['d']}")
    print(f"Content of FlexibleDictionary: {FI}")
    print("Setting variable element4 for ExampleHeritage")
    EHI["element4"] = "element4"
    print(f"Value of element4: {EHI['element4']}")
    print(f"Content of ExampleHeritage: {EHI}")
    # delitem
    print("Testing the delitem function:")
    print("Removing variable c for FlexibleDictionary")
    del FI["c"]
    print(f"Content of FlexibleDictionary: {FI}")
    print("Removing variable element3 for ExampleHeritage")
    del EHI["element3"]
    print(f"Content of ExampleHeritage: {EHI}")
    # delattr
    print("Testing the delattr function:")
    print("Removing variable d for FlexibleDictionary")
    del FI["d"]
    print(f"Content of FlexibleDictionary: {FI}")
    print("Removing variable element4 for ExampleHeritage")
    del EHI["element4"]
    print(f"Content of ExampleHeritage: {EHI}")
    print(f"Content of ExampleHeritage: {EHI}")
    # contains
    print("Testing the contains function:")
    print("Checking if variable d is in FlexibleDictionary")
    print(f"'d' in FlexibleDictionary: {'d' in FI}")
    print(f"'a' in FlexibleDictionary: {'a' in FI}")
    print("Checking if variable element4 if in ExampleHeritage")
    print(f"'element4' in ExampleHeritage: {'element4' in EHI}")
    print(f"'element2' in ExampleHeritage: {'element2' in EHI}")
    # iter
    print("Testing the iter function:")
    print("Getting the iter object from FlexibleDictionary")
    print(f"iter(FlexibleDictionary): {iter(FI)}")
    print("Getting the iter object from ExampleHeritage")
    print(f"iter(ExampleHeritage): {iter(EHI)}")
    # len
    print("Testing Dictionnary lengths:")
    print(f"FlexibleDictionary = {len(FI)}")
    print(f"ExampleHeritage    = {len(EHI)}")
    # eq
    print("Testing the eq (equal) function:")
    print("Getting the eq object from FlexibleDictionary")
    print(f"FlexibleDictionary == FlexibleDictionary: {FI == FI}")
    print(f"FlexibleDictionary == ExampleHeritage: {FI == EHI}")
    print("Getting the eq object from ExampleHeritage")
    print(f"ExampleHeritage == ExampleHeritage: {EHI == EHI}")
    print(f"ExampleHeritage == FlexibleDictionary: {EHI == FI}")
    # copy
    print("Testing the copy function:")
    print("Getting the copy object from FlexibleDictionary")
    FI_DUPLICATE = FI.copy()
    print(
        f"FlexibleDictionary == FlexibleDictionary (copy): {FI == FI_DUPLICATE}"
    )
    print("Getting the copy object from ExampleHeritage")
    EHI_DUPLICATE = EHI.copy()
    print(f"ExampleHeritage == ExampleHeritage (copy): {EHI == EHI_DUPLICATE}")
    # repr
    print("Testing the repr function:")
    print("Getting the repr representation from FlexibleDictionary")
    print(f"repr(FlexibleDictionary): {repr(FI)}")
    print("Getting the repr representation from ExampleHeritage")
    print(f"repr(ExampleHeritage): {repr(EHI)}")
    # reversed
    print("Testing the reversed function:")
    print("Getting the reversed object from FlexibleDictionary")
    print(f"reversed(FlexibleDictionary): {reversed(FI)}")
    print("Getting the reversed object from ExampleHeritage")
    print(f"reversed(ExampleHeritage): {reversed(EHI)}")
    # or
    print("Testing the | operator (merge):")
    merged = FI | {"z": "Z"}
    print(f"Merged FlexibleDictionary: {merged}")
    merged2 = EHI | {"element5": "Element5"}
    print(f"Merged FlexibleDictionary: {merged2}")
    # ior
    print("Testing the |= operator (in-place merge):")
    FI |= {"y": "Y"}
    print(f"In-place merged FlexibleDictionary: {FI}")
    EHI |= {"element6": "Element6"}
    print(f"in-place merged FlexibleDictionary: {EHI}")
    # getstate
    # print("Testing the reversed function:")
    # print("Getting the reversed object from FlexibleDictionary")
    # print(f"reversed(FlexibleDictionary): {reversed(FI)}")
    # print("Getting the reversed object from ExampleHeritage")
    # print(f"reversed(ExampleHeritage): {reversed(EHI)}")
    # setstate
    # print("Testing the reversed function:")
    # print("Getting the reversed object from FlexibleDictionary")
    # print(f"reversed(FlexibleDictionary): {reversed(FI)}")
    # print("Getting the reversed object from ExampleHeritage")
    # print(f"reversed(ExampleHeritage): {reversed(EHI)}")
    # str
    print("Testing the str function:")
    print("Getting the str object from FlexibleDictionary")
    print(f"str(FlexibleDictionary): {str(FI)}")
    print("Getting the str object from ExampleHeritage")
    print(f"str(ExampleHeritage): {str(EHI)}")
    # json.dumps
    print("Testing the json output")
    fi_dumped_data = json.dumps(FI, cls=FI.FlexibleJSONEncoder)
    print(f"Parent FlexibleDictionary json dumped data: {fi_dumped_data}")
    ehi_dumped_data = json.dumps(EHI, cls=FI.FlexibleJSONEncoder)
    print(f"Parent ExampleHeritage json dumped data: {ehi_dumped_data}")
    # keys
    print("Testing the keys function:")
    print("Getting the keys object from FlexibleDictionary")
    print(f"FlexibleDictionary.keys(): {FI.keys()}")
    print("Getting the keys object from ExampleHeritage")
    print(f"ExampleHeritage.keys(): {EHI.keys()}")
    # values
    print("Testing the values function:")
    print("Getting the values object from FlexibleDictionary")
    print(f"FlexibleDictionary.values(): {FI.values()}")
    print("Getting the values object from ExampleHeritage")
    print(f"ExampleHeritage.values(): {EHI.values()}")
    # to_dict
    print("Testing the to_dict function:")
    print("Getting the to_dict object from FlexibleDictionary")
    print(f"FlexibleDictionary.to_dict(): {FI.to_dict()}")
    print("Getting the to_dict object from ExampleHeritage")
    print(f"ExampleHeritage.to_dict(): {EHI.to_dict()}")
    # pop
    print("Testing the pop function:")
    print("Getting the pop object from FlexibleDictionary")
    print(f"FlexibleDictionary.pop('b'): {FI.pop('b')}")
    print("Getting the pop object from ExampleHeritage")
    print(f"ExampleHeritage.pop('element2'): {EHI.pop('element2')}")
    # get
    print("Testing the get function:")
    print("Getting the get object from FlexibleDictionary")
    print(f"FlexibleDictionary.get('a'): {FI.get('a')}")
    print("Getting the get object from ExampleHeritage")
    print(f"ExampleHeritage.get('element1'): {EHI.get('element1')}")
    # update
    print("Testing the update function:")
    print("Getting the update object from FlexibleDictionary")
    update_dict = {"b": "b", "c": "c", "d": "d"}
    print(
        f"FlexibleDictionary.update({update_dict}): {FI.update(update_dict)}")
    print(f"FlexibleDictionary: {FI}")
    print("Getting the get object from ExampleHeritage")
    update_dict = {
        "element2": "element2", "element3": "element3", "element4": "element4"
    }
    print(f"ExampleHeritage.update({update_dict}): {EHI.update(update_dict)}")
    print(f"ExampleHeritage: {EHI}")
    # clear
    print("Testing the clear function:")
    print("Getting the clear object from FlexibleDictionary")
    clear_dict = {"b": "b", "c": "c", "d": "d"}
    print(f"FlexibleDictionary.clear(): {FI.clear()}")
    print(f"FlexibleDictionary: {FI}")
    print("Getting the get object from ExampleHeritage")
    print(f"ExampleHeritage.clear(): {EHI.clear()}")
    print(f"ExampleHeritage: {EHI}")
