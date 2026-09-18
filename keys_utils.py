# keys_utils.py

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def generate_key_pair():
    """
    Generates an RSA key pair.
    Returns (private_key, public_key) as key objects.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_private_key(private_key, password: bytes = None) -> bytes:
    """Converts a private key into a savable PEM-format byte string."""
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )

def serialize_public_key(public_key) -> bytes:
    """Converts a public key into a savable PEM-format byte string."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

def load_private_key(pem_data: bytes, password: bytes = None):
    return serialization.load_pem_private_key(pem_data, password=password)

def load_public_key(pem_data: bytes):
    return serialization.load_pem_public_key(pem_data)

def rsa_encrypt(public_key, data: bytes) -> bytes:
    """Encrypts small data (like a passphrase) using the public key."""
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )

def rsa_decrypt(private_key, ciphertext: bytes) -> bytes:
    """Decrypts data using the private key."""
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )

if __name__ == "__main__":
    priv, pub = generate_key_pair()
    
    message = b"grove-xenon-tempo-jade"  # simulating a passphrase
    encrypted = rsa_encrypt(pub, message)
    decrypted = rsa_decrypt(priv, encrypted)
    
    print("Original: ", message)
    print("Decrypted:", decrypted)
    assert message == decrypted
    print("✅ Match!")