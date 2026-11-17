import jwt
from datetime import datetime, timedelta, timezone

from app.config.config import Config


def generate_token(user):
    payload = {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    return jwt.encode(
        payload,
        Config.JWT_SECRET_KEY,
        algorithm="HS256"
    )


def decode_token(token):
    try:
        return jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None