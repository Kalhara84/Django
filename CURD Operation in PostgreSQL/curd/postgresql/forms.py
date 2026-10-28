# =============================================================================
# postgresql/forms.py  -  User management form (UserForm)
# =============================================================================
# This file defines the form used to create and edit users in the usdmast table.
#
# Key concepts:
#   - Django ModelForm: automatically creates HTML form fields from a model.
#   - YN_FIELDS: dictionary of all permission flags that are stored as 'Y'/''.
#     The form shows them as checkboxes; clean() converts True/False -> 'Y'/''.
#   - Password handling: the form has a plain-text input for a new password.
#     If the user types something, save() hashes it with make_password().
#     If left blank (editing existing user), the old password is kept.
#   - sections(): helper that groups fields into labelled sections for the
#     HTML template (postgresql/templates/postgresql/users/form.html).
#   - save(acting_user): fills in the audit-trail columns (who created/updated
#     and when) before saving to the database.
#
# Connections:
#   - models.py   -> Usdmast (the model this form wraps)
#   - views.py    -> user_add() and user_edit() use this form
# =============================================================================

from django import forms                                   # Django form classes
from django.contrib.auth.hashers import make_password      # hash a plain-text password
from django.utils import timezone                          # timezone-aware datetime

# Usdmast is the user table defined in models.py.
from .models import Usdmast

# ---------------------------------------------------------------------------
# YN_FIELDS  -  permission flags that appear as checkboxes in the form
# ---------------------------------------------------------------------------
# Keys   = Usdmast field names (the DB columns)
# Values = Human-readable labels shown next to each checkbox in the HTML form
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

# Name of the "Active" flag field (handled separately from YN_FIELDS because
# its values are 'Y'/'N' instead of 'Y'/'').
ACTIVE = "usdactflg"


