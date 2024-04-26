import logging
import sys
from typing import Final
from pathlib import Path
import os

PATH_TO_ASSETS: Final[Path] = Path(__file__).parent.parent.parent / "assets"
sys.path.append(str(PATH_TO_ASSETS))

# pylint: disable=wrong-import-position
from logging_formatter import CustomFormatter

"""configure logging"""

# create log with 'spam_application'
log = logging.getLogger("My_app")
log.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

log.addHandler(ch)


def generate_aes_key(key_length: int = 32) -> bytes:
    """
    Generate a random AES key.

    Parameters
    ----------
    key_length : int, optional
        The length of the key in bytes. The default is 32.

    Returns
    -------
    key : bytes
        The random AES key.

    Notes
    -----
    In this example, os.urandom is used instead of random as
    on the other hand cannot be seeded and draws its source of entropy
    from many unpredictable sources, making it more random. It is more
    suitable for cryptographic purposes.
    """

    key = os.urandom(key_length)
    log.debug("Generated AES key: %s", key)
    return key
