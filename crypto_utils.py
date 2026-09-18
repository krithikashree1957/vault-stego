# crypto_utils.py

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_SIZE = 16
NONCE_SIZE = 12

def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Turns a human passphrase into a proper 256-bit encryption key."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return kdf.derive(passphrase.encode())

def encrypt_message(message: str, passphrase: str) -> bytes:
    """
    Encrypts a message using AES-GCM.
    Returns: salt + nonce + ciphertext, all packed together as bytes.
    """
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(passphrase, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)

    return salt + nonce + ciphertext

def decrypt_message(data: bytes, passphrase: str) -> str:
    """
    Reverses encrypt_message. Expects data in the same
    salt + nonce + ciphertext format.
    """
    salt = data[:SALT_SIZE]
    nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = data[SALT_SIZE + NONCE_SIZE:]

    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()



