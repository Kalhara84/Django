# =============================================================================
# postgresql/models.py  -  Database table definitions (ORM models)
# =============================================================================
# Each class here represents one table in the PostgreSQL database.
# Django's ORM (Object Relational Mapper) uses these classes to:
#   - Create / alter the database tables via migrations
#   - Let Python code query and save data without writing raw SQL
#
# Tables defined in this file:
#   Usdmast   -> usdmast      User master (login accounts)
#   Excmast   -> excmast      Item category lookup
#   Exlocmast -> exlocmast    Location lookup
#   Exsmast   -> exsmast      Service category lookup
#   Expmast   -> expmast      Period / duration lookup
#   GGenmast  -> g_genmast    General ledger / account master
#   Exhmast   -> exhmast      Expire entry HEADER (one row per document)
#   Exlmast   -> exlmast      Expire entry LINES  (many rows per header)
#
# Connections:
#   - auth.py         queries Usdmast for login
#   - decorators.py   loads Usdmast from session to check login/admin status
#   - forms.py        builds UserForm from Usdmast
#   - expire_forms.py uses Excmast, Exlocmast, Exsmast, Expmast, GGenmast
#                     to populate dropdowns; saves Exhmast + Exlmast rows
#   - views.py        queries Usdmast for CRUD
#   - expire_views.py queries all the expire-related models
# =============================================================================

from django.db import models  # base class and field types for all models


# ---------------------------------------------------------------------------
# Helper: re-usable single-character Y/N flag field
# ---------------------------------------------------------------------------
def yn():
    """
    Return a CharField(max_length=1) used for yes/no flags throughout the
    project.  Stored as 'Y', 'N', or '' (blank = not set).
    Defined once here to avoid repeating the same arguments many times.
    """
    return models.CharField(max_length=1, blank=True, default="")


