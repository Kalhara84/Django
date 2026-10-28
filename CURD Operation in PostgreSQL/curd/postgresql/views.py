from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .auth import authenticate_usdmast
from .decorators import admin_required, login_required
from .forms import UserForm
from .models import Usdmast


# ------------------------------------------------------------------ login
def login_view(request):
    if request.session.get("usdsno") and request.method == "GET":
        return redirect("dashboard")

    error = None
    usdusd = ""
    if request.method == "POST":
        usdusd = request.POST.get("usdusd", "").strip()
        usdpwd = request.POST.get("usdpwd", "")
        if not usdusd or not usdpwd:
            error = "Please enter User Code and Password"
        else:
            user, error = authenticate_usdmast(usdusd, usdpwd)
            if user:
                request.session.flush()
                request.session["usdsno"] = user.usdsno
                request.session["usdusd"] = user.usdusd
                request.session["usdnam"] = user.usdnam or user.usdusd
                request.session["usdadmin"] = user.usdadmin
                if not request.POST.get("remember"):
                    request.session.set_expiry(0)      # browser close = logout
                nxt = request.GET.get("next", "")
                if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
                    return redirect(nxt)
                return redirect("dashboard")
    return render(request, "postgresql/login.html", {"error": error, "usdusd": usdusd})


@require_POST
def logout_view(request):
    request.session.flush()
    return redirect("login")


# -------------------------------------------------------------- dashboard
@login_required
def dashboard(request):
    stats = Usdmast.objects.aggregate(
        total=Count("usdsno"),
        active=Count("usdsno", filter=~Q(usdactflg__iexact="N")),
        admins=Count("usdsno", filter=Q(usdadmin__iexact="Y")),
    )
    return render(request, "postgresql/dashboard.html", {"stats": stats})


# ------------------------------------------------------------- users CRUD
@admin_required
def user_list(request):
    users = Usdmast.objects.all().order_by("usdsno")
    return render(request, "postgresql/users/list.html", {"users": users})


@admin_required
def user_add(request):
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' added.")
        return redirect("user_list")
    return render(request, "postgresql/users/form.html", {"form": form, "obj": None})


@admin_required
def user_edit(request, pk):
    obj = get_object_or_404(Usdmast, pk=pk)
    form = UserForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save(acting_user=request.usd)
        messages.success(request, f"User '{obj.usdusd}' updated.")
        return redirect("user_list")
    return render(request, "postgresql/users/form.html", {"form": form, "obj": obj})


@admin_required
@require_POST
def user_delete(request, pk):
    obj = get_object_or_404(Usdmast, pk=pk)
    if obj.pk == request.usd.pk:
        messages.error(request, "You cannot delete the user you are logged in as.")
    else:
        obj.delete()
        messages.success(request, f"User '{obj.usdusd}' deleted.")
    return redirect("user_list")
