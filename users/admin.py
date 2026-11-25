
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Informations bibliothèque", {
            "fields": ("role", "telephone"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations bibliothèque", {
            "fields": ("email", "role", "telephone"),
        }),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = ("role", "is_staff", "is_active")

    search_fields = ("username", "email", "first_name", "last_name")
