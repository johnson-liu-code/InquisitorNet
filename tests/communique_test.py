

import sys
import os

# Get the absolute path to the directory containing the module
# Example: if 'my_module.py' is in 'parent_folder/another_dir'
# and your current script is in 'parent_folder/current_dir'
# you might need to go up one level and then into 'another_dir'
module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ))

# Add the directory to the system path
sys.path.append(module_dir)

from inquisitor_crypto import encrypt, decrypt

plaintext = "In the grim darkness of the far future there is only war."
key       = "Rosarius"

ciphertext = encrypt(plaintext, key, ordo="Malleus")
print("\n")
print(ciphertext)

# ...later...
original = decrypt(ciphertext, key)
assert original == plaintext

print("\n")
print(f"Original text:\n{original}")