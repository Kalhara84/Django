# =============================================================================
# migrations/0004_seed_expire_data.py - dummy data for the Expire Module combo boxes
# =============================================================================
# Fills: excmast, exlocmast, exsmast, expmast, g_genmast.
# Replace or delete these rows when real data is available.
# =============================================================================
import datetime
from django.db import migrations

# Date and time written in the "created" columns of the dummy rows
NOW_D = datetime.date.today()
NOW_T = datetime.time(9, 0, 0)


# Created-by / date / time columns for a table. prefix = exc, exloc, exs, exp or gen.
def audit(prefix):
    return {
        f"{prefix}ucdnew": "ADMIN",
        f"{prefix}entddt": NOW_D,
        f"{prefix}enttime": NOW_T,
    }


# Inserts dummy data into the combo box tables (skips rows that already exist).
def seed(apps, schema_editor):

    Excmast = apps.get_model("postgresql", "Excmast")
    Exlocmast = apps.get_model("postgresql", "Exlocmast")
    Exsmast = apps.get_model("postgresql", "Exsmast")
    Expmast = apps.get_model("postgresql", "Expmast")
    GGenmast = apps.get_model("postgresql", "GGenmast")

    # Item categories (excmast)
    for code, name in [
        ("MED", "Medicine"),
        ("VAC", "Vaccines"),
        ("FEED", "Feed"),
        ("PKG", "Packing Material"),
        ("CHM", "Chemicals")
    ]:
        Excmast.objects.get_or_create(excexc=code, defaults=dict(excnam=name, **audit("exc")))

    # Locations (exlocmast)
    for code, name in [
        ("MAIN", "Main Store"),
        ("FARM1", "Farm 1 Store"),
        ("FARM2", "Farm 2 Store"),
        ("HATCH", "Hatchery"),
        ("COLD", "Cold Room")
    ]:
        Exlocmast.objects.get_or_create(exlocloc=code, defaults=dict(exlocnam=name, **audit("exloc")))

    # Service categories (exsmast)
    for code, name in [
        ("INSP", "Inspection"),
        ("REORD", "Re-order"),
        ("DISP", "Disposal"),
        ("RETN", "Return to Supplier"),
        ("QC", "Quality Check")
    ]:
        Exsmast.objects.get_or_create(exsexs=code, defaults=dict(exsnam=name, **audit("exs")))

    # Periods (expmast): name and number of days
    for code, days in [
        ("1 WEEK", 7),
        ("2 WEEKS", 14),
        ("1 MONTH", 30),
        ("2 MONTHS", 60),
        ("3 MONTHS", 90),
        ("6 MONTHS", 180)
    ]:
        Expmast.objects.get_or_create(expexp=code, defaults=dict(expdays=days, **audit("exp")))

    # Accounts (g_genmast): control code, sub code, description
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

    dependencies = [("postgresql", "0003_expire_tables")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
