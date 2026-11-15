import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet

def generate_rsa_keypair(key_size=2048): # Generates an RSA key pair and returns (private_pem, public_pem) as strings.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem

def encrypt_fernet_key(public_key_pem: str, fernet_key: str) -> str: # Encrypts a Fernet key using the recipient's RSA Public Key (PEM). Returns a base64-encoded ciphertext string.
    public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
    encrypted_bytes = public_key.encrypt(
        fernet_key.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt_fernet_key(private_key_pem: str, encrypted_fernet_key_b64: str) -> str: # Decrypts an encrypted Fernet key using own RSA Private Key (PEM). Returns the Fernet key string.
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )
    encrypted_bytes = base64.b64decode(encrypted_fernet_key_b64.encode('utf-8'))
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_bytes.decode('utf-8')

def generate_fernet_key() -> str: # Generates a new random Fernet key string. Returns the key as a string.
    return Fernet.generate_key().decode('utf-8')

def fernet_encrypt(fernet_key: str, plaintext: str) -> str: # Encrypts plaintext string with Fernet key. Returns ciphertext string.
    f = Fernet(fernet_key.encode('utf-8') if isinstance(fernet_key, str) else fernet_key)
    return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')

def fernet_decrypt(fernet_key: str, ciphertext: str) -> str: # Decrypts ciphertext string with Fernet key. Returns plaintext string.
    f = Fernet(fernet_key.encode('utf-8') if isinstance(fernet_key, str) else fernet_key)
    return f.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
