""" 
# +==== BEGIN AsperHeader =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperHeader
# FILE: __init__.py
# CREATION DATE: 11-10-2025
# LAST Modified: 12:59:37 13-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The file allowing the code for the sql management files to be imported seamlessly.
# // AR
# +==== END AsperHeader =================+
"""

from .sql_injection import SQLInjection
from .sql_constants import TARGET
from .sql_manager import SQL

__all__ = [
    "TARGET",
    "SQLInjection",
    "SQL"
]

"""
Module: __init__.py

This module initializes the SQL management package, allowing seamless imports of key components such as:
- `SQLInjection`: Provides SQL injection protection utilities.
- `TARGET`: Constants for SQL operations.
- `SQL`: Core SQL management class.

Exports:
    TARGET, SQLInjection, SQL
"""
