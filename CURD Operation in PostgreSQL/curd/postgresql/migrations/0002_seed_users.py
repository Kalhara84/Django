import datetime

from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed(apps, schema_editor):
    Usdmast = apps.get_model("postgresql", "Usdmast")

    rows = [
        dict(
            usdsno=1, usdusd="2000", usdcomsno=0, usdnam="2000", usdpwd=make_password("2000 rbf"),
            usddesig="", usddepsno=4, usdlocsno=1, usduno="", usdemail="rumeshdezoysa@gmail.com",
            usdadmin="Y", usdactflg="Y", usdbockpodgrnyn="",
            usdbrcsalyn="Y", usdlacsalyn="Y", usdprnsalyn="Y", usdeggsalyn="Y", usdccnsalyn="Y",
            usdpgfsalyn="Y", usdcafsalyn="Y", usdmaisalyn="Y", usdhegsalyn="Y", usdhassalyn="Y",
            usdsalstkcatsnos="716,741,742,743,744,745,746,747,748,749,750,756,764,765,794,795,796,797,798,827,828",
            usdrepyn="", usdstkrolyn="Y", usdprintername="", usdatfauthyn="",
            usdatfliamt=0, usdatfnosetday=0, usdpwdddt=None, usdsohpvalyn="",
            usducdnew="2000", usdentddt=datetime.date(2022, 5, 13), usdenttime="",
            usducdame="2000", usdameddt=datetime.date(2026, 8, 28), usdametime=datetime.time(9, 45, 58),
        ),
        dict(
            usdsno=2, usdusd="ADMIN", usdcomsno=0, usdnam="ADMIN", usdpwd=make_password("0777289242"),
            usddesig="", usddepsno=7, usdlocsno=1, usduno="100", usdemail="",
            usdadmin="Y", usdactflg="Y", usdbockpodgrnyn="",
            usdbrcsalyn="", usdlacsalyn="", usdprnsalyn="", usdeggsalyn="", usdccnsalyn="",
            usdpgfsalyn="", usdcafsalyn="", usdmaisalyn="", usdhegsalyn="", usdhassalyn="",
            usdsalstkcatsnos="", usdrepyn="", usdstkrolyn="", usdprintername="", usdatfauthyn="",
            usdatfliamt=0, usdatfnosetday=0, usdpwdddt=datetime.date(2030, 1, 1), usdsohpvalyn="",
            usducdnew="", usdentddt=None, usdenttime="",
            usducdame="2000", usdameddt=datetime.date(2025, 8, 13), usdametime=datetime.time(15, 21, 31),
        ),
    ]
    for r in rows:
        if not Usdmast.objects.filter(usdusd=r["usdusd"], usdcomsno=r["usdcomsno"]).exists():
            Usdmast.objects.create(**r)

    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cur:
            cur.execute(
                "SELECT setval(pg_get_serial_sequence('usdmast', 'usdsno'), "
                "COALESCE((SELECT MAX(usdsno) FROM usdmast), 1))"
            )


class Migration(migrations.Migration):
    dependencies = [("postgresql", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
