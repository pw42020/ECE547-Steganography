"""
Description
-----------
Executable for stegosaurus.
"""

from typing import Final
from .keygen import generate_aes_key

if __name__ == "__main__":
    KEY: Final[int] = generate_aes_key()
