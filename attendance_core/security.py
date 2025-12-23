from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import secrets
def hash_password(pw: str) -> str:
    return generate_password_hash(pw, method="pbkdf2:sha256", salt_length=16)
def verify_password(pw: str, pw_hash: str) -> bool:
    return check_password_hash(pw, pw_hash)
def create_session(user_id: int, role: str):
    session.clear()
    session["uid"] = user_id
    session["role"] = role
    session["csrf"] = secrets.token_urlsafe(32)
