# =============================================================================
# postgresql/migrations/0002_seed_users.py  -  Database Migration: Initial Data
# =============================================================================
# This migration populates the 'usdmast' table with initial default users
# ('2000' and 'ADMIN') upon running initial database migrations.
#
# Default Users Created:
#   1. Username: "2000"  (Password: "2000 rbf") - Full Administrator Account
#   2. Username: "ADMIN" (Password: "0777289242") - System Administrator Account
#
# Related Files:
#   - postgresql/models.py: Usdmast model representation.
#   - postgresql/auth.py: Authenticates these seeded users using PBKDF2 hash checking.
# =============================================================================

import datetime

# Django password hashing utility to store passwords securely using PBKDF2
from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed(apps, schema_editor):
    """
    Data migration function that inserts default admin users if they do not
    already exist in the usdmast table.
    """
    # Fetch the historical model version matching this migration state
    Usdmast = apps.get_model("postgresql", "Usdmast")

    rows = [
        # User 1: Administrator '2000'
        dict(
            usdsno=1, usdusd="2000", usdcomsno=0, usdnam="2000",
            usdpwd=make_password("2000 rbf"), # Hash password securely before saving
            usddesig="", usddepsno=4, usdlocsno=1, usduno="",
            usdemail="rumeshdezoysa@gmail.com",
            usdadmin="Y", usdactflg="Y", usdbockpodgrnyn="",
            usdbrcsalyn="Y", usdlacsalyn="Y", usdprnsalyn="Y", usdeggsalyn="Y", usdccnsalyn="Y",
            usdpgfsalyn="Y", usdcafsalyn="Y", usdmaisalyn="Y", usdhegsalyn="Y", usdhassalyn="Y",
            usdsalstkcatsnos="716,741,742,743,744,745,746,747,748,749,750,756,764,765,794,795,796,797,798,827,828",
            usdrepyn="", usdstkrolyn="Y", usdprintername="", usdatfauthyn="",
            usdatfliamt=0, usdatfnosetday=0, usdpwdddt=None, usdsohpvalyn="",
            usducdnew="2000", usdentddt=datetime.date(2022, 5, 13), usdenttime="",
            usducdame="2000", usdameddt=datetime.date(2026, 8, 28), usdametime=datetime.time(9, 45, 58),
        ),
        # User 2: Administrator 'ADMIN'
        dict(
            usdsno=2, usdusd="ADMIN", usdcomsno=0, usdnam="ADMIN",
            usdpwd=make_password("0777289242"), # Hash password securely before saving
            usddesig="", usddepsno=7, usdlocsno=1, usduno="100",
            usdemail="",
            usdadmin="Y", usdactflg="Y", usdbockpodgrnyn="",
            usdbrcsalyn="", usdlacsalyn="", usdprnsalyn="", usdeggsalyn="", usdccnsalyn="",
            usdpgfsalyn="", usdcafsalyn="", usdmaisalyn="", usdhegsalyn="", usdhassalyn="",
            usdsalstkcatsnos="", usdrepyn="", usdstkrolyn="", usdprintername="", usdatfauthyn="",
            usdatfliamt=0, usdatfnosetday=0, usdpwdddt=datetime.date(2030, 1, 1), usdsohpvalyn="",
            usducdnew="", usdentddt=None, usdenttime="",
            usducdame="2000", usdameddt=datetime.date(2025, 8, 13), usdametime=datetime.time(15, 21, 31),
        ),
    ]

    # Create each record if not already present (idempotent seeding)
    for r in rows:
        if not Usdmast.objects.filter(usdusd=r["usdusd"], usdcomsno=r["usdcomsno"]).exists():
            Usdmast.objects.create(**r)

    # In PostgreSQL, explicitly sync the serial sequence to match the highest primary key ID
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cur:
            cur.execute(
                "SELECT setval(pg_get_serial_sequence('usdmast', 'usdsno'), "
                "COALESCE((SELECT MAX(usdsno) FROM usdmast), 1))"
            )


class Migration(migrations.Migration):
    # Depends on initial table creation migration 0001
    dependencies = [("postgresql", "0001_initial")]

    # Run the seed function forwards; do nothing on rollback (noop)
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
