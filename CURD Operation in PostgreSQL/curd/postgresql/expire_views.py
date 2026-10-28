# =============================================================================
# postgresql/expire_views.py  -  View functions for the Expire Module CRUD
# =============================================================================
# This file handles the complete business logic and HTTP request cycle for
# the Expire entry workflow:
#
#   URL Endpoints handled:
#     /expire/            -> expire_list()   List all expire entries with totals
#     /expire/add/        -> expire_add()    Create a new header and lines
#     /expire/<pk>/edit/  -> expire_edit()   Update existing header and lines
#     /expire/<pk>/delete/-> expire_delete() Delete header and all child lines
#
# Relationships and Connected Files:
#   - models.py       -> Exhmast (Header table), Exlmast (Line items table),
#                        Excmast (Categories), Exlocmast (Locations).
#   - expire_forms.py -> HeaderForm (validates header row),
#                        LineFormSet (manages collection of item lines),
#                        lookup_choices() (loads dropdown cached choices).
#   - decorators.py   -> @login_required (protects views so only logged-in
#                        users can view, add, edit, or delete records).
#   - templates       -> postgresql/expire/list.html (listing table),
#                        postgresql/expire/form.html (master-detail input form).
# =============================================================================

from django.contrib import messages                        # Flash notification banners shown to the user
from django.db import transaction                          # Provides atomic transactions (rollback on error)
from django.db.models import Count                         # Aggregation function to count child lines per header
from django.shortcuts import get_object_or_404, redirect, render  # Standard Django shortcuts for rendering & redirecting
from django.utils import timezone                          # Generates current date and time with local timezone support
from django.views.decorators.http import require_POST     # Restricts destructive actions (delete) to HTTP POST only

# Access control decorator ensuring user session exists
from .decorators import login_required

# Form classes and lookup dictionary builder from expire_forms.py
from .expire_forms import HeaderForm, LineFormSet, lookup_choices

# PostgreSQL database models from models.py
from .models import Excmast, Exhmast, Exlmast, Exlocmast


# -----------------------------------------------------------------------------
# Line Fields Constant
# -----------------------------------------------------------------------------
# Names of the form fields corresponding to columns in the Exlmast line table.
# Used for batch extraction and comparison during create and update operations:
#   exlexssno   - Service Type foreign key / choice ID
#   exlexpsno   - Period Type foreign key / choice ID
#   exlgensno   - General Account foreign key / choice ID
#   exlcomplddt - Completion target date
#   exlcutoffddt- Cut-off deadline date
# -----------------------------------------------------------------------------
LINE_FIELDS = ["exlexssno", "exlexpsno", "exlgensno", "exlcomplddt", "exlcutoffddt"]


# =============================================================================
# EXPIRE LIST VIEW
# =============================================================================
@login_required
def expire_list(request):
    """
    Display a summary table of all Expire records.

    Process:
      1. Pre-fetches category and location lookups into memory dictionaries.
      2. Groups and counts detail lines for each header row in a single query.
      3. Attaches human-readable category name, location name, and line count
         to each header object.
      4. Renders postgresql/expire/list.html.

    Template: postgresql/templates/postgresql/expire/list.html
    Context:  {'rows': list of Exhmast instances with dynamic attributes}
    """
    # Create lookup map: {excsno (ID): excnam (Name)} for fast in-memory category name resolution
    cats = dict(Excmast.objects.values_list("excsno", "excnam"))

    # Create lookup map: {exlocsno (ID): exlocnam (Name)} for fast location name resolution
    locs = dict(Exlocmast.objects.values_list("exlocsno", "exlocnam"))

    # Query line counts per header: {exlexhsno (Header ID): count of lines} to avoid N+1 query problem
    counts = dict(Exlmast.objects.values("exlexhsno").annotate(c=Count("exlsno")).values_list("exlexhsno", "c"))

    # Fetch all header records from the PostgreSQL database
    rows = list(Exhmast.objects.all())

    # Attach human-readable names and child line counts to each record
    for h in rows:
        h.cat_name = cats.get(h.exhexcsno, "")      # Category name from excmast
        h.loc_name = locs.get(h.exhexlocsno, "")    # Location name from exlocmast
        h.line_count = counts.get(h.exhsno, 0)      # Total number of detail lines from exlmast

    # Render HTML listing page with the populated rows
    return render(request, "postgresql/expire/list.html", {"rows": rows})


# =============================================================================
# HELPER: ATOMIC SAVE FOR HEADER AND DETAIL LINES
# =============================================================================
def _save(hform, formset, user):
    """
    Save both the header (Exhmast) and all its lines (Exlmast) atomically.

    Parameters:
      - hform   : Validated HeaderForm instance.
      - formset : Validated LineFormSet instance containing item lines.
      - user    : Currently logged-in Usdmast user object from request.usd.

    Database Safety:
      Uses transaction.atomic() so if any line fails, the entire transaction
      is rolled back, keeping the database in a consistent state.

    Audit Trail:
      - New record: sets exhucdnew/exlucdnew (creator), entry date, entry time.
      - Existing record: sets exhucdame/exlucdame (amender), amend date, amend time.
    """
    # Get current localized date and time without microseconds
    now = timezone.localtime()
    today, tm = now.date(), now.time().replace(microsecond=0)

    # Get user identifier string (truncated to max 30 chars for database column limit)
    code = user.usdusd[:30]

    with transaction.atomic():
        # Step 1: Save Header without committing immediately to set audit fields
        h = hform.save(commit=False)

        if h.pk is None:
            # New record: populate creation audit fields
            h.exhucdnew, h.exhentddt, h.exhenttime = code, today, tm
        else:
            # Existing record: populate modification audit fields
            h.exhucdame, h.exhameddt, h.exhametime = code, today, tm

        # Commit header changes to PostgreSQL
        h.save()

        # Step 2: Synchronize detail lines in Exlmast table
        # Fetch current lines in DB mapped by line number (exllno): {1: line1, 2: line2, ...}
        existing = {l.exllno: l for l in Exlmast.objects.filter(exlexhsno=h.exhsno)}

        # Iterate over submitted formset lines sequentially
        for no, form in enumerate(formset.forms, start=1):
            # Extract cleaned field values for the 5 line columns
            data = {k: form.cleaned_data[k] for k in LINE_FIELDS}

            # Check if this line number already exists in DB
            line = existing.pop(no, None)

            if line is None:
                # Brand new line added by user: insert new row into exlmast
                Exlmast.objects.create(
                    exlexhsno=h.exhsno,     # Foreign key referencing parent header ID
                    exllno=no,              # Sequential line number (1, 2, 3...)
                    exlucdnew=code,         # Created by user code
                    exlentddt=today,        # Creation date
                    exlenttime=tm,          # Creation time
                    **data                  # Unpack line values (service, period, account, dates)
                )
            elif any(getattr(line, k) != v for k, v in data.items()):
                # Existing line has modified values: update fields and amend audit columns
                for k, v in data.items():
                    setattr(line, k, v)
                line.exlucdame, line.exlameddt, line.exlametime = code, today, tm
                line.save()

        # Step 3: Delete lines that were removed by the user in the UI
        # Any items still remaining in the 'existing' dict were deleted on the frontend
        for line in existing.values():
            line.delete()

    return h


