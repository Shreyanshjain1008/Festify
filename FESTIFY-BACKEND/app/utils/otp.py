import random
import hashlib
import hmac
import time

from app.config.config import Config


# Temporary in-memory OTP storage.
# Key: email
# Value: {
#     "otp_hash": "...",
#     "created_at": 1234567890.0
# }
_otp_store = {}

# Temporary in-memory verified-email storage.
# Key: email
# Value: verification timestamp
_verified_emails = {}


def generate_otp():
    return f"{random.randint(100000, 999999)}"


def hash_otp(otp):
    if not Config.OTP_SECRET:
        raise ValueError("OTP_SECRET is not configured")

    return hmac.new(
        Config.OTP_SECRET.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def store_otp(email, otp):
    email = email.strip().lower()

    otp_hash = hash_otp(otp)

    _otp_store[email] = {
        "otp_hash": otp_hash,
        "created_at": time.time()
    }


def verify_otp(email, otp):
    email = email.strip().lower()

    record = _otp_store.get(email)

    if not record:
        return False, "OTP not found. Please request a new OTP."

    if is_otp_expired(record["created_at"]):
        _otp_store.pop(email, None)

        return False, "OTP has expired. Please request a new OTP."

    expected_hash = record["otp_hash"]
    provided_hash = hash_otp(otp)

    if not hmac.compare_digest(expected_hash, provided_hash):
        return False, "Invalid OTP"

    # OTP can only be used once.
    _otp_store.pop(email, None)

    # Mark email as verified.
    _verified_emails[email] = time.time()

    return True, "OTP verified successfully"


def is_email_verified(email):
    email = email.strip().lower()

    return email in _verified_emails


def clear_email_verification(email):
    email = email.strip().lower()

    _verified_emails.pop(email, None)


def is_otp_expired(created_at):
    return (
        time.time() - created_at
        > Config.OTP_EXPIRY_SECONDS
    )