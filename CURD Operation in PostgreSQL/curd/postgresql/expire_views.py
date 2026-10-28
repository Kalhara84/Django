from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import login_required
from .expire_forms import HeaderForm, LineFormSet, lookup_choices
from .models import Excmast, Exhmast, Exlmast, Exlocmast

LINE_FIELDS = ["exlexssno", "exlexpsno", "exlgensno", "exlcomplddt", "exlcutoffddt"]


@login_required
def expire_list(request):
    cats = dict(Excmast.objects.values_list("excsno", "excnam"))
    locs = dict(Exlocmast.objects.values_list("exlocsno", "exlocnam"))
    counts = dict(Exlmast.objects.values("exlexhsno").annotate(c=Count("exlsno")).values_list("exlexhsno", "c"))
    rows = list(Exhmast.objects.all())
    for h in rows:
        h.cat_name = cats.get(h.exhexcsno, "")
        h.loc_name = locs.get(h.exhexlocsno, "")
        h.line_count = counts.get(h.exhsno, 0)
    return render(request, "postgresql/expire/list.html", {"rows": rows})


def _save(hform, formset, user):
    now = timezone.localtime()
    today, tm = now.date(), now.time().replace(microsecond=0)
    code = user.usdusd[:30]

    with transaction.atomic():
        h = hform.save(commit=False)
        if h.pk is None:
            h.exhucdnew, h.exhentddt, h.exhenttime = code, today, tm
        else:
            h.exhucdame, h.exhameddt, h.exhametime = code, today, tm
        h.save()

        existing = {l.exllno: l for l in Exlmast.objects.filter(exlexhsno=h.exhsno)}
        for no, form in enumerate(formset.forms, start=1):
            data = {k: form.cleaned_data[k] for k in LINE_FIELDS}
            line = existing.pop(no, None)
            if line is None:
                Exlmast.objects.create(
                    exlexhsno=h.exhsno, exllno=no, exlucdnew=code, exlentddt=today, exlenttime=tm, **data)
            elif any(getattr(line, k) != v for k, v in data.items()):
                for k, v in data.items():
                    setattr(line, k, v)
                line.exlucdame, line.exlameddt, line.exlametime = code, today, tm
                line.save()
        for line in existing.values():          # row remove karapu ewa
            line.delete()
    return h


def _expire_form(request, obj):
    choices = lookup_choices()
    kwargs = {"prefix": "lines", "form_kwargs": {"choices": choices}}

    if request.method == "POST":
        hform = HeaderForm(request.POST, instance=obj, choices=choices)
        formset = LineFormSet(
            request.POST, error_messages={"too_few_forms": "Add at least one detail line"}, **kwargs)
        for f in formset.forms:                 # blank row ekak thiyenna ba
            f.empty_permitted = False
        h_ok, l_ok = hform.is_valid(), formset.is_valid()
        if h_ok and l_ok:
            saved = _save(hform, formset, request.usd)
            messages.success(request, f"Expire entry '{saved.exhdno}' {'updated' if obj else 'added'}.")
            return redirect("expire_list")
    else:
        hform = HeaderForm(instance=obj, choices=choices)
        initial = []
        if obj:
            initial = [{k: getattr(l, k) for k in LINE_FIELDS}
                       for l in Exlmast.objects.filter(exlexhsno=obj.exhsno).order_by("exllno")]
        formset = LineFormSet(initial=initial, **kwargs)

    return render(request, "postgresql/expire/form.html", {"hform": hform, "formset": formset, "obj": obj})


@login_required
def expire_add(request):
    return _expire_form(request, None)


@login_required
def expire_edit(request, pk):
    return _expire_form(request, get_object_or_404(Exhmast, pk=pk))


@login_required
@require_POST
def expire_delete(request, pk):
    obj = get_object_or_404(Exhmast, pk=pk)
    with transaction.atomic():
        Exlmast.objects.filter(exlexhsno=obj.exhsno).delete()
        obj.delete()
    messages.success(request, f"Expire entry '{obj.exhdno}' deleted.")
    return redirect("expire_list")
