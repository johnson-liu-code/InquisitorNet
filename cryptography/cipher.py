"""
Cipher primitives for the InquisitorNet cryptography suite.

The heart of this module is a straightforward implementation of the
Vigenère cipher, a classical symmetric algorithm in which each letter
of the plaintext is shifted by an amount determined by a repeating
keyword.  While this cipher is not cryptographically secure by
modern standards, it is easy to understand and demonstrate the
principles of encryption and decryption.  For serious security needs
the ``README.md`` notes that established algorithms such as AES
should be used instead.

Functions
---------

vigenere_encrypt(text: str, key: str) -> str
    Encrypt English text using a Vigenère‑style algorithm.  Only
    alphabetic characters and digits are shifted; other characters
    (spaces, punctuation) are preserved as‑is.

vigenere_decrypt(text: str, key: str) -> str
    Decrypt a Vigenère‑style ciphertext using the same key.

Key handling
------------

Only letters in the key are used to compute shifts.  Digits and
symbols in the key are ignored.  The algorithm is case‑insensitive
for keys; ``"a"`` and ``"A"`` produce identical shifts.  If the
key has no letters the functions will raise a ``ValueError``.

Numeric characters in the plaintext are shifted using the same
mechanism but modulo 10 instead of 26.  For example, a key letter
with value 3 will transform ``'7'`` into ``'0'``.
"""

from __future__ import annotations

import string

def _prepare_key(key: str) -> list[int]:
    """Preprocess the key and return a list of integer shifts.

    Each letter in the key produces a shift between 0 and 25.
    Non‑letter characters are skipped.  Raises ``ValueError`` if no
    letters are present.
    """
    shifts: list[int] = []
    for ch in key:
        if ch.isalpha():
            # convert to uppercase then map 'A'->0 ... 'Z'->25
            shifts.append((ord(ch.upper()) - ord('A')) % 26)
    if not shifts:
        raise ValueError("Key must contain at least one alphabetic character")
    return shifts


def vigenere_encrypt(text: str, key: str) -> str:
    """Encrypt `text` using a Vigenère‑style cipher with the provided `key`.

    Only letters and digits are transformed.  Letters preserve their
    case.  Digits are shifted modulo 10 by the same shift used for
    letters.  Non‑alphanumeric characters (including whitespace)
    remain unchanged.

    Parameters
    ----------
    text : str
        The plaintext to encrypt.
    key : str
        The encryption key consisting of one or more letters.  Other
        characters are ignored.  The key is case‑insensitive.

    Returns
    -------
    str
        The encrypted text.
    """
    shifts = _prepare_key(key)
    result: list[str] = []
    key_index = 0
    for ch in text:
        if ch.isalpha():
            shift = shifts[key_index % len(shifts)]
            if ch.isupper():
                base = ord('A')
                offset = (ord(ch) - base + shift) % 26
                result.append(chr(base + offset))
            else:
                base = ord('a')
                offset = (ord(ch) - base + shift) % 26
                result.append(chr(base + offset))
            key_index += 1
        elif ch.isdigit():
            shift = shifts[key_index % len(shifts)]
            new_digit = (int(ch) + shift) % 10
            result.append(str(new_digit))
            key_index += 1
        else:
            result.append(ch)
    return ''.join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    """Decrypt a Vigenère‑style ciphertext using the provided `key`.

    This function reverses the transformation applied by
    :func:`vigenere_encrypt`.  See that function for details.

    Parameters
    ----------
    text : str
        The ciphertext to decrypt.
    key : str
        The same key that was used to encrypt the plaintext.

    Returns
    -------
    str
        The original plaintext.
    """
    shifts = _prepare_key(key)
    result: list[str] = []
    key_index = 0
    for ch in text:
        if ch.isalpha():
            shift = shifts[key_index % len(shifts)]
            if ch.isupper():
                base = ord('A')
                offset = (ord(ch) - base - shift) % 26
                result.append(chr(base + offset))
            else:
                base = ord('a')
                offset = (ord(ch) - base - shift) % 26
                result.append(chr(base + offset))
            key_index += 1
        elif ch.isdigit():
            shift = shifts[key_index % len(shifts)]
            new_digit = (int(ch) - shift) % 10
            result.append(str(new_digit))
            key_index += 1
        else:
            result.append(ch)
    return ''.join(result)