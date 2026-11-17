from functools import wraps

from flask import request, jsonify, g

from app.utils.token import decode_token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Authorization header is required"
            }), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Invalid authorization format"
            }), 401

        token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return jsonify({
                "success": False,
                "message": "Token is required"
            }), 401

        payload = decode_token(token)

        if not payload:
            return jsonify({
                "success": False,
                "message": "Invalid or expired token"
            }), 401

        g.user = payload

        return f(*args, **kwargs)

    return decorated