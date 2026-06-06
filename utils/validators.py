"""Input validation utilities"""
import re

def is_valid_user_id(user_id) -> bool:
    """Validate Telegram user ID"""
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False

def is_valid_level(level: int) -> bool:
    """Validate level is within valid range"""
    return 1 <= level <= 250

def is_valid_meso_amount(amount: int) -> bool:
    """Validate meso amount"""
    return 0 <= amount <= 999999999

def is_valid_nx_amount(amount: int) -> bool:
    """Validate NX amount"""
    return 0 <= amount <= 999999

def is_valid_stars(stars: int) -> bool:
    """Validate equipment stars"""
    return 0 <= stars <= 25

def sanitize_username(username: str) -> str:
    """Sanitize username for display"""
    return re.sub(r'[^a-zA-Z0-9_]', '', username)[:20]

def is_valid_amount_string(text: str) -> tuple[bool, int]:
    """Parse amount string like '+1000' or '=5000'"""
    if not text or len(text) < 2:
        return False, 0
    
    operator = text[0]
    if operator not in ['+', '=']:
        return False, 0
    
    try:
        amount = int(text[1:])
        if amount < 0:
            return False, 0
        return True, amount
    except ValueError:
        return False, 0
