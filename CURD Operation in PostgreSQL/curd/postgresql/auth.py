"""
Authentication Logic for 'postgresql' app.

Role of this file:
- Handles user credential validation and password hashing for Usdmast users.
- Connects to:
  1. models.py -> queries Usdmast to find matching users
  2. views.py -> called inside login_view() to verify login form submissions
- Handles dual-password support:
  * Verifies secure PBKDF2/SHA256 Django hashed passwords.
  * Verifies legacy plaintext passwords using constant-time comparison (hmac.compare_digest)
    and automatically upgrades them to secure Django hashes upon successful login.
"""

import hmac

from django.contrib.auth.hashers import check_password, identify_hasher, make_password

from .models import Usdmast


def _is_hashed(value):
    """
    Checks if a password string is already hashed with a known Django algorithm.
    Returns True if valid hash format, False if plaintext legacy password.
    """
    try:
        identify_hasher(value)
        return True
    except ValueError:
        return False


def verify_password(user, raw_password):
    """
    Verifies raw user-entered password against the stored password in database.
    - If stored password is an encrypted hash, checks with Django's check_password().
    - If stored password is plain text (legacy system), checks using hmac.compare_digest().
      Upon successful legacy match, automatically upgrades and hashes the password into PostgreSQL.
    """
    stored = user.usdpwd or ""
    if not stored or not raw_password:
        return False

    # Check 1: Already hashed with modern algorithm
    if _is_hashed(stored):
        return check_password(raw_password, stored)

    # Check 2: Legacy plaintext match (constant-time comparison prevents timing attacks)
    ok = hmac.compare_digest(stored.encode(), raw_password.encode())
    if ok:
        # Transparently upgrade plaintext password to modern Django PBKDF2 hash
        user.usdpwd = make_password(raw_password)
        user.save(update_fields=["usdpwd"])
    return ok


def authenticate_usdmast(usdusd, usdpwd):
    """
    Authenticates a user against the Usdmast PostgreSQL table.
    - Matches username (case-insensitive: usdusd__iexact).
    - Ensures user account is not blocked (usdactflg != 'N').
    - Verifies password.
    
    Returns:
    - (user_object, None) on success
    - (None, "Error message") on failure
    """
    # Find active user by username
    user = (
        Usdmast.objects.filter(usdusd__iexact=usdusd)
        .exclude(usdactflg__iexact="N")
        .order_by("usdcomsno")
        .first()
    )
    if user is None:
        return None, "Invalid User Code"
    
    # Verify the password
    if not verify_password(user, usdpwd):
        return None, "Invalid Password"
        
    return user, None

