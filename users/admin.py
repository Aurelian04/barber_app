from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Ce vezi în listă (Read / List)
    list_display = ("id", "username", "email", "phone", "is_barber", "is_client", "is_staff", "is_active")
    list_filter = ("is_barber", "is_client", "is_staff", "is_active")

    # Căutare (Search)
    search_fields = ("username", "email", "phone")

    # Sortare
    ordering = ("-id",)

    # Cum arată pagina de edit (Update)
    fieldsets = DjangoUserAdmin.fieldsets + (
        (_("Extra fields"), {"fields": ("phone", "is_barber", "is_client")}),
    )

    # Cum arată pagina de create user (Create)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (_("Extra fields"), {"fields": ("email", "phone", "is_barber", "is_client")}),
    )
