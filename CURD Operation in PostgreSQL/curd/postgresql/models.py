from django.db import models


def yn():
    """1 character flag column: 'Y' or '' (same as the MySQL table)."""
    return models.CharField(max_length=1, blank=True, default="")


class Usdmast(models.Model):
    usdsno = models.AutoField(primary_key=True)                       # auto_increment
    usdusd = models.CharField(max_length=30)                          # user code (login name)
    usdcomsno = models.IntegerField(default=0)
    usdnam = models.CharField(max_length=50, null=True, blank=True)   # full name
    usdpwd = models.CharField(max_length=128, null=True, blank=True)
    usddesig = models.CharField(max_length=25, blank=True, default="")
    usddepsno = models.IntegerField(default=0)
    usdlocsno = models.IntegerField(default=0)
    usduno = models.CharField(max_length=4, blank=True, default="")
    usdemail = models.CharField(max_length=40, blank=True, default="")
    usdadmin = yn()
    usdactflg = yn()
    usdbockpodgrnyn = yn()
    usdbrcsalyn = yn()
    usdlacsalyn = yn()
    usdprnsalyn = yn()
    usdeggsalyn = yn()
    usdccnsalyn = yn()
    usdpgfsalyn = yn()
    usdcafsalyn = yn()
    usdmaisalyn = yn()
    usdhegsalyn = yn()
    usdhassalyn = yn()
    usdsalstkcatsnos = models.CharField(max_length=100, blank=True, default="")
    usdrepyn = yn()
    usdstkrolyn = yn()
    usdprintername = models.CharField(max_length=30, blank=True, default="")
    usdatfauthyn = yn()
    usdatfliamt = models.IntegerField(default=0)
    usdatfnosetday = models.IntegerField(default=0)
    usdpwdddt = models.DateField(null=True, blank=True)
    usdsohpvalyn = yn()
    usducdnew = models.CharField(max_length=10, blank=True, default="")      # created by
    usdentddt = models.DateField(null=True, blank=True)                      # created date
    usdenttime = models.CharField(max_length=12, blank=True, default="")     # created time
    usducdame = models.CharField(max_length=30, null=True, blank=True)       # LAST UPDATED BY
    usdameddt = models.DateField(null=True, blank=True)                      # last updated date
    usdametime = models.TimeField(null=True, blank=True)                     # last updated time

    class Meta:
        db_table = "usdmast"
        ordering = ["usdsno"]
        constraints = [
            models.UniqueConstraint(fields=["usdusd", "usdcomsno"], name="usdmast_usdusd_usdcomsno_uniq"),
        ]

    def __str__(self):
        return f"{self.usdusd} - {self.usdnam or ''}"

    @property
    def is_admin(self):
        return (self.usdadmin or "").upper() == "Y"

    @property
    def is_active_user(self):
        return (self.usdactflg or "").upper() != "N"
