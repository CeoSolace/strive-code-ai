# app/utils/security.py
import os
import re
import hashlib
from typing import List, Dict, Any
import jwt
from datetime import datetime, timedelta

# Hardcoded for demo — in prod: use vault
SECRET_KEY = os.getenv("JWT_SECRET", "strive-code-ai-ultra-secure-entropy-source-2048")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

def sanitize_input(user_input: str) -> str:
    """Remove dangerous patterns."""
    dangerous = [
        r"__import__",
        r"eval\s*\(",
        r"exec\s*\(",
        r"os\.system",
        r"subprocess",
        r"open\s*\(",
        r"__class__",
        r"__bases__",
        r"__subclasses__"
    ]
    clean = user_input
    for pattern in dangerous:
        clean = re.sub(pattern, "[REDACTED]", clean, flags=re.IGNORECASE)
    return clean

def generate_jwt(payload: Dict[str, Any]) -> str:
    """Generate signed JWT."""
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

def hash_password(password: str) -> str:
    """Argon2id hash (requires argon2-cffi)."""
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        return ph.hash(password)
    except:
        # Fallback
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored: str, provided: str) -> bool:
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        return ph.verify(stored, provided)
    except:
        return hashlib.sha256(provided.encode()).hexdigest() == stored

def is_safe_code(code: str, lang: str = "python") -> List[str]:
    """
    Static analysis for dangerous patterns.
    Returns list of warnings.
    """
    warnings = []
    patterns = {
        "python": [
            (r"__import__.*os", "Dangerous import"),
            (r"eval\s*\(", "Code execution"),
            (r"subprocess\.call", "Shell injection"),
            (r"open\s*\(.*['\"]w['\"]", "File write"),
        ],
        "javascript": [
            (r"eval\s*\(", "Code execution"),
            (r"child_process", "Shell access"),
        ]
    }

    for pattern, msg in patterns.get(lang, []):
        if re.search(pattern, code, re.IGNORECASE):
            warnings.append(msg)

    return warnings
