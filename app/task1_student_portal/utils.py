"""
Utility Functions for Student Portal

This module provides utility functions for file operations, specifically for reading
and writing JSON data files used by the Student Portal API. It includes error handling
and automatic file creation for missing files.
"""

import json
from pathlib import Path
from typing import Any

# Directory where data files are stored (same directory as this module)
DATA_DIR = Path(__file__).parent


class FileError(RuntimeError):
    """
    Custom exception for file operation errors.

    Raised when there are issues reading from or writing to JSON data files.
    Inherits from RuntimeError to indicate runtime file system issues.
    """
    pass


def read_json(name: str, default: Any) -> Any:
    """
    Read JSON data from a file, creating it with default value if it doesn't exist.

    This function attempts to read and parse a JSON file. If the file doesn't exist,
    it creates the file with the provided default value and returns that default.
    If the file exists but is empty, it also returns the default value.

    Args:
        name (str): Name of the JSON file to read (relative to DATA_DIR).
        default (Any): Default value to use if file doesn't exist or is empty.

    Returns:
        Any: Parsed JSON data from the file, or the default value.

    Raises:
        FileError: If there's an error reading or parsing the file.

    Example:
        >>> students = read_json("students.json", {})
        >>> # Returns {} if file doesn't exist, or parsed JSON if it does
    """
    path = DATA_DIR / name
    try:
        if not path.exists():
            path.write_text(json.dumps(default, indent=2))
            return default
        return json.loads(path.read_text() or json.dumps(default))
    except Exception as e:
        raise FileError(f"Error reading {name}: {e}")


def write_json(name: str, data: Any) -> None:
    """
    Write data to a JSON file with pretty formatting.

    Serializes the provided data to JSON format and writes it to the specified file.
    The JSON is formatted with 2-space indentation for readability.

    Args:
        name (str): Name of the JSON file to write (relative to DATA_DIR).
        data (Any): Data to serialize and write to the file.

    Raises:
        FileError: If there's an error writing to the file.

    Example:
        >>> write_json("students.json", {"john": {"password_hash": "...", "grades": []}})
        >>> # Creates/overwrites students.json with formatted JSON
    """
    path = DATA_DIR / name
    try:
        path.write_text(json.dumps(data, indent=2))
    except Exception as e:
        raise FileError(f"Error writing {name}: {e}")
