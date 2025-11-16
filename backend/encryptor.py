# encryptor.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import os

BLOCK_SIZE = AES.block_size  # 16

def pkcs7_pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len

def pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        return data
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def derive_key(password: str, salt: bytes = None, iterations: int = 200000) -> (bytes, bytes):
    """
    Derive a 32-byte key from password using PBKDF2 (SHA256).
    Returns (key, salt). If salt is provided, it's used, otherwise a new salt is generated.
    """
    if salt is None:
        salt = get_random_bytes(16)
    key = PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=iterations)
    return key, salt

def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pkcs7_pad(data))
    # Return: salt not here; salt handled by caller if password-derived key used.
    return iv + ct

def decrypt_bytes(ciphertext: bytes, key: bytes) -> bytes:
    iv = ciphertext[:BLOCK_SIZE]
    ct = ciphertext[BLOCK_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt_padded = cipher.decrypt(ct)
    return pkcs7_unpad(pt_padded)
