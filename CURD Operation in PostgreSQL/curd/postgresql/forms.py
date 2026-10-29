# =============================================================================
# postgresql/forms.py - the Add / Edit User form (Users tab)
# =============================================================================
# Used by:  views.py (user_add, user_edit)
# Uses:     models.py (Usdmast)
# Shown in: templates/postgresql/users/form.html
# The form checks the typed values and saves them to the usdmast table.
# =============================================================================
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import Usdmast

# Yes/No columns. In the database they hold 'Y' or '' ; on the form they are check boxes.
# Format:  column name -> label shown on the form
YN_FIELDS = {
    "usdadmin": "Administrator",
    "usdbockpodgrnyn": "Book PO / DGRN",
    "usdbrcsalyn": "BRC sales",
    "usdlacsalyn": "LAC sales",
    "usdprnsalyn": "PRN sales",
    "usdeggsalyn": "EGG sales",
    "usdccnsalyn": "CCN sales",
    "usdpgfsalyn": "PGF sales",
    "usdcafsalyn": "CAF sales",
    "usdmaisalyn": "MAI sales",
    "usdhegsalyn": "HEG sales",
    "usdhassalyn": "HAS sales",
    "usdrepyn": "Reports",
    "usdstkrolyn": "Stock re-order level",
    "usdatfauthyn": "ATF authorise",
    "usdsohpvalyn": "SOH price value",
}

# Active flag column: 'Y' = can login, 'N' = blocked (checked in auth.py)
ACTIVE = "usdactflg"


class UserForm(forms.ModelForm):
    # Not a database column. The typed password is hashed in save() and stored in usdpwd.
    new_password = forms.CharField(
        label="Password", required=False, max_length=30,
        widget=forms.PasswordInput(render_value=False, attrs={"autocomplete": "new-password"}),
        help_text="Edit karaddi hiswa thiyanna puluwan - wenas karanne nathnam.",
    )

    class Meta:
        # The form is built from the usdmast table (models.py)
        model = Usdmast

        # Columns that appear on the form
        fields = [
            "usdusd", "usdnam", "usdemail", "usddesig", "usdcomsno", "usddepsno",
            "usdlocsno", "usduno", "usdprintername", "usdsalstkcatsnos",
            "usdatfliamt", "usdatfnosetday",
            "usdactflg", *YN_FIELDS,          # check box columns
        ]

        # Labels shown above each input
        labels = {
            "usdusd": "User code (login name)",
            "usdnam": "Name",
            "usdemail": "Email",
            "usddesig": "Designation",
            "usdcomsno": "Company no",
            "usddepsno": "Department no",
            "usdlocsno": "Location no",
            "usduno": "Unit no",
            "usdprintername": "Printer name",
            "usdsalstkcatsnos": "Sales stock category nos",
            "usdatfliamt": "ATF limit amount",
            "usdatfnosetday": "ATF no. of days",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make each Y/N column a check box, checked when the saved value is 'Y'
        for name, label in YN_FIELDS.items():
            self.fields[name] = forms.BooleanField(label=label, required=False)
            self.initial[name] = (getattr(self.instance, name, "") or "").upper() == "Y"

        # "Active" check box: ticked unless the saved value is 'N'
        self.fields[ACTIVE] = forms.BooleanField(label="Active (can login)", required=False)
        if self.instance.pk:
            # Edit: show the saved value
            self.initial[ACTIVE] = self.instance.is_active_user
        else:
            # Add: new users are active, and the password is required
            self.initial[ACTIVE] = True
            self.fields["new_password"].required = True
            self.fields["new_password"].help_text = ""

        # Bootstrap css classes
        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs["class"] = "form-check-input"
            else:
                f.widget.attrs["class"] = "form-control"

    def clean_usdusd(self):
        # Remove spaces around the user code
        return self.cleaned_data["usdusd"].strip()

    def clean(self):
        cleaned = super().clean()

        # Check box -> 'Y' or '' (the value format used in the database)
        for name in YN_FIELDS:
            cleaned[name] = "Y" if cleaned.get(name) else ""

        # Active: ticked -> 'Y', not ticked -> 'N'
        cleaned[ACTIVE] = "Y" if cleaned.get(ACTIVE) else "N"

        return cleaned

    def sections(self):
        """Groups of fields for users/form.html (title, fields, show as switches?)."""
        def bf(*names):
            # Get the form field for each column name
            return [self[n] for n in names]

        return [
            # (card title, fields, True = show as check box switches)
            ("Login",       bf("usdusd", "new_password", "usdnam", "usdemail"), False),
            ("Details",     bf("usddesig", "usdcomsno", "usddepsno", "usdlocsno", "usduno", "usdprintername"), False),
            ("Status",      bf(ACTIVE, "usdadmin"), True),
            ("Permissions", bf(
                "usdbockpodgrnyn", "usdbrcsalyn", "usdlacsalyn", "usdprnsalyn", "usdeggsalyn",
                "usdccnsalyn", "usdpgfsalyn", "usdcafsalyn", "usdmaisalyn", "usdhegsalyn",
                "usdhassalyn", "usdrepyn", "usdstkrolyn", "usdatfauthyn", "usdsohpvalyn"), True),
            ("Other",       bf("usdsalstkcatsnos", "usdatfliamt", "usdatfnosetday"), False),
        ]

    def save(self, acting_user, commit=True):
        """Save the user. acting_user = the logged-in user (used for the audit columns)."""
        obj = super().save(commit=False)

        now = timezone.localtime()

        # Logged-in user code, saved as "created by" / "updated by"
        code = acting_user.usdusd[:30]

        # New password typed -> store the hash and today's date
        pwd = self.cleaned_data.get("new_password")
        if pwd:
            obj.usdpwd = make_password(pwd)
            obj.usdpwdddt = now.date()

        if obj.pk is None:
            # New user: fill the "created" columns
            obj.usducdnew = code[:10]
            obj.usdentddt = now.date()
            obj.usdenttime = now.strftime("%H:%M:%S")

        # Always fill the "last updated" columns (shown in the Users list)
        obj.usducdame = code
        obj.usdameddt = now.date()
        obj.usdametime = now.time().replace(microsecond=0)

        if commit:
            obj.save()
        return obj
