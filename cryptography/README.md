# InquisitorNet Cryptography Suite

This subfolder contains **`inquisitor_crypto`**, a self‑contained Python package that
encrypts and decrypts English text while wrapping the result in an
authentic‑looking *Warhammer 40 000* Inquisitorial communiqué.  
The goal is two‑fold:

1. **Education & utility** – provide a simple, understandable implementation of
   symmetric encryption that can be plugged straight into the InquisitorNet
   project (or any other Python code‑base).
2. **Aesthetic immersion** – evoke the secretive style of Imperial
   communications so that messages *look* and *feel* as though they were penned
   by an Inquisitor.

---

## 1 Cryptography background

Modern cryptography distinguishes between **symmetric** and
**asymmetric** cryptosystems.  In symmetric systems the same secret
key is used to encrypt and decrypt a message.  This was the only kind
of cryptography known until the 1970s, and it remains faster than
asymmetric methods; today algorithms like the Advanced Encryption
Standard (AES) are widely used. Asymmetric systems, by contrast, use a public key to encrypt and a related private key to decrypt.

For the purposes of this project a classical **Vigenère cipher** is
implemented.  Although simple compared with modern ciphers, the
Vigenère algorithm illustrates the basic principles of encryption and
decryption: a repeating keyword is used to shift letters of the
plaintext, producing a ciphertext that cannot be read without the key.
Digits are also shifted modulo 10 to preserve numbers.  See
`inquisitor_crypto/cipher.py` for the implementation and
explanatory comments.  **Important:** the Vigenère cipher is **not
cryptographically secure**.  It is used here to keep the codebase
self‑contained.  For production security you should substitute a
well‑reviewed algorithm such as AES. For real‑world security you should switch to a modern block cipher such as AES‑256 – the current NIST standard (<https://en.wikipedia.org/wiki/Advanced_Encryption_Standard>).

---

## 2 Warhammer aesthetics

### Inquisitorial ciphers and symbolism

---> Ask someone who is well-versed in Warhammer lore to check for accuracy. <---

The Inquisition is notoriously secretive.  According to the
*Warhammer 40 000* lore, an Inquisitor’s clothing and personal
possessions often contain subtle information about their philosophy,
allegiances and contacts; there is **no universal cipher** for
Inquisitorial iconography because it has evolved over ten thousand
Terran years and holds many layers of hidden meanings.  Inquisitors learn various
codes and **battle‑tongues** as interrogators, and it is one of
their first tasks to modify or create a **secret tongue** of their
own.  Cells of Inquisitors agree upon
code‑speak built on basic language foundations; some codes are
completely impenetrable, while others hide messages within ordinary
conversation.  The type of cipher an
Inquisitor uses can reveal whom they learned their skills from.

Imperial agents also employ physical devices for secure information.
The **Inquisitorial Cipher** is a relic of the Deathwatch – a small
device gifted by a mysterious Inquisitor that contains valuable
intelligence and is updated by its owner’s master.
During the Horus Heresy era, Traitor forces fielded **Unilingual
Cipher Hosts** to make their communications impervious to **Imperial
Cipher Breakers**.

---> Ask someone who is well-versed in Warhammer lore to check for accuracy. <---

### Thought for the day

Imperial communiqués often include a “**Thought for the Day**,” a
short aphorism intended to inspire loyalty or vigilance.  Lexicanum’s
collection notes that these phrases are used on various papers and
reports across the Imperium.  Examples
include “A suspicious mind is a healthy mind,” “A moment of laxity
spawns a lifetime of heresy,” and other stern slogans from Imperial
propaganda.

### Aesthetic choices in this project

To evoke this lore the cryptography suite wraps encrypted messages in
a multi‑line *communiqué* adorned with plus signs (``+``) and markers
like `++BEGIN CRYPTOGRAM++` and `++END CRYPTOGRAM++`.  The wrapper
includes an Ordo designation (e.g. “Hereticus” or “Malleus”) and a
Thought for the Day chosen at random from a built‑in list.  Grouping
the ciphertext into five‑character chunks further mimics the
fragmented look of archaic teleprinter transmissions.  These touches
are inspired by the way Inquisitors use personalised ciphers and
symbolism and by the ubiquitous use of Imperial aphorisms.

* **Inquisitorial symbolism & ciphers** – Inquisitors use personalised
  iconography and secret tongues that evolve over millennia, with no universal
  standard: <https://warhammer40k.fandom.com/wiki/Inquisition#Inquisitorial_Symbolism_%26_Ciphers>

<!-- This doesn't seem relevant to the project. -->
<!-- * **Inquisitorial Cipher** – a Deathwatch relic that constantly updates its
  intelligence: <https://wh40k.lexicanum.com/wiki/Inquisitorial_Cipher>
* **Unilingual Cipher Hosts** – devices used during the Horus Heresy to foil
  Imperial Cipher Breakers: <https://warhammer40k.fandom.com/wiki/Nykona_Sharrowkyn> -->


### Implementation
A plaintext encrypted with `inquisitor_crypto.encrypt` is wrapped in a
multi‑line communiqué with:

* `+++INQUISITORIAL COMMUNIQUÉ+++` header  
* An **Ordo** label (`Xenos`, `Hereticus`, or `Malleus`)  
* A randomly chosen **Thought for the Day** (Imperial slogan)  
  – list drawn from Lexicanum: <https://wh40k.lexicanum.com/wiki/Thought_for_the_day_(A_-_H)>  
* The cipher text bracketed by `++BEGIN/END CRYPTOGRAM++`  
* `+++END OF COMMUNIQUÉ+++` footer

Grouping the ciphertext into five‑character chunks further mimics the
fragmented look of archaic teleprinter traffic.


---

## 3 Installation

```bash
# Option A – drop straight into your project
cp -r inquisitor_crypto <your-project>/

# Option B – editable install (local development)
pip install -e .
```

The package has **no external dependencies**, so it works on any CPython ≥ 3.8.

---

## 4 Quick start

```python
from inquisitor_crypto import encrypt, decrypt

plaintext = "In the grim darkness of the far future there is only war."
key       = "Rosarius"

ciphertext = encrypt(plaintext, key, ordo="Malleus")
print(ciphertext)

# ...later...
original = decrypt(ciphertext, key)
assert original == plaintext
```

Sample output (Thought for the Day will vary):

```
+++INQUISITORIAL COMMUNIQUÉ+++
Ordo: Malleus
Thought for the Day: A suspicious mind is a healthy mind.
++BEGIN CRYPTOGRAM++
Oty hwv lpxt iracsmgt vm uwa pfe lhtujk tlmfr mw pzsxi nfg.
++END CRYPTOGRAM++
+++END OF COMMUNIQUÉ+++
```

---

## 5 Project structure

```
inquisitor_crypto/
├── __init__.py         # Public API (encrypt / decrypt)
├── cipher.py           # Vigenère implementation & helpers
├── aesthetics.py       # Warhammer wrapping, slogan pool
└── README.md           # This document
```

### Key modules

| Module | Purpose |
|--------|---------|
| **`cipher.py`** | `vigenere_encrypt` / `vigenere_decrypt` shift letters (A‑Z, a‑z) and digits (0‑9) with a repeating key. |
| **`aesthetics.py`** | `wrap_message` / `unwrap_message` add or remove Warhammer formatting; `encrypt` / `decrypt` combine cipher + wrapper. |

### `cipher.py`

This module defines `vigenere_encrypt` and `vigenere_decrypt`.  The
key is preprocessed to extract alphabetic characters and to compute a
shift value for each letter.  When encrypting, alphabetic characters
in the plaintext are shifted forward by the corresponding key value
(wrapping within A–Z or a–z); digits are shifted modulo 10.  All
other characters are left untouched.  Decryption reverses this
process.

### `aesthetics.py`

Defines `wrap_message` and `unwrap_message`, plus two convenience
functions `encrypt` and `decrypt` that combine encryption or
decryption with wrapping.  The wrapper selects a “Thought for the
Day” at random (unless one is provided), adds the Ordo label, and
inserts begin/end markers around the grouped cipher text.  The
unwrapper searches for these markers and strips all whitespace to
recover the raw cipher text before calling `vigenere_decrypt`.

---

## 6 Notes and future work

* **Security:** Vigenère is vulnerable to frequency analysis.  Substitute AES
  (e.g. via the [`cryptography`](https://pypi.org/project/cryptography/) library)
  if you need real confidentiality.
* **Internationalisation:** Only Latin letters & digits are shifted.  Extending
  to other scripts requires defining new ranges and modulo arithmetic.
* **Custom flavours:** Edit `aesthetics.py` to add more slogans, change headers,
  or integrate your own faction branding.

* **Security:** As noted above, the Vigenère cipher is vulnerable to
  frequency analysis and other attacks.  Its use here is for
  illustrative purposes.  For real security one should use a modern
  symmetric algorithm such as AES (e.g. via the [`cryptography`](https://pypi.org/project/cryptography/) library).
* **Internationalisation:** Currently only Latin letters and digits
  are shifted.  Adding support for extended Unicode alphabets would
  require defining appropriate ranges and modular arithmetic.
* **Custom aesthetics:** The list of Thoughts for the Day can be
  extended or loaded from an external file. Edit `aesthetics.py` to add more slogans, change headers, or integrate your own faction branding.Similarly, the wrapper
  markers can be changed to suit your group’s preferred style.

---

## 7 References

1. *Wikipedia – Cryptography* <https://en.wikipedia.org/wiki/Cryptography>  
2. *Wikipedia – Advanced Encryption Standard* <https://en.wikipedia.org/wiki/Advanced_Encryption_Standard>  
3. *Lexicanum – Thought for the Day (A–H)* <https://wh40k.lexicanum.com/wiki/Thought_for_the_day_(A_-_H)>  
4. *Lexicanum – Inquisitorial Cipher* <https://wh40k.lexicanum.com/wiki/Inquisitorial_Cipher>  
5. *Warhammer 40 k Wiki – Inquisition (Symbolism & Ciphers section)* <https://warhammer40k.fandom.com/wiki/Inquisition#Inquisitorial_Symbolism_%26_Ciphers>  
6. *Warhammer 40 k Wiki – Nykona Sharrowkyn* <https://warhammer40k.fandom.com/wiki/Nykona_Sharrowkyn>

---

*Version 1.2 – compiled 2025-08-03*  
