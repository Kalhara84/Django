# =============================================================================
# postgresql/auth.py - checks the user code and password
# =============================================================================
# Used by: views.py (login_view)
# Uses:    models.py (Usdmast table)
# Passwords are stored hashed. An old plain-text password still works once,
# then it is saved as a hash automatically.
# =============================================================================
import hmac

from django.contrib.auth.hashers import check_password, identify_hasher, make_password

from .models import Usdmast


def _is_hashed(value):
    """True if the stored password is already a Django hash."""
    try:
        identify_hasher(value)
        return True
    except ValueError:
        return False


def verify_password(user, raw_password):
    """Compare the typed password with the one in usdpwd."""
    stored = user.usdpwd or ""

    # Empty password never matches
    if not stored or not raw_password:
        return False

    # Normal case: hashed password
    if _is_hashed(stored):
        return check_password(raw_password, stored)

    # Old plain-text password: compare, and if correct, replace it with a hash
    ok = hmac.compare_digest(stored.encode(), raw_password.encode())
    if ok:
        user.usdpwd = make_password(raw_password)
        user.save(update_fields=["usdpwd"])
    return ok


def authenticate_usdmast(usdusd, usdpwd):
    """Return (user, None) if login is OK, or (None, error message)."""
    # Find the user code (any letter case) that is not blocked (usdactflg = 'N')
    user = (
        Usdmast.objects.filter(usdusd__iexact=usdusd)
        .exclude(usdactflg__iexact="N")
        .order_by("usdcomsno")
        .first()
    )

    if user is None:
        return None, "Invalid User Code"

    if not verify_password(user, usdpwd):
        return None, "Invalid Password"

    return user, None
