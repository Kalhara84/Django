"""
Django Admin Configuration for 'postgresql' app.

Role of this file:
- Registers models with the built-in Django administration site (/admin/).
- Allows administrators to view, add, edit, and delete database records via Django's default GUI.
"""
from django.contrib import admin
from .models import Usdmast


@admin.register(Usdmast)
class UsdmastAdmin(admin.ModelAdmin):
    """
    Configuration for viewing Usdmast in the Django Admin interface.
    """
    # Columns displayed in the admin list table
    list_display = ("usdsno", "usdusd", "usdnam", "usddesig", "usdemail", "usdadmin", "usdactflg")
    
    # Enable search by username, full name, or email
    search_fields = ("usdusd", "usdnam", "usdemail")
    
    # Filter sidebar options
    list_filter = ("usdadmin", "usdactflg")

