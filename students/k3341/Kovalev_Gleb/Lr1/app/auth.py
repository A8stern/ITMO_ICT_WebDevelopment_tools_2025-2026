import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PASSWORD_ITERATIONS = 120000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return "pbkdf2_sha256${}${}${}".format(PASSWORD_ITERATIONS, salt, password_hash)


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, iterations, salt, saved_hash = password_hash.split("$")
    if algorithm != "pbkdf2_sha256":
        return False
    calculated_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(calculated_hash, saved_hash)


def encode_base64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def decode_base64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: int) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    expire_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": int(expire_at.timestamp())}
    header_data = encode_base64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_data = encode_base64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = "{}.{}".format(header_data, payload_data)
    signature = hmac.new(
        JWT_SECRET.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return "{}.{}".format(signing_input, encode_base64(signature))


def decode_access_token(token: str) -> Optional[int]:
    try:
        header_data, payload_data, signature_data = token.split(".")
        signing_input = "{}.{}".format(header_data, payload_data)
        expected_signature = hmac.new(
            JWT_SECRET.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        signature = decode_base64(signature_data)
        if not hmac.compare_digest(signature, expected_signature):
            return None
        payload = json.loads(decode_base64(payload_data).decode("utf-8"))
        if int(payload["exp"]) < int(datetime.utcnow().timestamp()):
            return None
        return int(payload["sub"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None