# ---------------------------------------------------------------------------
# Usdmast  ->  database table: usdmast
# ---------------------------------------------------------------------------
class Usdmast(models.Model):
    """
    User master table.  Each row is one login account.

    Used by:
      auth.py       - authenticate_usdmast() looks up users here
      decorators.py - _load_user() reloads the user on every request
      views.py      - user CRUD (list / add / edit / delete)
      forms.py      - UserForm is built from this model
    """

    # Primary key - auto-incrementing integer. Django creates the DB column automatically.
    usdsno = models.AutoField(primary_key=True)

    # The user's login code (username), e.g. "JOHN".  Up to 30 characters.
    usdusd = models.CharField(max_length=30)

    # Company number this user belongs to.  0 = no specific company.
    usdcomsno = models.IntegerField(default=0)

    # Full name of the user, e.g. "John Smith".  Optional (nullable).
    usdnam = models.CharField(max_length=50, null=True, blank=True)

    # Hashed password (Django PBKDF2 hash) or legacy plain text.
    # auth.py -> verify_password() handles both formats.
    # Max 128 chars is enough for any Django hash string.
    usdpwd = models.CharField(max_length=128, null=True, blank=True)

    # Job title / designation, e.g. "Manager".
    usddesig = models.CharField(max_length=25, blank=True, default="")

    # Department number the user is assigned to.
    usddepsno = models.IntegerField(default=0)

    # Location number the user is assigned to.
    usdlocsno = models.IntegerField(default=0)

    # Short unit code for the user, e.g. "A1".
    usduno = models.CharField(max_length=4, blank=True, default="")

    # Email address of the user (optional).
    usdemail = models.CharField(max_length=40, blank=True, default="")

    # 'Y' = this user is an administrator, '' = regular user.
    # is_admin property (below) reads this field.
    usdadmin = yn()

    # 'N' = account is disabled; anything else = active.
    # is_active_user property (below) reads this field.
    # decorators.py excludes rows where this is 'N' when logging in.
    usdactflg = yn()

    # --- Permission flags (Y = allowed, '' = not allowed) ---
    # Each flag controls access to a specific area of the system.
    usdbockpodgrnyn = yn()   # Allow booking PO / DGRN
    usdbrcsalyn = yn()       # Allow BRC sales
    usdlacsalyn = yn()       # Allow LAC sales
    usdprnsalyn = yn()       # Allow PRN sales
    usdeggsalyn = yn()       # Allow EGG sales
    usdccnsalyn = yn()       # Allow CCN sales
    usdpgfsalyn = yn()       # Allow PGF sales
    usdcafsalyn = yn()       # Allow CAF sales
    usdmaisalyn = yn()       # Allow MAI sales
    usdhegsalyn = yn()       # Allow HEG sales
    usdhassalyn = yn()       # Allow HAS sales
    usdsalstkcatsnos = models.CharField(max_length=100, blank=True, default="")  # Sales stock category numbers
    usdrepyn = yn()          # Allow access to reports
    usdstkrolyn = yn()       # Allow stock re-order level access

    # Printer name assigned to this user (used for auto-printing).
    usdprintername = models.CharField(max_length=30, blank=True, default="")

    # ATF (Advance Transfer Form) permissions.
    usdatfauthyn = yn()            # Can authorise ATF
    usdatfliamt = models.IntegerField(default=0)     # ATF authorisation limit amount
    usdatfnosetday = models.IntegerField(default=0)  # ATF number of days allowed

    # Date the password was last changed.
    usdpwdddt = models.DateField(null=True, blank=True)

    # SOH (Stock on Hand) price value permission.
    usdsohpvalyn = yn()

    # Audit trail: who created this row and when.
    usducdnew = models.CharField(max_length=10, blank=True, default="")   # created by (user code, max 10)
    usdentddt = models.DateField(null=True, blank=True)                    # created date
    usdenttime = models.CharField(max_length=12, blank=True, default="")  # created time (stored as "HH:MM:SS")

    # Audit trail: who last updated this row and when.
    usducdame = models.CharField(max_length=30, null=True, blank=True)    # last updated by (user code)
    usdameddt = models.DateField(null=True, blank=True)                   # last updated date
    usdametime = models.TimeField(null=True, blank=True)                  # last updated time

    class Meta:
        # The actual PostgreSQL table name.  Without this, Django would use
        # "postgresql_usdmast" (app_model convention).
        db_table = "usdmast"

        # Default ordering when you do Usdmast.objects.all() - sorted by primary key.
        ordering = ["usdsno"]

        # Database-level uniqueness: the same user code cannot appear twice
        # for the same company number.
        constraints = [
            models.UniqueConstraint(fields=["usdusd", "usdcomsno"], name="usdmast_usdusd_usdcomsno_uniq"),
        ]

    def __str__(self):
        """Human-readable representation used in Django admin and debug output."""
        return f"{self.usdusd} - {self.usdnam or ''}"

    @property
    def is_admin(self):
        """True if this user is an administrator (usdadmin = 'Y')."""
        # Used by decorators.py -> admin_required to protect admin-only views.
        return (self.usdadmin or "").upper() == "Y"

    @property
    def is_active_user(self):
        """True if this user's account is active (usdactflg != 'N')."""
        # Used by decorators.py -> _load_user to reject disabled accounts.
        return (self.usdactflg or "").upper() != "N"


# ---------------------------------------------------------------------------
# Excmast  ->  database table: excmast
# ---------------------------------------------------------------------------
class Excmast(models.Model):
    """
    Item category lookup table.
    Each row is a category that an expire entry (Exhmast) belongs to.

    Used by:
      expire_forms.py -> lookup_choices() populates the Category dropdown
      expire_views.py -> expire_list() displays the category name in the list
    """
    # Primary key - auto-incrementing.
    excsno = models.AutoField(primary_key=True)

    # Short code for the category, e.g. "ELEC".  Must be unique.
    excexc = models.CharField(max_length=40, default="")

    # Full name / description of the category, e.g. "Electronics".
    excnam = models.CharField(max_length=40, default="")

    # Audit trail fields (who created/updated this row and when).
    excusdsno = models.IntegerField(null=True, blank=True)           # user sno who created
    excucdnew = models.CharField(max_length=30, null=True, blank=True)  # created by user code
    excentddt = models.DateField(null=True, blank=True)              # created date
    excenttime = models.TimeField(null=True, blank=True)             # created time
    excucdame = models.CharField(max_length=30, null=True, blank=True)  # last updated by
    excameddt = models.DateField(null=True, blank=True)              # last updated date
    excametime = models.TimeField(null=True, blank=True)             # last updated time

    class Meta:
        db_table = "excmast"        # actual table name in PostgreSQL
        ordering = ["excexc"]       # alphabetical by category code
        constraints = [models.UniqueConstraint(fields=["excexc"], name="excmast_excexc_uniq")]

    def __str__(self):
        return f"{self.excexc} - {self.excnam}"


