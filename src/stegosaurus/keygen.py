"""
Description
-----------
This module is used to generate a random key for the encryption and decryption of messages.
Specifically, it generates an AES key with an optional parameter for the key length.

Author
------
Patrick Walsh
"""

import os
from .utils import log


def generate_aes_key(key_length: int = 32) -> int:
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