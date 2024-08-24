"""
File in charge of launching a demo when called
"""

from .hl_hello_world import HLHelloWorld

if __name__ == '__main__':
    HWI = HLHelloWorld()
    HWI.test()
    print(f"Created by {HWI.author}")