# ---------------------------------------------------------------------------
# Exlocmast  ->  database table: exlocmast
# ---------------------------------------------------------------------------
class Exlocmast(models.Model):
    """
    Location lookup table.
    Each row is a physical location (warehouse, branch, etc.).

    Used by:
      expire_forms.py -> lookup_choices() populates the Location dropdown
      expire_views.py -> expire_list() displays the location name in the list
    """
    exlocsno = models.AutoField(primary_key=True)   # auto primary key

    # Short location code, e.g. "WH01".  Must be unique.
    exlocloc = models.CharField(max_length=40, default="")

    # Full location name, e.g. "Main Warehouse".
    exlocnam = models.CharField(max_length=40, default="")

    # Audit trail fields.
    exlocucdnew = models.CharField(max_length=30, null=True, blank=True)  # created by
    exlocentddt = models.DateField(null=True, blank=True)                  # created date
    exlocenttime = models.TimeField(null=True, blank=True)                 # created time
    exlocucdame = models.CharField(max_length=30, null=True, blank=True)  # last updated by
    exlocameddt = models.DateField(null=True, blank=True)                  # last updated date
    exlocametime = models.TimeField(null=True, blank=True)                 # last updated time

    class Meta:
        db_table = "exlocmast"
        ordering = ["exlocloc"]
        constraints = [models.UniqueConstraint(fields=["exlocloc"], name="exlocmast_exlocloc_uniq")]

    def __str__(self):
        return f"{self.exlocloc} - {self.exlocnam}"


# ---------------------------------------------------------------------------
# Exsmast  ->  database table: exsmast
# ---------------------------------------------------------------------------
class Exsmast(models.Model):
    """
    Service category lookup table.
    Each row is a type of service that can appear on an expire line (Exlmast).

    Used by:
      expire_forms.py -> lookup_choices() populates the Service Category dropdown
    """
    exssno = models.AutoField(primary_key=True)  # auto primary key

    # Short service code, e.g. "MAINT".  Must be unique.
    exsexs = models.CharField(max_length=40, default="")

    # Full service name, e.g. "Maintenance".
    exsnam = models.CharField(max_length=40, default="")

    # Audit trail fields.
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


# ---------------------------------------------------------------------------
# Expmast  ->  database table: expmast
# ---------------------------------------------------------------------------
class Expmast(models.Model):
    """
    Period / duration lookup table.
    Each row represents a time period, e.g. "ANNUAL" = 365 days.

    Used by:
      expire_forms.py -> lookup_choices() populates the Period dropdown
    """
    expsno = models.AutoField(primary_key=True)  # auto primary key

    # Short period code, e.g. "ANNUAL".  Must be unique.
    expexp = models.CharField(max_length=40, default="")

    # Number of days this period represents.  Optional (some periods may not
    # have a fixed day count).
    expdays = models.IntegerField(null=True, blank=True)

    # Audit trail fields.
    expucdnew = models.CharField(max_length=30, null=True, blank=True)
    expentddt = models.DateField(null=True, blank=True)
    expenttime = models.TimeField(null=True, blank=True)
    expucdame = models.CharField(max_length=30, null=True, blank=True)
    expameddt = models.DateField(null=True, blank=True)
    expametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "expmast"
        # Sort by number of days first (shortest periods first), then alphabetically.
        ordering = ["expdays", "expexp"]
        constraints = [models.UniqueConstraint(fields=["expexp"], name="expmast_expexp_uniq")]

    def __str__(self):
        return f"{self.expexp} ({self.expdays} days)"


