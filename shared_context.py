import secret, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class EncryptionContext:
    def __init__(self, key: bytes, sender_id: bytes, recipient_id: bytes):
        self.key = key
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.aes = AESGCM(self.key)

    def protect(self, payload: bytes) -> bytes:
        nonce = os.urandom(12)
        aad = "".encode()
        ciphertext = self.aes.encrypt(nonce, payload, aad)
        return nonce + ciphertext

    def unprotect(self, protected_data: bytes) -> bytes:
        nonce = protected_data[:12]
        ciphertext = protected_data[12:]
        aad = "".encode()
        return self.aes.decrypt(nonce, ciphertext, aad)