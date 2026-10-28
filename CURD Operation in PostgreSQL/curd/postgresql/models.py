"""
Database Models for 'postgresql' app.

Role of this file:
- Defines the data structure (schema) for the PostgreSQL database using Django ORM.
- The 'Usdmast' model maps directly to the 'usdmast' table in PostgreSQL.
- It is used by:
  1. forms.py (for user creation/editing validation)
  2. auth.py (to query user credentials during login)
  3. views.py (to perform CRUD operations - Create, Read, Update, Delete)
  4. decorators.py (to verify active session user)
"""

from django.db import models


def yn():
    """
    Helper function to define a 1-character field for 'Yes' ('Y') or blank ('') flags.
    Matches legacy database convention where checkboxes are stored as 'Y' or empty string.
    """
    return models.CharField(max_length=1, blank=True, default="")


class Usdmast(models.Model):
    """
    User Master Model (Usdmast):
    Represents the staff/user records in the jewellery system.
    """
    # Primary Key: Auto-incrementing unique ID number for each user
    usdsno = models.AutoField(primary_key=True)

    # Authentication & Basic Profile Fields:
    usdusd = models.CharField(max_length=30)                          # User login username / code
    usdcomsno = models.IntegerField(default=0)                       # Company ID number (multi-company support)
    usdnam = models.CharField(max_length=50, null=True, blank=True)   # User's full display name
    usdpwd = models.CharField(max_length=128, null=True, blank=True) # Password (hashed or plain legacy)
    usddesig = models.CharField(max_length=25, blank=True, default="")# Job title / Designation (e.g. Cashier, Manager)
    usddepsno = models.IntegerField(default=0)                       # Department ID number
    usdlocsno = models.IntegerField(default=0)                       # Branch / Location ID number
    usduno = models.CharField(max_length=4, blank=True, default="")   # Unit number code
    usdemail = models.CharField(max_length=40, blank=True, default="")# User's email address

    # Status & System Roles:
    usdadmin = yn()                                                  # 'Y' = Admin privileges, '' = Regular staff
    usdactflg = yn()                                                 # 'Y' or '' = Active user, 'N' = Inactive / Blocked

    # Module Permissions (Flags: 'Y' allows access, '' denies access):
    usdbockpodgrnyn = yn()                                           # Permission: Book Purchase Orders / DGRN
    usdbrcsalyn = yn()                                               # Permission: BRC category sales
    usdlacsalyn = yn()                                               # Permission: LAC category sales
    usdprnsalyn = yn()                                               # Permission: PRN category sales
    usdeggsalyn = yn()                                               # Permission: EGG category sales
    usdccnsalyn = yn()                                               # Permission: CCN category sales
    usdpgfsalyn = yn()                                               # Permission: PGF category sales
    usdcafsalyn = yn()                                               # Permission: CAF category sales
    usdmaisalyn = yn()                                               # Permission: MAI category sales
    usdhegsalyn = yn()                                               # Permission: HEG category sales
    usdhassalyn = yn()                                               # Permission: HAS category sales
    usdrepyn = yn()                                                  # Permission: View and export reports
    usdstkrolyn = yn()                                               # Permission: Manage stock re-order levels
    usdatfauthyn = yn()                                              # Permission: Authorize ATF (After Trade Finance)
    usdsohpvalyn = yn()                                              # Permission: View stock-on-hand (SOH) price values

    # Extended Settings & Limits:
    usdsalstkcatsnos = models.CharField(max_length=100, blank=True, default="") # Allowed stock category IDs
    usdprintername = models.CharField(max_length=30, blank=True, default="")    # Default receipt/barcode printer
    usdatfliamt = models.IntegerField(default=0)                                 # ATF limit amount allowed
    usdatfnosetday = models.IntegerField(default=0)                              # ATF allowed number of settlement days
    usdpwdddt = models.DateField(null=True, blank=True)                          # Date password was last changed

    # Audit Trail (Creation & Last Modification tracking):
    usducdnew = models.CharField(max_length=10, blank=True, default="")          # Username of who created this record
    usdentddt = models.DateField(null=True, blank=True)                          # Date created
    usdenttime = models.CharField(max_length=12, blank=True, default="")         # Time created
    usducdame = models.CharField(max_length=30, null=True, blank=True)           # Username of who last amended/updated
    usdameddt = models.DateField(null=True, blank=True)                          # Date of last amendment
    usdametime = models.TimeField(null=True, blank=True)                         # Time of last amendment

    class Meta:
        db_table = "usdmast"                                         # Direct mapping to PostgreSQL table 'usdmast'
        ordering = ["usdsno"]                                        # Default ordering by primary key ascending
        constraints = [
            # Ensures username (usdusd) is unique per company (usdcomsno)
            models.UniqueConstraint(fields=["usdusd", "usdcomsno"], name="usdmast_usdusd_usdcomsno_uniq"),
        ]

    def __str__(self):
        """String representation of the user model (e.g. 'admin - John Doe')."""
        return f"{self.usdusd} - {self.usdnam or ''}"

    @property
    def is_admin(self):
        """Returns True if user has Admin flag set to 'Y'."""
        return (self.usdadmin or "").upper() == "Y"

    @property
    def is_active_user(self):
        """Returns True if user is not blocked ('N' means blocked)."""
        return (self.usdactflg or "").upper() != "N"

