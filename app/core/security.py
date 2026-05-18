import base64
import hashlib
from datetime import datetime, timezone, timedelta
from jose import jwt
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

from app.config.settings import settings


def _get_key(pin: str) -> bytes:
    return hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),
        b'nunchi_salt',
        100000,
        dklen=32
    )


def encrypt(plain_text: str, pin: str) -> str:
    key = _get_key(pin)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return f"{iv}:{ct}"


def decrypt(cipher_text: str, pin: str) -> str:
    key = _get_key(pin)
    iv, ct = cipher_text.split(':')
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')


def create_pin_token(pin: str) -> str:
    # PIN을 토큰 안에 암호화해서 담음
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "pin": encrypt(pin, settings.JWT_SECRET_KEY[:32].ljust(32)[:32]),
        "exp": expire,
        "type": "pin"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_pin_token(token: str) -> str:
    from jose import JWTError
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "pin":
            raise ValueError("PIN 토큰이 아니에요")
        encrypted_pin = payload.get("pin")
        return decrypt(encrypted_pin, settings.JWT_SECRET_KEY[:32].ljust(32)[:32])
    except JWTError:
        raise ValueError("PIN 토큰이 유효하지 않아요")