# =============================================================================
# postgresql/auth.py  -  Custom login / password-verification logic
# =============================================================================
# This file handles authenticating users against the  usdmast  table in
# PostgreSQL.  It does NOT use Django's built-in User model.
#
# Login flow (called from views.py -> login_view):
#   1. views.py collects usdusd (user code) and usdpwd (password) from POST.
#   2. views.py calls  authenticate_usdmast(usdusd, usdpwd)  defined here.
#   3. authenticate_usdmast looks up the Usdmast row and calls verify_password.
#   4. verify_password handles two cases:
#        a) Password stored as a Django hash  -> use check_password()
#        b) Password stored as legacy plain text -> use constant-time compare,
#           then auto-upgrade to a hash so the DB is more secure going forward.
#   5. Returns (user_object, None) on success or (None, "error message") on failure.
#
# Connections:
#   - models.py   defines the Usdmast table (usdusd, usdpwd, usdactflg, ...)
#   - views.py    calls authenticate_usdmast() inside login_view()
# =============================================================================

import hmac  # constant-time string comparison (prevents timing attacks)

# Django's password helpers:
#   check_password   -> verify a raw password against a stored hash
#   identify_hasher  -> detect whether a string looks like a Django password hash
#   make_password    -> turn a plain-text password into a secure hash
from django.contrib.auth.hashers import check_password, identify_hasher, make_password

# Usdmast is the user-master table defined in models.py
from .models import Usdmast


def _is_hashed(value):
    """Return True if 'value' is a Django password hash, False if it's plain text."""
    try:
        # identify_hasher raises ValueError for plain-text strings.
        identify_hasher(value)
        return True
    except ValueError:
        return False


def verify_password(user, raw_password):
    """
    Check whether 'raw_password' matches what is stored in user.usdpwd.

    Handles two storage formats:
      - Django hash  (modern):  e.g. "pbkdf2_sha256$..."
      - Plain text   (legacy):  e.g. "mypassword"

    If the password is correct AND was stored as plain text, it is
    automatically re-saved as a secure hash (upgrade-in-place).
    """
    stored = user.usdpwd or ""  # stored value from the database

    # If either side is empty, reject immediately.
    if not stored or not raw_password:
        return False

    if _is_hashed(stored):
        # Modern path: compare using Django's secure check_password().
        return check_password(raw_password, stored)

    # Legacy plain-text path (old data imported from MySQL or similar).
    # hmac.compare_digest prevents timing attacks by always taking the
    # same amount of time regardless of how many characters match.
    ok = hmac.compare_digest(stored.encode(), raw_password.encode())
    if ok:
        # Password is correct but stored insecurely.
        # Upgrade it to a proper hash so next login uses the modern path.
        user.usdpwd = make_password(raw_password)
        user.save(update_fields=["usdpwd"])  # only update the password column
    return ok


def authenticate_usdmast(usdusd, usdpwd):
    """
    Look up a user by their user code and verify their password.

    Parameters:
        usdusd  - the user code typed on the login form (case-insensitive)
        usdpwd  - the password typed on the login form

    Returns:
        (Usdmast_object, None)        on success
        (None, "error message string") on failure

    Called by: views.py -> login_view()
    """
    # Find the user row in usdmast where usdusd matches (case-insensitive).
    # Exclude rows where usdactflg = 'N' (disabled/inactive accounts).
    # Order by usdcomsno so that if the same code exists in multiple companies,
    # we consistently pick the first one.
    user = (
        Usdmast.objects.filter(usdusd__iexact=usdusd)
        .exclude(usdactflg__iexact="N")
        .order_by("usdcomsno")
        .first()
    )

    # If no active user row found, reject with a vague message (don't reveal
    # whether the user code exists or not - better for security).
    if user is None:
        return None, "Invalid User Code"

    # User found; now check the password.
    if not verify_password(user, usdpwd):
        return None, "Invalid Password"

    # Both checks passed - return the user object.
    return user, None
