from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from base64 import b64encode, b64decode
import os, secret, hmac, hashlib

def protect(pt: str):
    with open(secret.MQTT_KEY, "rb") as f:
        key = f.read()
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, pt.encode(), None)
    h = hmac.new(key, iv + ciphertext, hashlib.sha256)
    signature = h.digest()
    return iv + ciphertext + signature

def unprotect(ct: bytes):
    with open(secret.MQTT_KEY, "rb") as f:
        key = f.read()
    aesgcm = AESGCM(key)
    iv = ct[0:12]
    ciphertext = ct[12:-32]
    signature = ct[-32:]

    expected_hmac = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_hmac):
        print("⚠️ Подпись недействительна! Сообщение отклонено.")
        return
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode()