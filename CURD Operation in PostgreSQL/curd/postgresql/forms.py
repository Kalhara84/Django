from django import forms
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import Usdmast

# Y / blank checkbox flags
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
ACTIVE = "usdactflg"


class UserForm(forms.ModelForm):
    new_password = forms.CharField(
        label="Password", required=False, max_length=30,
        widget=forms.PasswordInput(render_value=False, attrs={"autocomplete": "new-password"}),
        help_text="Edit karaddi hiswa thiyanna puluwan - wenas karanne nathnam.",
    )

    class Meta:
        model = Usdmast
        fields = [
            "usdusd", "usdnam", "usdemail", "usddesig", "usdcomsno", "usddepsno",
            "usdlocsno", "usduno", "usdprintername", "usdsalstkcatsnos",
            "usdatfliamt", "usdatfnosetday",
            "usdactflg", *YN_FIELDS,          # checkbox flags (Y / blank)
        ]
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
        for name, label in YN_FIELDS.items():
            self.fields[name] = forms.BooleanField(label=label, required=False)
            self.initial[name] = (getattr(self.instance, name, "") or "").upper() == "Y"
        self.fields[ACTIVE] = forms.BooleanField(label="Active (can login)", required=False)
        if self.instance.pk:
            self.initial[ACTIVE] = self.instance.is_active_user
        else:
            self.initial[ACTIVE] = True
            self.fields["new_password"].required = True
            self.fields["new_password"].help_text = ""

        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs["class"] = "form-check-input"
            else:
                f.widget.attrs["class"] = "form-control"

    def clean_usdusd(self):
        return self.cleaned_data["usdusd"].strip()

    def clean(self):
        cleaned = super().clean()
        for name in YN_FIELDS:
            cleaned[name] = "Y" if cleaned.get(name) else ""
        cleaned[ACTIVE] = "Y" if cleaned.get(ACTIVE) else "N"
        return cleaned

    # ---- layout helper for the template ----
    def sections(self):
        def bf(*names):
            return [self[n] for n in names]
        return [
            ("Login", bf("usdusd", "new_password", "usdnam", "usdemail"), False),
            ("Details", bf("usddesig", "usdcomsno", "usddepsno", "usdlocsno", "usduno", "usdprintername"), False),
            ("Status", bf(ACTIVE, "usdadmin"), True),
            ("Permissions", bf(
                "usdbockpodgrnyn", "usdbrcsalyn", "usdlacsalyn", "usdprnsalyn", "usdeggsalyn",
                "usdccnsalyn", "usdpgfsalyn", "usdcafsalyn", "usdmaisalyn", "usdhegsalyn",
                "usdhassalyn", "usdrepyn", "usdstkrolyn", "usdatfauthyn", "usdsohpvalyn"), True),
            ("Other", bf("usdsalstkcatsnos", "usdatfliamt", "usdatfnosetday"), False),
        ]

    def save(self, acting_user, commit=True):
        """acting_user = login wela inna user (Usdmast). Audit columns fill karanawa."""
        obj = super().save(commit=False)
        now = timezone.localtime()
        code = acting_user.usdusd[:30]

        pwd = self.cleaned_data.get("new_password")
        if pwd:
            obj.usdpwd = make_password(pwd)
            obj.usdpwdddt = now.date()

        if obj.pk is None:                         # new user
            obj.usducdnew = code[:10]
            obj.usdentddt = now.date()
            obj.usdenttime = now.strftime("%H:%M:%S")
        obj.usducdame = code                       # who updated
        obj.usdameddt = now.date()
        obj.usdametime = now.time().replace(microsecond=0)
        if commit:
            obj.save()
        return obj
