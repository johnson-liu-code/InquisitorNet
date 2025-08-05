"""
InquisitorNet Cryptography Suite
================================

This package provides functions to encrypt and decrypt English text
using a simple Vigenère‑style cipher and to wrap/unwrap the resulting
messages in a Warhammer 40 000–style communique.  The goal is to give
projects like InquisitorNet a plug‑and‑play encryption component that
looks like it came straight from the Inquisition while still being
based on reproducible mathematics.

Usage
-----

Basic encryption and decryption can be performed via the
``encrypt`` and ``decrypt`` functions.  See the documentation in
``README.md`` for more details and examples.

Example:

>>> from inquisitor_crypto import encrypt, decrypt
>>> message = "The heretic must be hunted"
>>> key = "ROSARIUS"
>>> wrapped = encrypt(message, key, ordo="Malleus")
>>> print(wrapped)
... # see README for sample output
>>> original = decrypt(wrapped, key)
>>> assert original == message

"""

from .cipher import vigenere_encrypt, vigenere_decrypt
from .aesthetics import (
    wrap_message,
    unwrap_message,
    encrypt,
    decrypt,
)

__all__ = [
    "vigenere_encrypt",
    "vigenere_decrypt",
    "wrap_message",
    "unwrap_message",
    "encrypt",
    "decrypt",
]