# =============================================================================
# HELPER: SHARED FORM HANDLER FOR ADD AND EDIT
# =============================================================================
def _expire_form(request, obj):
    """
    Common handler for GET and POST requests on the Expire Form.

    Parameters:
      - request : The incoming HTTP request.
      - obj     : Exhmast instance if editing, or None if adding new.

    Workflow:
      1. Loads dropdown choices via lookup_choices().
      2. If POST:
           - Binds request.POST data to HeaderForm and LineFormSet.
           - Validates both forms (checks required fields, formats, min lines).
           - On success: saves data via _save(), shows flash message, redirects to list.
      3. If GET:
           - Pre-fills HeaderForm with obj data (or blank if obj is None).
           - Pre-fills LineFormSet with existing Exlmast rows from DB.
           - Renders postgresql/expire/form.html.
    """
    # Fetch cached choices for service, period, and account dropdowns
    choices = lookup_choices()

    # Common keyword arguments passed to the line formset
    kwargs = {"prefix": "lines", "form_kwargs": {"choices": choices}}

    if request.method == "POST":
        # Bind submitted POST data to Header form
        hform = HeaderForm(request.POST, instance=obj, choices=choices)

        # Bind submitted POST data to Lines formset
        formset = LineFormSet(
            request.POST,
            error_messages={"too_few_forms": "Add at least one detail line"},
            **kwargs
        )

        # Ensure no line is left empty/unfilled
        for f in formset.forms:
            f.empty_permitted = False

        # Validate both header form and lines formset
        h_ok, l_ok = hform.is_valid(), formset.is_valid()

        if h_ok and l_ok:
            # Save header and lines inside atomic transaction
            saved = _save(hform, formset, request.usd)

            # Display success notification message
            messages.success(request, f"Expire entry '{saved.exhdno}' {'updated' if obj else 'added'}.")

            # Redirect user back to the expire list view
            return redirect("expire_list")
    else:
        # GET request: instantiate header form (empty or bound to obj)
        hform = HeaderForm(instance=obj, choices=choices)

        # Populate existing detail lines if editing an existing record
        initial = []
        if obj:
            initial = [
                {k: getattr(l, k) for k in LINE_FIELDS}
                for l in Exlmast.objects.filter(exlexhsno=obj.exhsno).order_by("exllno")
            ]

        # Instantiate line formset with existing rows (or empty form if adding)
        formset = LineFormSet(initial=initial, **kwargs)

    # Render template with header form, lines formset, and header object
    return render(
        request,
        "postgresql/expire/form.html",
        {"hform": hform, "formset": formset, "obj": obj}
    )


# =============================================================================
# EXPIRE CREATE VIEW
# =============================================================================
@login_required
def expire_add(request):
    """
    Handle adding a new expire entry (Header + initial detail lines).
    Calls _expire_form helper with obj=None.
    """
    return _expire_form(request, None)


# =============================================================================
# EXPIRE EDIT VIEW
# =============================================================================
@login_required
def expire_edit(request, pk):
    """
    Handle editing an existing expire entry (Header + lines).

    pk: Primary key (exhsno) of the Exhmast record to edit.
    Fetches the record or returns 404 Not Found if missing.
    """
    return _expire_form(request, get_object_or_404(Exhmast, pk=pk))


# =============================================================================
# EXPIRE DELETE VIEW
# =============================================================================
@login_required
@require_POST   # Only allow HTTP POST requests to prevent accidental deletion via GET links
def expire_delete(request, pk):
    """
    Delete an expire entry and all associated line rows from the database.

    Process:
      1. Retrieves the Exhmast header row by pk (exhsno) or returns 404.
      2. Deletes all related Exlmast lines first inside a transaction.
      3. Deletes the Exhmast header record.
      4. Displays success flash message and redirects to expire_list.

    Parameters:
      pk - Primary key (exhsno) of Exhmast to delete.
    """
    # Fetch target header object or return 404 error
    obj = get_object_or_404(Exhmast, pk=pk)

    with transaction.atomic():
        # Step 1: Delete all child detail lines belonging to this header
        Exlmast.objects.filter(exlexhsno=obj.exhsno).delete()

        # Step 2: Delete parent header row
        obj.delete()

    # Inform user of successful deletion
    messages.success(request, f"Expire entry '{obj.exhdno}' deleted.")

    # Redirect back to the listing view
    return redirect("expire_list")
