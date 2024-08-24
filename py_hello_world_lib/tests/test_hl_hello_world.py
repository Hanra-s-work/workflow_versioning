"""_summary_
This file contains the test cases for the hello_world function in the hl_hello_world module.
"""
import pytest
from hl_hello_world import HLHelloWorld


@pytest.fixture
def hl_hello_world():
    """Fixture to create an instance of HLHelloWorld."""
    return HLHelloWorld()


def test_hw_string_default(hl_hello_world):
    """Test that hw_string returns the default hello world string."""
    assert hl_hello_world.hw_string() == "Hello World !"


def test_hw_string_custom():
    """Test that hw_string returns a custom hello world string."""
    custom_string = "Hello Epitech!"
    hl_hello_world = HLHelloWorld(hello_world=custom_string)
    assert hl_hello_world.hw_string() == custom_string


def test_hw_print(capsys, hl_hello_world):
    """Test that hw_print prints the correct hello world string."""
    hl_hello_world.hw_print()
    captured = capsys.readouterr()
    assert captured.out == "Hello World !\n"


def test_is_hello_world_true(hl_hello_world):
    """Test that is_hello_world returns True for the correct hello world string."""
    assert hl_hello_world.is_hello_world("Hello World !")
    assert hl_hello_world.is_hello_world("Hello World !\n")


def test_is_hello_world_false(hl_hello_world):
    """Test that is_hello_world returns False for an incorrect string."""
    assert not hl_hello_world.is_hello_world("Goodbye World!")
    assert not hl_hello_world.is_hello_world("Hello World")


def test_version(hl_hello_world):
    """Test that the version attribute is set correctly."""
    assert hl_hello_world.__version__ == "1.0.0"


def test_author(hl_hello_world):
    """Test that the author attribute is set correctly."""
    assert hl_hello_world.author == "Henry Letellier"


def test_test_function(capsys, hl_hello_world):
    """Test that the test method prints the hello world string."""
    hl_hello_world.test()
    captured = capsys.readouterr()
    assert captured.out == "Hello World !\n"
