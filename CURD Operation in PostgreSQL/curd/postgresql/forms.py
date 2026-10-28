"""
Django Forms for 'postgresql' app.

Role of this file:
- Handles user input validation, HTML widget rendering, and database saving.
- Connects to:
  1. models.py (uses Usdmast model)
  2. views.py (instantiated in user_add and user_edit views)
  3. templates/postgresql/users/form.html (rendered section by section in the UI)
"""

from django import forms
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import Usdmast

# Dictionary of permission flags stored as 'Y' (yes/enabled) or '' (empty/disabled)
# Maps field names to human-readable form labels for checkboxes
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
# Field name that controls if user account is active ('Y') or blocked ('N')
ACTIVE = "usdactflg"


class UserForm(forms.ModelForm):
    """
    Form for adding and editing Usdmast records.
    Provides validation, password hashing, and audit column population.
    """
    # Custom password field (not directly bound to Usdmast.usdpwd text field for security)
    new_password = forms.CharField(
        label="Password",
        required=False,
        max_length=30,
        widget=forms.PasswordInput(render_value=False, attrs={"autocomplete": "new-password"}),
        help_text="Leave blank when editing if you do not want to change the password.",
    )

    class Meta:
        model = Usdmast
        # Fields from the model that should be present in this form
        fields = [
            "usdusd", "usdnam", "usdemail", "usddesig", "usdcomsno", "usddepsno",
            "usdlocsno", "usduno", "usdprintername", "usdsalstkcatsnos",
            "usdatfliamt", "usdatfnosetday",
            "usdactflg", *YN_FIELDS,          # Checkbox flags ('Y' / blank)
        ]
        # User-friendly labels for fields displayed in HTML forms
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
        """
        Customizes form initialization:
        - Converts database 'Y'/'' flag values into standard HTML boolean checkboxes.
        - Sets active status flag (defaults to True for newly added users).
        - Makes password required when creating a new user, optional when editing.
        - Attaches Bootstrap CSS classes ('form-control' or 'form-check-input') for styling.
        """
        super().__init__(*args, **kwargs)

        # Convert each Y/N flag into a BooleanField checkbox
        for name, label in YN_FIELDS.items():
            self.fields[name] = forms.BooleanField(label=label, required=False)
            self.initial[name] = (getattr(self.instance, name, "") or "").upper() == "Y"

        # Active flag checkbox
        self.fields[ACTIVE] = forms.BooleanField(label="Active (can login)", required=False)
        if self.instance.pk:
            # Editing existing user: set initial checked state from current status
            self.initial[ACTIVE] = self.instance.is_active_user
        else:
            # New user creation: default active to True, and password is required
            self.initial[ACTIVE] = True
            self.fields["new_password"].required = True
            self.fields["new_password"].help_text = ""

        # Apply Bootstrap styling classes to all input elements
        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs["class"] = "form-check-input"
            else:
                f.widget.attrs["class"] = "form-control"

    def clean_usdusd(self):
        """Validates and trims whitespace from user login code."""
        return self.cleaned_data["usdusd"].strip()

    def clean(self):
        """
        Converts boolean checkbox values back to database character formats:
        - Checked checkboxes -> 'Y'
        - Unchecked checkboxes -> '' (or 'N' for active status)
        """
        cleaned = super().clean()
        for name in YN_FIELDS:
            cleaned[name] = "Y" if cleaned.get(name) else ""
        cleaned[ACTIVE] = "Y" if cleaned.get(ACTIVE) else "N"
        return cleaned

    # ---- Layout Helper for the Template ----
    def sections(self):
        """
        Groups form fields into organized visual sections for clean display in form.html:
        Returns tuples of: (Section_Title, [BoundFields], is_checkbox_group)
        """
        def bf(*names):
            return [self[n] for n in names]
        return [
            ("Login Information", bf("usdusd", "new_password", "usdnam", "usdemail"), False),
            ("User Details", bf("usddesig", "usdcomsno", "usddepsno", "usdlocsno", "usduno", "usdprintername"), False),
            ("Account Status", bf(ACTIVE, "usdadmin"), True),
            ("Module Permissions", bf(
                "usdbockpodgrnyn", "usdbrcsalyn", "usdlacsalyn", "usdprnsalyn", "usdeggsalyn",
                "usdccnsalyn", "usdpgfsalyn", "usdcafsalyn", "usdmaisalyn", "usdhegsalyn",
                "usdhassalyn", "usdrepyn", "usdstkrolyn", "usdatfauthyn", "usdsohpvalyn"), True),
            ("Limits & Categories", bf("usdsalstkcatsnos", "usdatfliamt", "usdatfnosetday"), False),
        ]

    def save(self, acting_user, commit=True):
        """
        Saves the user to PostgreSQL database:
        - acting_user: The currently logged-in administrator (Usdmast instance).
        - Hashes new password if provided.
        - Updates audit trail columns:
          * If creating new user: fills usducdnew (creator), usdentddt (date), usdenttime (time).
          * Always fills usducdame (amended by), usdameddt (amended date), usdametime (amended time).
        """
        obj = super().save(commit=False)
        now = timezone.localtime()
        code = acting_user.usdusd[:30]

        # Hash and save password if supplied
        pwd = self.cleaned_data.get("new_password")
        if pwd:
            obj.usdpwd = make_password(pwd)
            obj.usdpwdddt = now.date()

        # Audit creation fields (only on initial insert)
        if obj.pk is None:
            obj.usducdnew = code[:10]
            obj.usdentddt = now.date()
            obj.usdenttime = now.strftime("%H:%M:%S")

        # Audit modification fields (on every edit/save)
        obj.usducdame = code
        obj.usdameddt = now.date()
        obj.usdametime = now.time().replace(microsecond=0)

        if commit:
            obj.save()
        return obj

