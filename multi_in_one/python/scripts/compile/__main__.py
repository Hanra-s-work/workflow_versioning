"""
    File in charge of making sure that the file can be called as if it were a program
"""

import sys

# try:
#     sys.path.append("..")
#     from .. import globals
# except ImportError:
#     try:
#         import globals
#     except ImportError:
#         print("Error: Unable to import globals module. Ensure you are running this script from the correct directory.")
#         sys.exit(1)


import compile as COMP

if __name__ == "__main__":
    compiler = COMP.Compile()
    compiler.run()
