from django import forms
from django.forms import BoundField, formset_factory
from django.utils import timezone

from .models import Excmast, Exhmast, Exlocmast, Expmast, Exsmast, GGenmast

SELECT = [("", "-- Select --")]


def lookup_choices():
    return {
        "cat": SELECT + [(o.excsno, f"{o.excexc} - {o.excnam}") for o in Excmast.objects.all()],
        "loc": SELECT + [(o.exlocsno, f"{o.exlocloc} - {o.exlocnam}") for o in Exlocmast.objects.all()],
        "svc": SELECT + [(o.exssno, f"{o.exsexs} - {o.exsnam}") for o in Exsmast.objects.all()],
        "per": SELECT + [(o.expsno, f"{o.expexp} ({o.expdays} days)" if o.expdays is not None else o.expexp)
                         for o in Expmast.objects.all()],
        "acc": SELECT + [
            (o.gensno, f"{o.genctl}{'-' + o.gensub if o.gensub else ''}  {o.gendes or ''}".strip())
            for o in GGenmast.objects.all()
        ],
    }


class BSBoundField(BoundField):

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = dict(attrs or {})
        if self.errors:
            base = attrs.get("class") or self.field.widget.attrs.get("class", "")
            attrs["class"] = f"{base} is-invalid".strip()
            attrs["title"] = " ".join(self.errors)
        return super().as_widget(widget, attrs, only_initial)


class BSFormMixin:
    bound_field_class = BSBoundField          # Django 5.2+


def _combo(label, **kw):
    return forms.TypedChoiceField(
        label=label, choices=[], coerce=int, empty_value=None,
        error_messages={"required": f"{label} is required", "invalid_choice": f"Select a valid {label}"},
        widget=forms.Select(attrs={"class": "form-select"}), **kw)


def _date(label):
    return forms.DateField(
        label=label,
        error_messages={"required": f"{label} is required", "invalid": f"Enter a valid {label}"},
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}))


# ------------------------------------------------------------------ header
class HeaderForm(BSFormMixin, forms.ModelForm):
    exhexcsno = _combo("Item Category")
    exhexlocsno = _combo("Location")

    class Meta:
        model = Exhmast
        fields = ["exhdno", "exhddt", "exhdes", "exhexcsno", "exhexlocsno"]
        labels = {"exhdno": "Code", "exhddt": "Date", "exhdes": "Description"}
        widgets = {
            "exhdno": forms.TextInput(attrs={"class": "form-control", "maxlength": 30, "autocomplete": "off"}),
            "exhddt": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}),
            "exhdes": forms.TextInput(attrs={"class": "form-control", "maxlength": 50, "autocomplete": "off"}),
        }
        error_messages = {
            "exhdno": {"required": "Code is required"},
            "exhddt": {"required": "Date is required", "invalid": "Enter a valid Date"},
            "exhdes": {"required": "Description is required"},
        }

    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exhexcsno"].choices = choices["cat"]
        self.fields["exhexlocsno"].choices = choices["loc"]
        if not self.instance.pk:
            self.initial["exhddt"] = timezone.localdate()

    def clean_exhdno(self):
        code = (self.cleaned_data["exhdno"] or "").strip()
        qs = Exhmast.objects.filter(exhdno=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This Code already exists")
        return code


# ------------------------------------------------------------------- lines
class LineForm(BSFormMixin, forms.Form):
    exlexssno = _combo("Service Cat")
    exlexpsno = _combo("Period")
    exlgensno = _combo("Acc Code")
    exlcomplddt = _date("Complete Date")
    exlcutoffddt = _date("Cutoff Date")

    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exlexssno"].choices = choices["svc"]
        self.fields["exlexpsno"].choices = choices["per"]
        self.fields["exlgensno"].choices = choices["acc"]
        for f in self.fields.values():
            f.widget.attrs["class"] += " form-select-sm" if isinstance(f.widget, forms.Select) else " form-control-sm"


LineFormSet = formset_factory(LineForm, extra=0, min_num=1, validate_min=True)
