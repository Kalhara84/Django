# =============================================================================
# postgresql/models.py - database tables (one class = one table)
# =============================================================================
# "python manage.py migrate" creates these tables in PostgreSQL
# (see the files in migrations/). Column names are the same as the old MySQL tables.
#
# Users tab:      Usdmast
# Expire Module:  Exhmast (header)  +  Exlmast (lines)
#                 Excmast, Exlocmast, Exsmast, Expmast, GGenmast = data for the combo boxes
#
# Used by: views.py, expire_views.py, forms.py, expire_forms.py, auth.py
# =============================================================================
from django.db import models


# Short way to write a 1-letter Yes/No column: 'Y' or empty.
def yn():
    return models.CharField(max_length=1, blank=True, default="")


# USERS (table usdmast): used for login and the Users tab.
class Usdmast(models.Model):
    # Auto number (primary key)
    usdsno = models.AutoField(primary_key=True)

    # User code = the name typed on the login page
    usdusd = models.CharField(max_length=30)

    usdcomsno = models.IntegerField(default=0)

    usdnam = models.CharField(max_length=50, null=True, blank=True)

    # Password (stored as a hash, so the length is 128)
    usdpwd = models.CharField(max_length=128, null=True, blank=True)

    usddesig = models.CharField(max_length=25, blank=True, default="")

    usddepsno = models.IntegerField(default=0)

    usdlocsno = models.IntegerField(default=0)

    usduno = models.CharField(max_length=4, blank=True, default="")

    usdemail = models.CharField(max_length=40, blank=True, default="")

    # Y = admin user (can open the Users tab)
    usdadmin = yn()

    # Y = active, N = blocked (cannot login)
    usdactflg = yn()

    # Permission flags (Y / empty)
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

    # Date the password was last changed (empty = never)
    usdpwdddt = models.DateField(null=True, blank=True)

    usdsohpvalyn = yn()

    # Created by / date / time
    usducdnew = models.CharField(max_length=10, blank=True, default="")
    usdentddt = models.DateField(null=True, blank=True)
    usdenttime = models.CharField(max_length=12, blank=True, default="")

    # Last updated by / date / time (shown in the Users list)
    usducdame = models.CharField(max_length=30, null=True, blank=True)
    usdameddt = models.DateField(null=True, blank=True)
    usdametime = models.TimeField(null=True, blank=True)

    class Meta:
        # Table name in PostgreSQL
        db_table = "usdmast"

        ordering = ["usdsno"]

        # Same user code cannot be used twice in one company
        constraints = [
            models.UniqueConstraint(fields=["usdusd", "usdcomsno"], name="usdmast_usdusd_usdcomsno_uniq"),
        ]

    def __str__(self):
        return f"{self.usdusd} - {self.usdnam or ''}"

    # True when usdadmin = 'Y' (used by decorators.py and the sidebar)
    @property
    def is_admin(self):
        return (self.usdadmin or "").upper() == "Y"

    # True unless usdactflg = 'N' (used by auth.py and decorators.py)
    @property
    def is_active_user(self):
        return (self.usdactflg or "").upper() != "N"


# ITEM CATEGORY (excmast): data for the Item Category combo box.
class Excmast(models.Model):
    excsno = models.AutoField(primary_key=True)

    excexc = models.CharField(max_length=40, default="")

    excnam = models.CharField(max_length=40, default="")

    excusdsno = models.IntegerField(null=True, blank=True)
    excucdnew = models.CharField(max_length=30, null=True, blank=True)
    excentddt = models.DateField(null=True, blank=True)
    excenttime = models.TimeField(null=True, blank=True)
    excucdame = models.CharField(max_length=30, null=True, blank=True)
    excameddt = models.DateField(null=True, blank=True)
    excametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "excmast"
        ordering = ["excexc"]
        constraints = [models.UniqueConstraint(fields=["excexc"], name="excmast_excexc_uniq")]

    def __str__(self):
        return f"{self.excexc} - {self.excnam}"


