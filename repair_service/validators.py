# Validators for user inputs

def is_non_empty(value):
    """Check if a string is not empty or just whitespace."""
    if value is None:
        return False
    return len(str(value).strip()) > 0


def is_valid_phone(phone):
    """Check if phone number contains only digits, spaces, dashes, or plus, and has at least 7 digits."""
    if not is_non_empty(phone):
        return False
    cleaned = phone.replace(" ", "").replace("-", "").replace("+", "")
    return cleaned.isdigit() and len(cleaned) >= 7


def is_valid_email(email):
    """Basic email format check: must contain '@' and '.' with characters around them."""
    if not is_non_empty(email):
        return False
    email = email.strip()
    if "@" not in email or "." not in email:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    user_part, domain_part = parts
    if not user_part or not domain_part:
        return False
    if "." not in domain_part or domain_part.startswith(".") or domain_part.endswith("."):
        return False
    return True


def is_valid_price(price_str):
    """Check if price string is a valid non-negative float."""
    try:
        val = float(price_str)
        return val >= 0.0
    except (ValueError, TypeError):
        return False


def is_valid_quantity(qty_str):
    """Check if quantity string is a valid non-negative integer."""
    try:
        val = int(qty_str)
        return val >= 0
    except (ValueError, TypeError):
        return False
