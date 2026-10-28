# =============================================================================
# postgresql/expire_forms.py  -  Forms for the Expire module
# =============================================================================
# This file defines the forms used to create and edit expire entries.
#
# An expire entry has two levels:
#   HEADER (one row in exhmast)  ->  HeaderForm
#   LINES  (many rows in exlmast) ->  LineForm / LineFormSet
#
# The template renders one HeaderForm and then a formset of LineForms side by
# side so the user can add/edit the header and all its lines on one page.
#
# Key helpers in this file:
#   lookup_choices()  - loads all dropdown options from the lookup tables once
#                       and returns them as a dict so both HeaderForm and
#                       LineForm can share the same data without extra DB hits.
#   BSBoundField      - extends Django's BoundField to automatically add
#                       Bootstrap 'is-invalid' CSS class when a field has errors.
#   BSFormMixin       - mix into any form to activate BSBoundField.
#   _combo()          - shortcut to build a styled dropdown (TypedChoiceField).
#   _date()           - shortcut to build a styled date picker (DateField).
#   HeaderForm        - ModelForm for the exhmast header row.
#   LineForm          - plain Form for one exlmast line row.
#   LineFormSet       - a set of LineForms (created via formset_factory).
#
# Connections:
#   - models.py       -> Excmast, Exlocmast, Exsmast, Expmast, GGenmast
#                        (lookup tables for dropdowns)
#                        Exhmast (the header model HeaderForm wraps)
#   - expire_views.py -> uses HeaderForm, LineFormSet, lookup_choices()
# =============================================================================

from django import forms                                # Django form base classes
from django.forms import BoundField, formset_factory    # BoundField for custom rendering;
                                                        # formset_factory creates LineFormSet
from django.utils import timezone                       # timezone-aware date/time

# Lookup-table models (for populating dropdowns) and header model.
from .models import Excmast, Exhmast, Exlocmast, Expmast, Exsmast, GGenmast

# Placeholder option that appears at the top of every dropdown.
SELECT = [("", "-- Select --")]


# ---------------------------------------------------------------------------
# lookup_choices()  -  load all dropdown options in one go
# ---------------------------------------------------------------------------
def lookup_choices():
    """
    Query all lookup tables and return their data as choice lists.

    Returns a dict:
        {
          "cat":  [(excsno,  "code - name"), ...],   # item categories (Excmast)
          "loc":  [(exlocsno,"code - name"), ...],   # locations (Exlocmast)
          "svc":  [(exssno,  "code - name"), ...],   # service categories (Exsmast)
          "per":  [(expsno,  "code (N days)"), ...], # periods (Expmast)
          "acc":  [(gensno,  "ctl-sub desc"), ...],  # account codes (GGenmast)
        }

    Called by expire_views.py -> _expire_form() once per request.
    Both HeaderForm and all LineForms receive this dict so the DB is only
    queried once, not once per form field.
    """
    return {
        # Category dropdown: value = excsno (int), label = "code - name"
        "cat": SELECT + [(o.excsno, f"{o.excexc} - {o.excnam}") for o in Excmast.objects.all()],

        # Location dropdown: value = exlocsno (int), label = "code - name"
        "loc": SELECT + [(o.exlocsno, f"{o.exlocloc} - {o.exlocnam}") for o in Exlocmast.objects.all()],

        # Service category dropdown: value = exssno (int), label = "code - name"
        "svc": SELECT + [(o.exssno, f"{o.exsexs} - {o.exsnam}") for o in Exsmast.objects.all()],

        # Period dropdown: value = expsno (int), label = "code (N days)" or just "code"
        "per": SELECT + [(o.expsno, f"{o.expexp} ({o.expdays} days)" if o.expdays is not None else o.expexp)
                         for o in Expmast.objects.all()],

        # Account code dropdown: value = gensno (int), label = "ctl-sub description"
        "acc": SELECT + [
            (o.gensno, f"{o.genctl}{'-' + o.gensub if o.gensub else ''}  {o.gendes or ''}".strip())
            for o in GGenmast.objects.all()
        ],
    }


# ---------------------------------------------------------------------------
# BSBoundField  -  Bootstrap-aware field renderer
# ---------------------------------------------------------------------------
class BSBoundField(BoundField):
    """
    Custom BoundField that adds Bootstrap validation CSS when a field has errors.

    When a field fails validation, Django stores error messages on it.
    This class intercepts the rendering and appends 'is-invalid' to the widget's
    CSS class so Bootstrap shows the red border automatically.

    Activated by setting  bound_field_class = BSBoundField  on a form (BSFormMixin).
    """

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = dict(attrs or {})   # copy the attrs dict so we do not modify the original
        if self.errors:
            # Get whatever CSS class the widget already has.
            base = attrs.get("class") or self.field.widget.attrs.get("class", "")
            # Append Bootstrap's 'is-invalid' class to trigger red styling.
            attrs["class"] = f"{base} is-invalid".strip()
            # Put all error messages into the title attribute for a tooltip.
            attrs["title"] = " ".join(self.errors)
        # Render the widget with the (possibly updated) attrs.
        return super().as_widget(widget, attrs, only_initial)


# ---------------------------------------------------------------------------
# BSFormMixin  -  mix into a form class to enable BSBoundField
# ---------------------------------------------------------------------------
class BSFormMixin:
    """
    Mixin that tells Django 5.2+ to use BSBoundField for every field.
    Add this as the first parent class of any form that needs Bootstrap error styling:

        class MyForm(BSFormMixin, forms.ModelForm):
            ...
    """
    # Django 5.2+ reads this attribute to decide which BoundField subclass to use.
    bound_field_class = BSBoundField


# ---------------------------------------------------------------------------
# _combo()  -  helper to build a styled integer dropdown field
# ---------------------------------------------------------------------------
def _combo(label, **kw):
    """
    Return a TypedChoiceField for an integer foreign-key dropdown.

    - choices=[] is empty here; the form's __init__ fills it from lookup_choices().
    - coerce=int converts the selected string value to an integer automatically.
    - empty_value=None means "nothing selected" evaluates to None (not 0 or "").
    - The widget is a Bootstrap-styled <select> element.
    """
    return forms.TypedChoiceField(
        label=label, choices=[], coerce=int, empty_value=None,
        error_messages={"required": f"{label} is required", "invalid_choice": f"Select a valid {label}"},
        widget=forms.Select(attrs={"class": "form-select"}), **kw)


# ---------------------------------------------------------------------------
# _date()  -  helper to build a styled date picker field
# ---------------------------------------------------------------------------
def _date(label):
    """
    Return a DateField with an HTML5 date picker widget.

    format="%Y-%m-%d"  matches the value browsers send back (ISO 8601).
    type="date"        tells the browser to show its native date picker UI.
    """
    return forms.DateField(
        label=label,
        error_messages={"required": f"{label} is required", "invalid": f"Enter a valid {label}"},
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}))