# ---------------------------------------------------------------------------
# GGenmast  ->  database table: g_genmast
# ---------------------------------------------------------------------------
class GGenmast(models.Model):
    """
    General ledger / account master table.
    Each row is a chart-of-accounts entry (control account + sub-account).

    Used by:
      expire_forms.py -> lookup_choices() populates the Account Code dropdown
      Exlmast links to this table via exlgensno -> gensno
    """
    gensno = models.AutoField(primary_key=True)  # auto primary key

    # Control account code (main account), e.g. "1000".
    genctl = models.CharField(max_length=8)

    # Sub-account code, e.g. "01".  Blank for top-level accounts.
    gensub = models.CharField(max_length=4, default="", blank=True)

    # Combined control+sub code for quick reference.
    genctlsub = models.CharField(max_length=8, default="", blank=True)

    # Debit/Credit interest flags (Y/N single chars).
    gendebint = models.CharField(max_length=1, default="", blank=True)
    gencrdint = models.CharField(max_length=1, default="", blank=True)

    # Description / name of the account (primary and secondary).
    gendes = models.CharField(max_length=60, null=True, blank=True)
    gendes1 = models.CharField(max_length=30, default="", blank=True)

    # External mapping code (used to link to other systems).
    genmapcode = models.CharField(max_length=15, null=True, blank=True)

    # Single-character account type code.
    gencde = models.CharField(max_length=1, null=True, blank=True)

    # Company, location, and various categorisation foreign keys (stored as
    # plain integers rather than ForeignKey relations for compatibility with
    # the legacy database structure).
    gencomsno = models.IntegerField(default=0)     # company number
    genlocsno = models.IntegerField(default=0)     # location number
    gencatsno = models.IntegerField(null=True, blank=True)  # category number
    genaansno = models.IntegerField(null=True, blank=True)
    gencursno = models.IntegerField(default=0)     # currency number
    genjobsno = models.IntegerField(default=0)     # job number
    genempsno = models.IntegerField(default=0)     # employee number
    gengrpsno = models.IntegerField(default=0)     # group number
    genectsno = models.IntegerField(default=0)

    # Y/N flags indicating which sub-ledger dimensions apply to this account.
    gensupyn = models.CharField(max_length=1, null=True, blank=True)   # supplier
    genjobyn = models.CharField(max_length=1, null=True, blank=True)   # job
    gendepyn = models.CharField(max_length=1, default="", blank=True)  # department
    genempyn = models.CharField(max_length=1, default="", blank=True)  # employee
    gencusyn = models.CharField(max_length=1, default="", blank=True)  # customer
    genictyn = models.CharField(max_length=1, default="", blank=True)  # ICT
    genadvyn = models.CharField(max_length=1, default="", blank=True)  # advance
    genappyn = models.CharField(max_length=1, default="", blank=True)  # approval
    gencamyn = models.CharField(max_length=1, default="", blank=True)  # camera / asset
    genvehyn = models.CharField(max_length=1, default="", blank=True)  # vehicle
    genlocyn = models.CharField(max_length=1, default="", blank=True)  # location flag

    # Exchange rate applicable to this account.
    genrate = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Bank-related fields.
    genbnkprefix = models.CharField(max_length=5, default="", blank=True)   # bank prefix code
    genoticrdacc = models.CharField(max_length=12, default="", blank=True)  # OTI credit account

    # Audit trail fields.
    genucdnew = models.CharField(max_length=30, null=True, blank=True)
    genentddt = models.DateField(null=True, blank=True)
    genenttime = models.TimeField(null=True, blank=True)
    genucdame = models.CharField(max_length=30, null=True, blank=True)
    genameddt = models.DateField(null=True, blank=True)
    genametime = models.TimeField(null=True, blank=True)

    # Temporary flag (used during data import/migration).
    gentemp = models.CharField(max_length=1, default="", blank=True)

    class Meta:
        db_table = "g_genmast"          # actual table name (note the "g_" prefix)
        ordering = ["genctl", "gensub"] # sorted by control code, then sub-code
        # The combination of control + sub must be unique (no duplicate accounts).
        constraints = [models.UniqueConstraint(fields=["genctl", "gensub"], name="g_genmast_genctl_gensub_uniq")]

    def __str__(self):
        return f"{self.genctl}-{self.gensub} {self.gendes or ''}"