# LOCATION (exlocmast): data for the Location combo box.
# (New locations are added from the "Add Location" pop-up on the Expire form.)
class Exlocmast(models.Model):
    exlocsno = models.AutoField(primary_key=True)

    exlocloc = models.CharField(max_length=40, default="")

    exlocnam = models.CharField(max_length=40, default="")

    exlocucdnew = models.CharField(max_length=30, null=True, blank=True)
    exlocentddt = models.DateField(null=True, blank=True)
    exlocenttime = models.TimeField(null=True, blank=True)
    exlocucdame = models.CharField(max_length=30, null=True, blank=True)
    exlocameddt = models.DateField(null=True, blank=True)
    exlocametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "exlocmast"
        ordering = ["exlocloc"]
        constraints = [models.UniqueConstraint(fields=["exlocloc"], name="exlocmast_exlocloc_uniq")]

    def __str__(self):
        return f"{self.exlocloc} - {self.exlocnam}"


# SERVICE CATEGORY (exsmast): data for the Service Cat combo box in the lines.
class Exsmast(models.Model):
    exssno = models.AutoField(primary_key=True)

    exsexs = models.CharField(max_length=40, default="")

    exsnam = models.CharField(max_length=40, default="")

    exsucdnew = models.CharField(max_length=30, null=True, blank=True)
    exsentddt = models.DateField(null=True, blank=True)
    exsenttime = models.TimeField(null=True, blank=True)
    exsucdame = models.CharField(max_length=30, null=True, blank=True)
    exsameddt = models.DateField(null=True, blank=True)
    exsametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "exsmast"
        ordering = ["exsexs"]
        constraints = [models.UniqueConstraint(fields=["exsexs"], name="exsmast_exsexs_uniq")]

    def __str__(self):
        return f"{self.exsexs} - {self.exsnam}"


# PERIOD (expmast): data for the Period combo box in the lines (expdays = number of days).
class Expmast(models.Model):
    expsno = models.AutoField(primary_key=True)

    expexp = models.CharField(max_length=40, default="")

    expdays = models.IntegerField(null=True, blank=True)

    expucdnew = models.CharField(max_length=30, null=True, blank=True)
    expentddt = models.DateField(null=True, blank=True)
    expenttime = models.TimeField(null=True, blank=True)
    expucdame = models.CharField(max_length=30, null=True, blank=True)
    expameddt = models.DateField(null=True, blank=True)
    expametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "expmast"

        ordering = ["expdays", "expexp"]
        constraints = [models.UniqueConstraint(fields=["expexp"], name="expmast_expexp_uniq")]

    def __str__(self):
        return f"{self.expexp} ({self.expdays} days)"