# ---------------------------------------------------------------------------
# HeaderForm  -  form for one Exhmast (expire header) row
# ---------------------------------------------------------------------------
class HeaderForm(BSFormMixin, forms.ModelForm):
    """
    Form to create or edit one expire header (exhmast row).

    Fields:
      exhdno      - unique document code (text)
      exhddt      - document date (date picker)
      exhdes      - description (text)
      exhexcsno   - item category dropdown (populated from Excmast)
      exhexlocsno - location dropdown (populated from Exlocmast)

    The choices for the two dropdowns are injected via the 'choices' kwarg
    in __init__ so they come from a single lookup_choices() call per request.

    Validation:
      clean_exhdno() ensures the document code is unique (excluding the current
      row when editing).

    Used by: expire_views.py -> _expire_form()
    """

    # Override the model's integer fields with our _combo() dropdown helper.
    exhexcsno = _combo("Item Category")
    exhexlocsno = _combo("Location")

    class Meta:
        model = Exhmast   # this form saves/updates rows in the exhmast table

        # Which model fields to include in the form.
        fields = ["exhdno", "exhddt", "exhdes", "exhexcsno", "exhexlocsno"]

        # Human-readable labels for the text fields.
        labels = {"exhdno": "Code", "exhddt": "Date", "exhdes": "Description"}

        # Custom widgets with Bootstrap styling and HTML5 attributes.
        widgets = {
            "exhdno": forms.TextInput(attrs={"class": "form-control", "maxlength": 30, "autocomplete": "off"}),
            "exhddt": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}),
            "exhdes": forms.TextInput(attrs={"class": "form-control", "maxlength": 50, "autocomplete": "off"}),
        }

        # Custom error messages for each field.
        error_messages = {
            "exhdno": {"required": "Code is required"},
            "exhddt": {"required": "Date is required", "invalid": "Enter a valid Date"},
            "exhdes": {"required": "Description is required"},
        }

    def __init__(self, *args, choices, **kwargs):
        """
        choices  - dict returned by lookup_choices() (injected from expire_views.py).
                   We pull "cat" and "loc" from it to populate the two dropdowns.

        If this is a new header (no instance pk), pre-fill the date to today.
        """
        super().__init__(*args, **kwargs)

        # Inject choice lists into the two dropdown fields.
        self.fields["exhexcsno"].choices = choices["cat"]    # item categories
        self.fields["exhexlocsno"].choices = choices["loc"]  # locations

        # Default the date field to today when adding a new entry.
        if not self.instance.pk:
            self.initial["exhddt"] = timezone.localdate()

    def clean_exhdno(self):
        """
        Validate that the document code is unique in exhmast.

        When editing an existing header, exclude the current row from the
        uniqueness check so the user can save without changing the code.
        """
        code = (self.cleaned_data["exhdno"] or "").strip()
        qs = Exhmast.objects.filter(exhdno=code)

        if self.instance.pk:
            # Exclude the row being edited so it does not conflict with itself.
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This Code already exists")

        return code


# ---------------------------------------------------------------------------
# LineForm  -  form for one Exlmast (expire line) row
# ---------------------------------------------------------------------------
class LineForm(BSFormMixin, forms.Form):
    """
    Plain form (not a ModelForm) for one detail line in the expire entry.

    Fields:
      exlexssno    - service category dropdown  (-> exsmast)
      exlexpsno    - period dropdown             (-> expmast)
      exlgensno    - account code dropdown       (-> g_genmast)
      exlcomplddt  - completion date picker
      exlcutoffddt - cutoff date picker

    Multiple LineForms are combined into a LineFormSet (see below) so the
    template can render them as rows in a table.

    The choices dict is injected in __init__ (same pattern as HeaderForm).
    Also adds '-sm' Bootstrap size variant to all widgets so they look compact
    in a table row.

    Used by: expire_views.py -> _expire_form() via LineFormSet
    """

    # Dropdown fields - choices filled in __init__
    exlexssno = _combo("Service Cat")
    exlexpsno = _combo("Period")
    exlgensno = _combo("Acc Code")

    # Date picker fields
    exlcomplddt = _date("Complete Date")
    exlcutoffddt = _date("Cutoff Date")

    def __init__(self, *args, choices, **kwargs):
        """
        choices - dict from lookup_choices() with keys "svc", "per", "acc".
        """
        super().__init__(*args, **kwargs)

        # Set the choice lists for the three dropdowns.
        self.fields["exlexssno"].choices = choices["svc"]
        self.fields["exlexpsno"].choices = choices["per"]
        self.fields["exlgensno"].choices = choices["acc"]

        # Add Bootstrap small-size variant to every widget so lines fit neatly
        # in a compact table layout.
        for f in self.fields.values():
            # Selects get 'form-select-sm'; text/date inputs get 'form-control-sm'.
            f.widget.attrs["class"] += " form-select-sm" if isinstance(f.widget, forms.Select) else " form-control-sm"


# ---------------------------------------------------------------------------
# LineFormSet  -  a formset of LineForms
# ---------------------------------------------------------------------------
# formset_factory() creates a class that manages multiple LineForms together.
#   extra=0        - do not add blank extra forms by default (JS adds them dynamically)
#   min_num=1      - require at least 1 line (enforced by validate_min=True)
#   validate_min   - raise an error if fewer than min_num forms are submitted
#
# expire_views.py creates an instance:
#   LineFormSet(request.POST, prefix="lines", form_kwargs={"choices": choices})
# The form_kwargs dict is passed to each LineForm's __init__ as keyword args.
LineFormSet = formset_factory(LineForm, extra=0, min_num=1, validate_min=True)
