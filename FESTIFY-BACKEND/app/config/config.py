import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    OTP_SECRET = os.getenv("OTP_SECRET", os.getenv("SECRET_KEY", "dev-secret-key"))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", "300"))
    # MAIL_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
    # MAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.getenv("SMTP_USERNAME", "")
    # MAIL_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    # MAIL_DEFAULT_SENDER = os.getenv(
    #     "SMTP_FROM_EMAIL",
    #     os.getenv("SMTP_USERNAME", "")
    # )
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
    BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "")
    BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Festify")
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000")