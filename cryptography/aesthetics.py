"""
Warhammer 40 000 styling utilities for cryptographic messages.

This module defines helper functions to wrap Vigenère‑encrypted
messages in an aesthetic befitting the InquisitorNet project.  It
simulates the language and flair of Imperial communiqués by adding
markers, Ordo identifiers and a randomly selected "Thought for the
day"—brief slogans used throughout the Imperium on official papers
and reports.

Functions
---------

wrap_message(cipher_text: str, ordo: str = "Hereticus", thought: str | None = None) -> str
    Format an encrypted message into a Warhammer‑style communiqué.

unwrap_message(wrapped: str) -> str
    Extract the raw cipher text from a wrapped communiqué.  Spaces
    inserted for readability are stripped.

encrypt(plaintext: str, key: str, ordo: str = "Hereticus", thought: str | None = None) -> str
    High‑level function that encrypts a plaintext string using the
    Vigenère cipher and immediately wraps it using ``wrap_message``.

decrypt(wrapped: str, key: str) -> str
    Reverse of ``encrypt``.  Unwraps a Warhammer‑style message and
    decrypts it back to plaintext using the provided key.

"""

from __future__ import annotations

import random
import re
from typing import Iterable

from .cipher import vigenere_encrypt, vigenere_decrypt

# A curated list of Imperial aphorisms (Thoughts for the day) drawn
# from Lexicanum and other official sources.  These phrases emphasise
# the unyielding faith of the Imperium.  Feel free to expand this list
# to introduce more variety.  Citations for these aphorisms can be
# found in the "Thought for the day" Lexicanum collection【566384215732101†L10-L14】.
THOUGHTS: list[str] = [
    "A suspicious mind is a healthy mind.",
    "A moment of laxity spawns a lifetime of heresy.",
    "A questioning mind betrays a treacherous soul.",
    "A single thought of heresy can blight a lifetime of faithful duty.",
    "A broad mind lacks focus.",
]


def _group_text(text: str, group_size: int = 5) -> str:
    """Group a string into fixed‑width chunks separated by spaces.

    This helper prepares the cipher text for human reading.  It first
    replaces literal spaces in the input with underscores so that
    significant whitespace is not lost.  All newline characters are
    stripped, then the string is split into chunks of ``group_size``.
    The resulting groups are joined by single spaces.  The grouping
    has no semantic meaning; it merely improves legibility.
    """
    # Protect spaces by converting them to underscores.  Newlines are
    # removed entirely.  Other whitespace (e.g. tabs) is also removed.
    clean = text.replace(" ", "_")
    clean = re.sub(r"\s+", "", clean)
    return ' '.join(
        clean[i : i + group_size] for i in range(0, len(clean), group_size)
    )


def wrap_message(cipher_text: str, ordo: str = "Hereticus", thought: str | None = None) -> str:
    """Wrap an encrypted string in a Warhammer‑style communiqué.

    Parameters
    ----------
    cipher_text : str
        The raw encrypted text to be wrapped.  It may contain
        whitespace, but it will be stripped and regrouped by this
        function.
    ordo : str, optional
        Which Ordo of the Inquisition the message purports to be
        associated with (e.g. ``"Hereticus"``, ``"Malleus"``,
        ``"Xenos"``).  This label is purely cosmetic.
    thought : str | None, optional
        Optionally override the thought for the day.  If omitted, a
        random thought is selected.

    Returns
    -------
    str
        A multi‑line string styled like an Imperial transmission.
    """
    grouped = _group_text(cipher_text)
    chosen_thought = thought or random.choice(THOUGHTS)
    lines: list[str] = []
    lines.append("+++INQUISITORIAL COMMUNIQUÉ+++")
    lines.append(f"Ordo: {ordo}")
    lines.append(f"Thought for the Day: {chosen_thought}")
    lines.append("++BEGIN CRYPTOGRAM++")
    lines.append(grouped)
    lines.append("++END CRYPTOGRAM++")
    lines.append("+++END OF COMMUNIQUÉ+++")
    return '\n'.join(lines)


def unwrap_message(wrapped: str) -> str:
    """Extract the cipher text from a wrapped communiqué.

    This function looks for lines between ``++BEGIN CRYPTOGRAM++`` and
    ``++END CRYPTOGRAM++``.  Any whitespace inside the cipher is
    removed.  If the markers cannot be found, the entire message is
    treated as raw cipher text.

    Parameters
    ----------
    wrapped : str
        The styled message produced by :func:`wrap_message`.

    Returns
    -------
    str
        The ungrouped cipher text ready for decryption.
    """
    begin_marker = "++BEGIN CRYPTOGRAM++"
    end_marker = "++END CRYPTOGRAM++"
    pattern = re.compile(
        re.escape(begin_marker) + r"(.*?)" + re.escape(end_marker), re.DOTALL
    )
    match = pattern.search(wrapped)
    if match:
        inner = match.group(1)
        # Remove whitespace and newlines
        # Remove all whitespace that was added for grouping
        clean = re.sub(r"\s+", "", inner)
        # Convert underscores back to literal spaces
        return clean.replace("_", " ")
    # Fallback: remove all whitespace from the entire input and restore
    # underscores as spaces
    clean = re.sub(r"\s+", "", wrapped)
    return clean.replace("_", " ")


def encrypt(plaintext: str, key: str, ordo: str = "Hereticus", thought: str | None = None) -> str:
    """Encrypt and wrap plaintext using the Vigenère cipher and Warhammer styling.

    This convenience function combines :func:`vigenere_encrypt` and
    :func:`wrap_message` into a single call.
    """
    cipher_text = vigenere_encrypt(plaintext, key)
    return wrap_message(cipher_text, ordo=ordo, thought=thought)


def decrypt(wrapped: str, key: str) -> str:
    """Unwrap and decrypt a Warhammer‑styled message back to plaintext.

    Parameters
    ----------
    wrapped : str
        The formatted message produced by :func:`encrypt`.
    key : str
        The same key that was used for encryption.

    Returns
    -------
    str
        The original plaintext.
    """
    cipher_text = unwrap_message(wrapped)
    return vigenere_decrypt(cipher_text, key)