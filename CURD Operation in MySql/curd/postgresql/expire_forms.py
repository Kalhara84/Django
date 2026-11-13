# =============================================================================
# postgresql/expire_forms.py - forms of the Expire Module
# =============================================================================
# Used by:  expire_views.py
# Uses:     models.py (Exhmast, Exlmast and the combo tables)
# Shown in: templates/postgresql/expire/form.html (+ _field.html, _row.html)
#
#   HeaderForm  -> top part of the page  -> saved to exhmast
#   LineForm    -> one table row         -> saved to exlmast
#   LineFormSet -> all rows (+ / - buttons add and remove rows)
#   LocationForm-> "Add Location" pop-up -> saved to exlocmast
# =============================================================================
from django import forms
from django.forms import BoundField, formset_factory
from django.utils import timezone

from .models import Excmast, Exhmast, Exlocmast, Expmast, Exsmast, GGenmast

# First item of every combo box
SELECT = [("", "-- Select --")]


def lookup_choices():
    """Load the data of all combo boxes from the database (once per request)."""
    return {
        # Item Category  <- excmast
        "cat": SELECT + [(o.excsno, f"{o.excexc} - {o.excnam}") for o in Excmast.objects.all()],

        # Location       <- exlocmast
        "loc": SELECT + [(o.exlocsno, f"{o.exlocloc} - {o.exlocnam}") for o in Exlocmast.objects.all()],

        # Service Cat    <- exsmast
        "svc": SELECT + [(o.exssno, f"{o.exsexs} - {o.exsnam}") for o in Exsmast.objects.all()],

        # Period         <- expmast
        "per": SELECT + [(o.expsno, f"{o.expexp} ({o.expdays} days)" if o.expdays is not None else o.expexp)
                         for o in Expmast.objects.all()],

        # Acc Code       <- g_genmast
        "acc": SELECT + [
            (o.gensno, f"{o.genctl}{'-' + o.gensub if o.gensub else ''}  {o.gendes or ''}".strip())
            for o in GGenmast.objects.all()
        ],
    }


class BSBoundField(BoundField):
    """Adds the Bootstrap 'is-invalid' class (red border) to a field that has an error."""

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = dict(attrs or {})
        if self.errors:
            # Keep the normal css class and add is-invalid
            base = attrs.get("class") or self.field.widget.attrs.get("class", "")
            attrs["class"] = f"{base} is-invalid".strip()
            # Error text shows when the mouse is over the field
            attrs["title"] = " ".join(self.errors)
        return super().as_widget(widget, attrs, only_initial)


class BSFormMixin:
    # Every form that uses this mixin gets the red-border fields above
    bound_field_class = BSBoundField


def _combo(label, **kw):
    """A required combo box. The chosen id is converted to a number."""
    return forms.TypedChoiceField(
        label=label, choices=[], coerce=int, empty_value=None,
        error_messages={"required": f"{label} is required", "invalid_choice": f"Select a valid {label}"},
        widget=forms.Select(attrs={"class": "form-select"}), **kw)


def _date(label):
    """A required date picker (type="date")."""
    return forms.DateField(
        label=label,
        error_messages={"required": f"{label} is required", "invalid": f"Enter a valid {label}"},
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}))


# -----------------------------------------------------------------------------
# HEADER (exhmast): code, date, description, item category, location
# -----------------------------------------------------------------------------
class HeaderForm(BSFormMixin, forms.ModelForm):
    # The two combo boxes. Their choices are filled in __init__.
    exhexcsno = _combo("Item Category")
    exhexlocsno = _combo("Location")

    class Meta:
        model = Exhmast
        fields = ["exhdno", "exhddt", "exhdes", "exhexcsno", "exhexlocsno"]

        # Label shown above each field
        labels = {"exhdno": "Code", "exhddt": "Date", "exhdes": "Description"}

        # Input types and css classes
        widgets = {
            "exhdno": forms.TextInput(attrs={"class": "form-control", "maxlength": 30, "autocomplete": "off"}),
            "exhddt": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}),
            "exhdes": forms.TextInput(attrs={"class": "form-control", "maxlength": 50, "autocomplete": "off"}),
        }

        # Messages shown when a field is empty or wrong
        error_messages = {
            "exhdno": {"required": "Code is required"},
            "exhddt": {"required": "Date is required", "invalid": "Enter a valid Date"},
            "exhdes": {"required": "Description is required"},
        }

    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, **kwargs)

        # Fill the combo boxes (data comes from lookup_choices)
        self.fields["exhexcsno"].choices = choices["cat"]
        self.fields["exhexlocsno"].choices = choices["loc"]

        # New entry: the date starts as today
        if not self.instance.pk:
            self.initial["exhddt"] = timezone.localdate()

    def clean_exhdno(self):
        """The code must be unique."""
        code = (self.cleaned_data["exhdno"] or "").strip()
        qs = Exhmast.objects.filter(exhdno=code)

        # When editing, ignore the record itself
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This Code already exists")

        return code


# -----------------------------------------------------------------------------
# LINE (exlmast): service cat, period, acc code, complete date, cutoff date
# -----------------------------------------------------------------------------
class LineForm(BSFormMixin, forms.Form):
    # Combo boxes (choices are filled in __init__)
    exlexssno = _combo("Service Cat")
    exlexpsno = _combo("Period")
    exlgensno = _combo("Acc Code")

    # Date pickers
    exlcomplddt = _date("Complete Date")
    exlcutoffddt = _date("Cutoff Date")

    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, **kwargs)

        # Fill the combo boxes
        self.fields["exlexssno"].choices = choices["svc"]
        self.fields["exlexpsno"].choices = choices["per"]
        self.fields["exlgensno"].choices = choices["acc"]

        # Small size inputs for the table
        for f in self.fields.values():
            f.widget.attrs["class"] += " form-select-sm" if isinstance(f.widget, forms.Select) else " form-control-sm"


# Many LineForms = the table rows.
#   min_num=1 -> at least one row.  extra=0 -> no extra empty rows.
LineFormSet = formset_factory(LineForm, extra=0, min_num=1, validate_min=True)


# -----------------------------------------------------------------------------
# NEW LOCATION (exlocmast): the "Add Location" pop-up on the Expire form
# -----------------------------------------------------------------------------
class LocationForm(forms.ModelForm):
    """Checks the Location Code and Name typed in the pop-up. Saved by expire_views.location_add."""

    class Meta:
        model = Exlocmast
        fields = ["exlocloc", "exlocnam"]
        labels = {"exlocloc": "Location Code", "exlocnam": "Location Name"}
        error_messages = {
            "exlocloc": {"required": "Location Code is required"},
            "exlocnam": {"required": "Location Name is required"},
        }

    def clean_exlocloc(self):
        """The location code must be unique (capital/small letters are treated the same)."""
        code = (self.cleaned_data["exlocloc"] or "").strip()
        if Exlocmast.objects.filter(exlocloc__iexact=code).exists():
            raise forms.ValidationError("This Location Code already exists")
        return code

    def clean_exlocnam(self):
        # Remove spaces around the name
        return (self.cleaned_data["exlocnam"] or "").strip()