# ---------------------------------------------------------------------------
# UserForm  -  create / edit a Usdmast (user) row
# ---------------------------------------------------------------------------
class UserForm(forms.ModelForm):
    """
    Form for creating and editing user accounts.

    Extra field (not on the model):
      new_password  -  optional plain-text password input.
                       If filled in, save() hashes it and stores it in usdpwd.
                       If left blank on edit, the existing password is kept.
    """

    # Extra field not in the Usdmast model - collects a new plain-text password.
    # render_value=False means the current value is never pre-filled in the
    # browser (good practice; passwords should not be echoed back).
    new_password = forms.CharField(
        label="Password", required=False, max_length=30,
        widget=forms.PasswordInput(render_value=False, attrs={"autocomplete": "new-password"}),
        help_text="Edit karaddi hiswa thiyanna puluwan - wenas karanne nathnam.",
    )

    class Meta:
        # Which model this form is based on.
        model = Usdmast

        # The model fields to include.  *YN_FIELDS unpacks all the permission
        # flag names so we do not have to list them one by one.
        fields = [
            "usdusd", "usdnam", "usdemail", "usddesig", "usdcomsno", "usddepsno",
            "usdlocsno", "usduno", "usdprintername", "usdsalstkcatsnos",
            "usdatfliamt", "usdatfnosetday",
            "usdactflg", *YN_FIELDS,          # checkbox flags (Y / blank)
        ]

        # Override the default labels Django generates from field names.
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
        Customise the form after it is built:
          1. Replace all YN_FIELDS text inputs with BooleanField checkboxes.
          2. Set initial checkbox values by reading 'Y' from the model instance.
          3. Handle the Active flag separately (its off-value is 'N', not '').
          4. Make password required when creating a new user (no instance yet).
          5. Add Bootstrap CSS classes to all widgets.
        """
        super().__init__(*args, **kwargs)

        # Step 1 & 2: Convert each Y/N permission column to a checkbox.
        for name, label in YN_FIELDS.items():
            self.fields[name] = forms.BooleanField(label=label, required=False)
            # Pre-tick the checkbox if the current value in the DB is 'Y'.
            self.initial[name] = (getattr(self.instance, name, "") or "").upper() == "Y"

        # Step 3: The Active flag checkbox (usdactflg).
        self.fields[ACTIVE] = forms.BooleanField(label="Active (can login)", required=False)
        if self.instance.pk:
            # Editing an existing user: tick if account is active.
            self.initial[ACTIVE] = self.instance.is_active_user
        else:
            # Creating a new user: default to Active = True.
            self.initial[ACTIVE] = True
            # Password is mandatory when creating a new user.
            self.fields["new_password"].required = True
            self.fields["new_password"].help_text = ""

        # Step 5: Add Bootstrap CSS classes so widgets look correct with Bootstrap.
        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs["class"] = "form-check-input"   # Bootstrap checkbox style
            else:
                f.widget.attrs["class"] = "form-control"       # Bootstrap text-input style

    def clean_usdusd(self):
        """Remove leading/trailing whitespace from the user code before saving."""
        return self.cleaned_data["usdusd"].strip()

    def clean(self):
        """
        Convert checkbox True/False values back to 'Y'/'N'/'' strings
        so they match what the database columns expect.
        """
        cleaned = super().clean()

        # Permission flags: True -> 'Y', False -> '' (blank = no permission)
        for name in YN_FIELDS:
            cleaned[name] = "Y" if cleaned.get(name) else ""

        # Active flag: True -> 'Y', False -> 'N' (explicitly disabled)
        cleaned[ACTIVE] = "Y" if cleaned.get(ACTIVE) else "N"

        return cleaned

    def sections(self):
        """
        Group form fields into named sections for the HTML template.

        Returns a list of tuples:
            (section_title, [BoundField, ...], is_checkbox_section)

        The template (users/form.html) loops over sections() to render each
        group in its own card / fieldset with the right Bootstrap layout.
        """
        def bf(*names):
            # Return a list of BoundField objects for the named fields.
            # BoundField knows its value, label, errors, and how to render itself.
            return [self[n] for n in names]

        return [
            # (title,  fields list,  True=checkbox layout / False=text layout)
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
        """
        Save the user to the database, filling in audit trail columns.

        Parameters:
            acting_user  - the currently logged-in Usdmast object (request.usd).
                           Their user code is written to the 'updated by' columns.
            commit       - if True (default), save to the DB immediately.
                           If False, return the unsaved object (useful for testing).

        Steps:
          1. Call the parent save(commit=False) to get the model instance without
             hitting the database yet (so we can set extra fields first).
          2. Hash the new password if the user typed one.
          3. Set the 'created by' columns on new users, 'updated by' on all.
          4. Save to the database.
        """
        # Get the model instance with form data applied, but not yet saved to DB.
        obj = super().save(commit=False)

        # Current timestamp for the audit trail.
        now = timezone.localtime()

        # The user code of whoever is performing this action (max 30 chars).
        code = acting_user.usdusd[:30]

        # If a new password was typed, hash it before saving.
        pwd = self.cleaned_data.get("new_password")
        if pwd:
            obj.usdpwd = make_password(pwd)         # convert plain text to secure hash
            obj.usdpwdddt = now.date()              # record the date the password changed

        if obj.pk is None:
            # This is a brand new user (no primary key yet).
            # Fill in the 'created by' audit columns.
            obj.usducdnew = code[:10]               # max 10 chars for this column
            obj.usdentddt = now.date()              # today's date
            obj.usdenttime = now.strftime("%H:%M:%S")  # current time as string

        # Always fill in the 'last updated by' audit columns (for both new and edit).
        obj.usducdame = code                        # who did this action
        obj.usdameddt = now.date()                  # today's date
        obj.usdametime = now.time().replace(microsecond=0)  # current time (no microseconds)

        if commit:
            obj.save()  # write the row to the PostgreSQL database
        return obj
