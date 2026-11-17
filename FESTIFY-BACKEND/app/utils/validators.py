import re
from datetime import datetime


def validate_custom_field_value(field_type, value, field_options=None):
    
    if field_type == "EMAIL":
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", str(value)):
            return False, "must be a valid email address"

    elif field_type == "NUMBER":
        try:
            float(value)
        except (ValueError, TypeError):
            return False, "must be a number"

    elif field_type == "DATE":
        try:
            datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            return False, "must be a valid date in YYYY-MM-DD format"

    elif field_type == "URL":
        if not re.match(r"^https?://[^\s]+$", str(value)):
            return False, "must be a valid URL starting with http:// or https://"

    elif field_type == "DROPDOWN":
        options = [opt.strip() for opt in (field_options or "").split(",")]
        if value not in options:
            return False, f"must be one of: {', '.join(options)}"

    return True, None