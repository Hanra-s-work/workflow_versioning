"""
    File in charge of containing the code that allows users to access content from a dictionnary as if it were a structure
"""

import json
from collections.abc import Mapping
from typing import Any, Dict, get_type_hints, TypeVar, Type, Iterable, Generic

_KT = TypeVar("_KT")
VT = TypeVar("VT")


class FlexibleDictionary(Generic[_KT, VT]):
    """ Class in charge of emulating the functionalities of a dictionary as well as a C type structure 
    Class in charge of emulating the functionalities of a dictionary as well as a C type structure.

    Provides dictionary-like behavior with attribute access, default values from type hints,
    recursive dictionary wrapping, and support for serialization and merging.
    """

    class FlexibleJSONEncoder(json.JSONEncoder):
        """_summary_
            Custom library encoder that is meant to help the json library dump the content as json.

        Args:
            json (_type_): _description_
        """

        def default(self, obj):

            if hasattr(obj, '__json__'):
                return obj.__json__()
            return super().default(obj)

    def __init__(self, **kwargs) -> None:
        """
        Initialize a new FlexibleDictionary instance.

        Args:
            **kwargs: Key-value pairs to initialize the dictionary.

        Notes:
            Class attributes with type hints will be used as defaults if not overridden by kwargs.
        """
        # Store the name of the class
        self._class_name: str = self.__class__.__name__

        # initialise the reference dictionnary
        self._data: Dict[str, Any] = {}

        # Use type hints (if any) for default values
        defaults = {
            k: getattr(self.__class__, k)
            for k in get_type_hints(self.__class__)
            if hasattr(self.__class__, k)
        }

        # Load defaults first
        for key, value in defaults.items():
            self._data[key] = self._wrap(value)

        # Override with explicit kwargs
        for key, value in kwargs.items():
            self._data[key] = self._wrap(value)

    def _wrap(self, value):
        """
        Wraps nested dictionaries into FlexibleDictionary instances.

        Args:
            value: Any value, possibly a dict.

        Returns:
            The original value or an FlexibleDictionary if value is a dict.
        """
        if isinstance(value, Mapping) and not isinstance(value, FlexibleDictionary):
            try:
                # Only try to unpack dicts with string keys
                if all(isinstance(k, str) for k in value.keys()):
                    return self.__class__(**value)
            except Exception:
                pass  # fallback to returning the raw value
        return value

    def __getattr__(self, name):
        """
        Fallback for attribute access when not found on the instance.

        Args:
            name: Attribute name.

        Returns:
            The corresponding value from internal data.

        Raises:
            AttributeError: If the key does not exist.
        """
        if '_data' not in self.__dict__:
            raise AttributeError(
                f"'{self._class_name}' object has no attribute '{name}' (data not initialized)")
        try:
            return self.__dict__['_data'][name]
        except KeyError as e:
            raise AttributeError(
                f"'{self._class_name}' object has no attribute '{name}'"
            ) from e

    def __setattr__(self, name, value):
        """
        Sets an attribute or dictionary item.

        During initialization, before _data exists, attributes are set directly.
        Afterwards, non-private attributes are stored in the internal _data dictionary.

        Args:
            name: Attribute name.
            value: Value to assign.
        """
        if name in self.__dict__ or name.startswith('_') or '_data' not in self.__dict__:
            super().__setattr__(name, value)
        else:
            self.__dict__['_data'][name] = self._wrap(value)

    def __getitem__(self, key):
        """
        Retrieve a value by key.

        Args:
            key: Key to access.

        Returns:
            Corresponding value from the internal data.
        """
        if '_data' not in self.__dict__:
            raise AttributeError(
                f"'{self._class_name}' object has no attribute '{key}' (data not initialized)")
        try:
            return self.__dict__['_data'][key]
        except KeyError as e:
            raise AttributeError(
                f"'{self._class_name}' object has no attribute '{key}'"
            ) from e

    def __setitem__(self, key, value):
        """
        Set a value by key.

        Args:
            key: Key to assign to.
            value: Value to store.
        """
        if '_data' not in self.__dict__:
            raise AttributeError(
                f"'{self._class_name}' object has no attribute '{key}' (data not initialized)")
        self._data[key] = self._wrap(value)

    def __delitem__(self, key):
        """
        Delete a key from the dictionary.

        Args:
            key: Key to remove.
        """
        del self._data[key]

    def __delattr__(self, key):
        """
        Delete an attribute from the dictionary.

        Args:
            key: Key to remove.
        """
        del self._data[key]

    def __contains__(self, key):
        """
        Check if a key exists in the dictionary.

        Args:
            key: The key to check.

        Returns:
            True if key exists, False otherwise.
        """
        return key in self._data

    def __iter__(self):
        """
        Return iterator over dictionary keys.

        Returns:
            Iterator over keys.
        """
        return iter(self._data)

    def __len__(self):
        """
        Return the number of stored keys.

        Returns:
            The number of items.
        """
        return len(self._data)

    def __eq__(self, other):
        """
        Equality comparison.

        Args:
            other: Another FlexibleDictionary or dict.

        Returns:
            True if contents are equal, False otherwise.
        """
        if isinstance(other, FlexibleDictionary):
            return self._data == other._data
        if isinstance(other, dict):
            return self.to_dict() == other
        return NotImplemented

    def __copy__(self):
        """
        Create a shallow copy of the dictionary.

        Returns:
            A new FlexibleDictionary with the same content.
        """
        return self.copy()

    def __repr__(self):
        """
        Return the official string representation.

        Returns:
            A developer-friendly string of the internal data.
        """
        return f"{self._class_name}({self._data})"

    def __reversed__(self):
        """
        Return reversed iterator over keys.

        Returns:
            A reversed iterator of keys.
        """
        return reversed(list(self._data))

    def __or__(self, other):
        """
        Merge two dictionaries using the | operator.

        Args:
            other: Another dictionary.

        Returns:
            A new merged FlexibleDictionary.
        """
        if isinstance(other, dict):
            merged = self.to_dict()
            merged.update(other)
            return self.__class__(**merged)
        return NotImplemented

    def __ior__(self, other):
        """
        In-place merge using |= operator.

        Args:
            other: A dictionary to merge.

        Returns:
            The updated FlexibleDictionary.
        """
        if isinstance(other, dict):
            self.update(other)
            return self
        return NotImplemented

    def __getstate__(self):
        """
        Support for pickling.

        Returns:
            Internal state as a plain dictionary.
        """
        return self.to_dict()

    def __setstate__(self, state: Dict):
        """
        Restore from pickled state.

        Args:
            state: Dictionary representing internal data.
        """
        object.__setattr__(self, "_data", {})
        for key, value in state.items():
            self._data[key] = self._wrap(value)

    def __str__(self):
        """
        Return string version of the internal dictionary.

        Returns:
            A stringified dictionary.
        """
        return self.dumps(indent=2)

    def __json__(self):
        """
        JSON serializer hook.

        Returns:
            A dictionary suitable for JSON serialization.
        """
        return self.to_dict()

    def items(self):
        """
        Return key-value pairs.

        Returns:
            dict_items of internal data.
        """
        return self._data.items()

    def keys(self):
        """
        Return keys of the dictionary.

        Returns:
            dict_keys of internal data.
        """
        return self._data.keys()

    def values(self):
        """
        Return values of the dictionary.

        Returns:
            dict_values of internal data.
        """
        return self._data.values()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a standard Python dictionary.

        Returns:
            A dict with all nested AQFlexibleDictionaries unwrapped.
        """
        # Optionally convert back to plain dict
        def unwrap(val):
            if isinstance(val, FlexibleDictionary):
                return val.to_dict()
            return val
        _data = self.__dict__.get('_data', None)
        if _data is None:
            return {}  # Or raise or handle as appropriate
        return {k: unwrap(v) for k, v in _data.items()}

    def copy(self) -> "FlexibleDictionary":
        """
        Shallow copy of this object.

        Returns:
            A new FlexibleDictionary instance.
        """
        return self.__class__(**self.to_dict())

    def pop(self, key, default=None):
        """
        Remove and return item by key.

        Args:
            key: The key to pop.
            default: Value to return if key is missing.

        Returns:
            The value associated with the key, or default.
        """
        return self._data.pop(key, default)

    def get(self, key, default=None):
        """
        Return value for key if present.

        Args:
            key: Key to look for.
            default: Value to return if key is missing.

        Returns:
            The value or default.
        """
        return self._data.get(key, default)

    def setdefault(self, key, default=None):
        """
        Insert key with default if not already present.

        Args:
            key: Key to insert.
            default: Value to use if key is not found.

        Returns:
            The value associated with the key.
        """
        return self._data.setdefault(key, self._wrap(default))

    def update(self, other=(), **kwargs):
        """
        Update internal data with another dict or iterable.

        Args:
            other: Dictionary or iterable of key-value pairs.
            **kwargs: Additional key-value pairs to update.
        """
        if isinstance(other, dict):
            items = other.items()
        else:
            items = other  # assume iterable of pairs
        for k, v in items:
            self._data[k] = self._wrap(v)
        for k, v in kwargs.items():
            self._data[k] = self._wrap(v)

    def clear(self):
        """
        Remove all items from the dictionary.
        """
        self._data.clear()

    def dumps(self, **kwargs) -> str:
        """
        A custom json dumper to allow the class to be output as a json.
        This is a rebind of the dumps function.

        Returns:
            str: A string containing the json content.
        """
        return json.dumps(self.to_dict(), cls=self.FlexibleJSONEncoder, **kwargs)

    def to_json(self, **kwargs) -> str:
        """
        A custom json dumper to allow the class to be output as a json.
        This is a rebind of the dumps function.

        Returns:
            str: A string containing the json content.
        """
        return self.dumps(**kwargs)

    @classmethod
    def fromkeys(cls: Type["FlexibleDictionary"], iterable: Iterable[str], value: Any = None):
        """
        Create new instance from keys and a shared default value.

        Args:
            iterable: Iterable of keys.
            value: Value assigned to each key.

        Returns:
            A new FlexibleDictionary instance.
        """
        return cls(**{k: value for k in iterable})
