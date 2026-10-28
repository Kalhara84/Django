# =============================================================================
# postgresql/migrations/0004_seed_expire_data.py  -  Database Migration: Expire Seed Data
# =============================================================================
# This migration populates the Expire lookup tables with initial master data:
#
#   1. Excmast   - Categories (MED, VAC, FEED, PKG, CHM)
#   2. Exlocmast - Locations (MAIN, FARM1, FARM2, HATCH, COLD)
#   3. Exsmast   - Services/Actions (INSP, REORD, DISP, RETN, QC)
#   4. Expmast   - Expiry reminder periods (1 WEEK, 2 WEEKS, 1 MONTH, etc.)
#   5. GGenmast  - Stock and write-off accounts (1100-001, 1100-002, 5100-001, etc.)
#
# Related Files:
#   - postgresql/models.py       : Defines model schemas for the tables populated here.
#   - postgresql/expire_forms.py : lookup_choices() reads these rows to build UI dropdowns.
# =============================================================================

import datetime
from django.db import migrations

# Fixed reference date & time for audit stamps on seeded records
NOW_D = datetime.date.today()
NOW_T = datetime.time(9, 0, 0)


def audit(prefix):
    """
    Helper function generating creation audit fields for the specified table prefix.
    Example: prefix='exc' -> {'excucdnew': 'ADMIN', 'excentddt': ..., 'excenttime': ...}
    """
    return {
        f"{prefix}ucdnew": "ADMIN",
        f"{prefix}entddt": NOW_D,
        f"{prefix}enttime": NOW_T,
    }


def seed(apps, schema_editor):
    """
    Inserts initial lookup records for Categories, Locations, Services, Periods,
    and GL Accounts using get_or_create to prevent duplicate keys if re-run.
    """
    # Load historical models from migration context
    Excmast = apps.get_model("postgresql", "Excmast")
    Exlocmast = apps.get_model("postgresql", "Exlocmast")
    Exsmast = apps.get_model("postgresql", "Exsmast")
    Expmast = apps.get_model("postgresql", "Expmast")
    GGenmast = apps.get_model("postgresql", "GGenmast")

    # 1. Seed Categories (excmast)
    for code, name in [
        ("MED", "Medicine"),
        ("VAC", "Vaccines"),
        ("FEED", "Feed"),
        ("PKG", "Packing Material"),
        ("CHM", "Chemicals")
    ]:
        Excmast.objects.get_or_create(excexc=code, defaults=dict(excnam=name, **audit("exc")))

    # 2. Seed Locations / Warehouses (exlocmast)
    for code, name in [
        ("MAIN", "Main Store"),
        ("FARM1", "Farm 1 Store"),
        ("FARM2", "Farm 2 Store"),
        ("HATCH", "Hatchery"),
        ("COLD", "Cold Room")
    ]:
        Exlocmast.objects.get_or_create(exlocloc=code, defaults=dict(exlocnam=name, **audit("exloc")))

    # 3. Seed Service / Action Types (exsmast)
    for code, name in [
        ("INSP", "Inspection"),
        ("REORD", "Re-order"),
        ("DISP", "Disposal"),
        ("RETN", "Return to Supplier"),
        ("QC", "Quality Check")
    ]:
        Exsmast.objects.get_or_create(exsexs=code, defaults=dict(exsnam=name, **audit("exs")))

    # 4. Seed Expiry Periods and durations in days (expmast)
    for code, days in [
        ("1 WEEK", 7),
        ("2 WEEKS", 14),
        ("1 MONTH", 30),
        ("2 MONTHS", 60),
        ("3 MONTHS", 90),
        ("6 MONTHS", 180)
    ]:
        Expmast.objects.get_or_create(expexp=code, defaults=dict(expdays=days, **audit("exp")))

    # 5. Seed General Ledger Accounts (g_genmast)
    for ctl, sub, des in [
        ("1100", "001", "Medicine Stock"),
        ("1100", "002", "Vaccine Stock"),
        ("1200", "001", "Feed Stock"),
        ("1300", "001", "Packing Material Stock"),
        ("5100", "001", "Expired Stock Write-off"),
        ("5100", "002", "Damaged Stock Write-off"),
        ("5200", "001", "Stock Adjustment")
    ]:
        GGenmast.objects.get_or_create(
            genctl=ctl,
            gensub=sub,
            defaults=dict(
                gendes=des,
                gendes1=des[:30],
                genctlsub=ctl + sub,
                gencde="N",
                **audit("gen")
            ),
        )


class Migration(migrations.Migration):
    # Depends on migration 0003 where tables were created
    dependencies = [("postgresql", "0003_expire_tables")]

    # Forward migration calls seed(); backward does nothing (noop)
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
