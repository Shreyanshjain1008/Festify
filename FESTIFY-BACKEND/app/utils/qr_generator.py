import qrcode
import io
import base64
import secrets
from app.config.config import Config

def generate_pass_token():
    return secrets.token_urlsafe(32)


def generate_qr_code_base64(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def pass_verify_url(token):
    return f"{Config.PUBLIC_BASE_URL.rstrip('/')}/api/pass/verify/{token}"