# ---------------------------------------------------------------------------
# Exhmast  ->  database table: exhmast  (Expire HEADER)
# ---------------------------------------------------------------------------
class Exhmast(models.Model):
    """
    Expire entry HEADER table.
    One row = one expire document (like the top part of an invoice).

    Child rows (the detail lines) live in Exlmast and link back here via
    Exlmast.exlexhsno = Exhmast.exhsno.

    Used by:
      expire_views.py -> expire_list(), expire_add(), expire_edit(), expire_delete()
      expire_forms.py -> HeaderForm saves/updates rows here
    """
    exhsno = models.AutoField(primary_key=True)  # auto primary key

    # Unique document code, e.g. "EXP-2026-001".  The user enters this manually.
    exhdno = models.CharField(max_length=30, unique=True)

    # Foreign key (as plain integer) -> excmast.excsno  (item category)
    exhexcsno = models.IntegerField()

    # Foreign key (as plain integer) -> exlocmast.exlocsno  (location)
    exhexlocsno = models.IntegerField()

    # Document date.
    exhddt = models.DateField()

    # Short description of the expire entry.
    exhdes = models.CharField(max_length=50)

    # Audit trail fields.
    exhucdnew = models.CharField(max_length=30, null=True, blank=True)   # created by
    exhentddt = models.DateField(null=True, blank=True)                   # created date
    exhenttime = models.TimeField(null=True, blank=True)                  # created time
    exhucdame = models.CharField(max_length=30, null=True, blank=True)   # last updated by
    exhameddt = models.DateField(null=True, blank=True)                   # last updated date
    exhametime = models.TimeField(null=True, blank=True)                  # last updated time

    class Meta:
        db_table = "exhmast"
        # Most recent entries appear first (negative = descending sort).
        ordering = ["-exhsno"]

    def __str__(self):
        return self.exhdno


# ---------------------------------------------------------------------------
# Exlmast  ->  database table: exlmast  (Expire LINES)
# ---------------------------------------------------------------------------
class Exlmast(models.Model):
    """
    Expire entry LINES table.
    Each row is one detail line belonging to an Exhmast header.

    Relationship:
      Exlmast.exlexhsno  ->  Exhmast.exhsno   (many lines belong to one header)
      Exlmast.exllno     =   line number within that header (1, 2, 3, ...)

    Foreign key references (stored as plain integers):
      exlexssno -> exsmast.exssno     (service category)
      exlexpsno -> expmast.expsno     (period/duration)
      exlgensno -> g_genmast.gensno   (account code)

    Used by:
      expire_views.py -> _save() creates/updates/deletes lines
      expire_forms.py -> LineForm / LineFormSet collects line data
    """
    exlsno = models.AutoField(primary_key=True)  # auto primary key

    # Link to the parent header row in exhmast.
    exlexhsno = models.IntegerField(default=0)

    # Line sequence number within this header (1, 2, 3, ...).
    exllno = models.IntegerField(default=0)

    # Foreign keys stored as integers (no Django ForeignKey for legacy compatibility).
    exlexssno = models.IntegerField()   # -> exsmast.exssno  (service category)
    exlexpsno = models.IntegerField()   # -> expmast.expsno  (period/duration)
    exlgensno = models.IntegerField()   # -> g_genmast.gensno (account code)

    # Dates for this line item.
    exlcomplddt = models.DateField(null=True, blank=True)    # completion date
    exlcutoffddt = models.DateField(null=True, blank=True)   # cutoff date

    # Audit trail fields.
    exlucdnew = models.CharField(max_length=30, null=True, blank=True)   # created by
    exlentddt = models.DateField(null=True, blank=True)                   # created date
    exlenttime = models.TimeField(null=True, blank=True)                  # created time
    exlucdame = models.CharField(max_length=30, null=True, blank=True)   # last updated by
    exlameddt = models.DateField(null=True, blank=True)                   # last updated date
    exlametime = models.TimeField(null=True, blank=True)                  # last updated time

    # Soft-delete flag: 'D' = deleted, '' = active.
    # (expire_views.py currently uses hard delete, but this flag exists for
    #  future use if soft-delete is needed.)
    exldelflg = models.CharField(max_length=1, default="", blank=True)

    class Meta:
        db_table = "exlmast"
        # Sort lines in the order they were added (header first, then by line number).
        ordering = ["exlexhsno", "exllno"]
        # A header cannot have two lines with the same line number.
        constraints = [models.UniqueConstraint(fields=["exlexhsno", "exllno"], name="exlmast_exlexhsno_exllno_uniq")]