# ACCOUNT MASTER (g_genmast): data for the Acc Code combo box in the lines.
class GGenmast(models.Model):
    gensno = models.AutoField(primary_key=True)

    genctl = models.CharField(max_length=8)

    gensub = models.CharField(max_length=4, default="", blank=True)

    genctlsub = models.CharField(max_length=8, default="", blank=True)

    gendebint = models.CharField(max_length=1, default="", blank=True)
    gencrdint = models.CharField(max_length=1, default="", blank=True)

    gendes = models.CharField(max_length=60, null=True, blank=True)
    gendes1 = models.CharField(max_length=30, default="", blank=True)

    genmapcode = models.CharField(max_length=15, null=True, blank=True)

    gencde = models.CharField(max_length=1, null=True, blank=True)

    gencomsno = models.IntegerField(default=0)
    genlocsno = models.IntegerField(default=0)
    gencatsno = models.IntegerField(null=True, blank=True)
    genaansno = models.IntegerField(null=True, blank=True)
    gencursno = models.IntegerField(default=0)
    genjobsno = models.IntegerField(default=0)
    genempsno = models.IntegerField(default=0)
    gengrpsno = models.IntegerField(default=0)
    genectsno = models.IntegerField(default=0)

    gensupyn = models.CharField(max_length=1, null=True, blank=True)
    genjobyn = models.CharField(max_length=1, null=True, blank=True)
    gendepyn = models.CharField(max_length=1, default="", blank=True)
    genempyn = models.CharField(max_length=1, default="", blank=True)
    gencusyn = models.CharField(max_length=1, default="", blank=True)
    genictyn = models.CharField(max_length=1, default="", blank=True)
    genadvyn = models.CharField(max_length=1, default="", blank=True)
    genappyn = models.CharField(max_length=1, default="", blank=True)
    gencamyn = models.CharField(max_length=1, default="", blank=True)
    genvehyn = models.CharField(max_length=1, default="", blank=True)
    genlocyn = models.CharField(max_length=1, default="", blank=True)

    genrate = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    genbnkprefix = models.CharField(max_length=5, default="", blank=True)
    genoticrdacc = models.CharField(max_length=12, default="", blank=True)

    genucdnew = models.CharField(max_length=30, null=True, blank=True)
    genentddt = models.DateField(null=True, blank=True)
    genenttime = models.TimeField(null=True, blank=True)
    genucdame = models.CharField(max_length=30, null=True, blank=True)
    genameddt = models.DateField(null=True, blank=True)
    genametime = models.TimeField(null=True, blank=True)

    gentemp = models.CharField(max_length=1, default="", blank=True)

    class Meta:
        db_table = "g_genmast"
        ordering = ["genctl", "gensub"]

        constraints = [models.UniqueConstraint(fields=["genctl", "gensub"], name="g_genmast_genctl_gensub_uniq")]

    def __str__(self):
        return f"{self.genctl}-{self.gensub} {self.gendes or ''}"


# EXPIRE ENTRY - HEADER (exhmast): one row per entry (top part of the form).
# Its lines are in Exlmast.
class Exhmast(models.Model):
    exhsno = models.AutoField(primary_key=True)

    # Entry code (must be unique)
    exhdno = models.CharField(max_length=30, unique=True)

    # id of the Item Category (excmast.excsno)
    exhexcsno = models.IntegerField()

    # id of the Location (exlocmast.exlocsno)
    exhexlocsno = models.IntegerField()

    exhddt = models.DateField()

    exhdes = models.CharField(max_length=50)

    exhucdnew = models.CharField(max_length=30, null=True, blank=True)
    exhentddt = models.DateField(null=True, blank=True)
    exhenttime = models.TimeField(null=True, blank=True)
    exhucdame = models.CharField(max_length=30, null=True, blank=True)
    exhameddt = models.DateField(null=True, blank=True)
    exhametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "exhmast"

        ordering = ["-exhsno"]

    def __str__(self):
        return self.exhdno


# EXPIRE ENTRY - LINES (exlmast): the table rows of an entry.
# exlexhsno = exhsno of the header, exllno = line number 1, 2, 3 ...
class Exlmast(models.Model):
    exlsno = models.AutoField(primary_key=True)

    # Link to the header (exhmast.exhsno)
    exlexhsno = models.IntegerField(default=0)

    exllno = models.IntegerField(default=0)

    # ids of the Service Cat (exsmast), Period (expmast), Acc Code (g_genmast)
    exlexssno = models.IntegerField()
    exlexpsno = models.IntegerField()
    exlgensno = models.IntegerField()

    # Complete date and cutoff date
    exlcomplddt = models.DateField(null=True, blank=True)
    exlcutoffddt = models.DateField(null=True, blank=True)

    exlucdnew = models.CharField(max_length=30, null=True, blank=True)
    exlentddt = models.DateField(null=True, blank=True)
    exlenttime = models.TimeField(null=True, blank=True)
    exlucdame = models.CharField(max_length=30, null=True, blank=True)
    exlameddt = models.DateField(null=True, blank=True)
    exlametime = models.TimeField(null=True, blank=True)

    exldelflg = models.CharField(max_length=1, default="", blank=True)

    class Meta:
        db_table = "exlmast"

        ordering = ["exlexhsno", "exllno"]

        constraints = [models.UniqueConstraint(fields=["exlexhsno", "exllno"], name="exlmast_exlexhsno_exllno_uniq")]
