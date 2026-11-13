# =============================================================================
# postgresql/expire_views.py - pages of the Expire Module
# =============================================================================
# URLs (see urls.py):
#   /expire/                 expire_list     table of all entries
#   /expire/add/             expire_add      new entry
#   /expire/<id>/edit/       expire_edit     change an entry
#   /expire/<id>/delete/     expire_delete   delete an entry and its lines
#   /expire/location/add/    location_add    save a new location from the pop-up
#
# Uses: expire_forms.py (forms), models.py (tables), decorators.py (login check)
# Templates: templates/postgresql/expire/list.html and form.html
# =============================================================================
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import login_required
from .expire_forms import HeaderForm, LineFormSet, LocationForm, lookup_choices
from .models import Excmast, Exhmast, Exlmast, Exlocmast

# Columns of one line (exlmast) that come from the form
LINE_FIELDS = ["exlexssno", "exlexpsno", "exlgensno", "exlcomplddt", "exlcutoffddt"]


# ---------------------------------------------------------------- list page
@login_required
def expire_list(request):
    """Table of all entries (list.html)."""
    # id -> name, so the table can show names instead of ids
    cats = dict(Excmast.objects.values_list("excsno", "excnam"))
    locs = dict(Exlocmast.objects.values_list("exlocsno", "exlocnam"))

    # Number of lines for each entry (one query)
    counts = dict(Exlmast.objects.values("exlexhsno").annotate(c=Count("exlsno")).values_list("exlexhsno", "c"))

    rows = list(Exhmast.objects.all())
    for h in rows:
        # Extra values used by list.html
        h.cat_name = cats.get(h.exhexcsno, "")
        h.loc_name = locs.get(h.exhexlocsno, "")
        h.line_count = counts.get(h.exhsno, 0)

    return render(request, "postgresql/expire/list.html", {"rows": rows})


# ------------------------------------------------------------------- save
def _save(hform, formset, user):
    """Save the header (exhmast) and all lines (exlmast) together.
    If anything fails, nothing is saved (transaction)."""
    now = timezone.localtime()
    today, tm = now.date(), now.time().replace(microsecond=0)

    # Logged-in user code, saved in the created/updated columns
    code = user.usdusd[:30]

    with transaction.atomic():
        # --- header ---
        h = hform.save(commit=False)
        if h.pk is None:
            # New entry: "created" columns
            h.exhucdnew, h.exhentddt, h.exhenttime = code, today, tm
        else:
            # Existing entry: "updated" columns
            h.exhucdame, h.exhameddt, h.exhametime = code, today, tm
        h.save()

        # --- lines ---
        # Lines already in the database: {line no: line}
        existing = {l.exllno: l for l in Exlmast.objects.filter(exlexhsno=h.exhsno)}

        # Rows on the screen are line 1, 2, 3 ...
        for no, form in enumerate(formset.forms, start=1):
            data = {k: form.cleaned_data[k] for k in LINE_FIELDS}
            line = existing.pop(no, None)

            if line is None:
                # New row -> insert (exlexhsno links the line to the header)
                Exlmast.objects.create(
                    exlexhsno=h.exhsno, exllno=no, exlucdnew=code, exlentddt=today, exlenttime=tm, **data)
            elif any(getattr(line, k) != v for k, v in data.items()):
                # Row changed -> update it and fill the "updated" columns
                for k, v in data.items():
                    setattr(line, k, v)
                line.exlucdame, line.exlameddt, line.exlametime = code, today, tm
                line.save()

        # Rows that were removed with the "-" button -> delete from the database
        for line in existing.values():
            line.delete()
    return h


# ------------------------------------------------------- add / edit form
def _expire_form(request, obj):
    """Shared by expire_add (obj = None) and expire_edit (obj = the entry)."""
    # Data for all combo boxes
    choices = lookup_choices()
    kwargs = {"prefix": "lines", "form_kwargs": {"choices": choices}}

    if request.method == "POST":
        # Form submitted: header and rows
        hform = HeaderForm(request.POST, instance=obj, choices=choices)
        formset = LineFormSet(
            request.POST, error_messages={"too_few_forms": "Add at least one detail line"}, **kwargs)

        # An empty row is not allowed
        for f in formset.forms:
            f.empty_permitted = False

        h_ok, l_ok = hform.is_valid(), formset.is_valid()
        if h_ok and l_ok:
            # Everything is valid -> save and go back to the list
            saved = _save(hform, formset, request.usd)
            messages.success(request, f"Expire entry '{saved.exhdno}' {'updated' if obj else 'added'}.")
            return redirect("expire_list")
    else:
        # Page opened: empty form (add) or filled form (edit)
        hform = HeaderForm(instance=obj, choices=choices)
        initial = []
        if obj:
            # Existing lines of this entry, in line order
            initial = [{k: getattr(l, k) for k in LINE_FIELDS}
                       for l in Exlmast.objects.filter(exlexhsno=obj.exhsno).order_by("exllno")]
        formset = LineFormSet(initial=initial, **kwargs)

    return render(request, "postgresql/expire/form.html", {"hform": hform, "formset": formset, "obj": obj})


@login_required
def expire_add(request):
    """New entry."""
    return _expire_form(request, None)


@login_required
def expire_edit(request, pk):
    """Change an entry (pk = exhsno)."""
    return _expire_form(request, get_object_or_404(Exhmast, pk=pk))


@login_required
@require_POST
def expire_delete(request, pk):
    """Delete an entry and its lines (POST only, from the delete pop-up in list.html)."""
    obj = get_object_or_404(Exhmast, pk=pk)

    with transaction.atomic():
        # Lines first, then the header
        Exlmast.objects.filter(exlexhsno=obj.exhsno).delete()
        obj.delete()

    messages.success(request, f"Expire entry '{obj.exhdno}' deleted.")
    return redirect("expire_list")


# ----------------------------------------------------- add location pop-up
@login_required
@require_POST
def location_add(request):
    """Save a new location (exlocmast) from the "Add Location" pop-up.
    Called by expire-form.js without reloading the page; the answer is JSON."""
    form = LocationForm(request.POST)

    if not form.is_valid():
        # Send the first error of each field back, so the pop-up can show it
        errors = {name: errs[0] for name, errs in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    now = timezone.localtime()
    loc = form.save(commit=False)

    # "Created by / date / time" columns
    loc.exlocucdnew = request.usd.usdusd[:30]
    loc.exlocentddt = now.date()
    loc.exlocenttime = now.time().replace(microsecond=0)
    loc.save()

    # id + text for the new <option> in the Location combo box (same text format as lookup_choices)
    return JsonResponse({"ok": True, "id": loc.exlocsno, "label": f"{loc.exlocloc} - {loc.exlocnam}"})
