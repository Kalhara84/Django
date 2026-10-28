"""
Login logic  -  PHP login.php eke wage:
  * usdmast eken usdusd (user code) hoyanawa, usdactflg != 'N'
  * usdpwd eka check karanawa
Password eka hash karala thiyenawa nam check_password, parana plain text nam
compare karala, login wunama auto hash karala update karanawa.
"""
import hmac

from django.contrib.auth.hashers import check_password, identify_hasher, make_password

from .models import Usdmast


def _is_hashed(value):
    try:
        identify_hasher(value)
        return True
    except ValueError:
        return False


def verify_password(user, raw_password):
    stored = user.usdpwd or ""
    if not stored or not raw_password:
        return False
    if _is_hashed(stored):
        return check_password(raw_password, stored)
    # legacy plain-text (old MySQL data)
    ok = hmac.compare_digest(stored.encode(), raw_password.encode())
    if ok:
        user.usdpwd = make_password(raw_password)
        user.save(update_fields=["usdpwd"])
    return ok


def authenticate_usdmast(usdusd, usdpwd):
    """Returns (user, error_message)."""
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
