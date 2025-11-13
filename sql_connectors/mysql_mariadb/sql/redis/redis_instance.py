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
# FILE: redis_instance.py
# CREATION DATE: 11-10-2025
# LAST Modified: 17:32:40 12-10-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The file in charge of handling the redis connection as well as cache.
# // AR
# +==== END AsperHeader =================+
"""

import os
import redis

r = redis.Redis(
    unix_socket_path=os.getenv("REDIS_SOCKET", "/run/redis/redis.sock"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)


class RedisCaching:

    def __init__(self) -> None:
        pass
