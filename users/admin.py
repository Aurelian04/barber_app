from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Ce vezi în listă (Read / List)
    list_display = ("id", "username", "email", "phone", 
                    "first_name", "last_name", "is_barber", "is_client", "is_staff", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("is_barber", "is_client", "is_staff", "is_active")

    # Căutare (Search)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    # Sortare
    ordering = ("-id",)

    # Cum arată pagina de edit (Update)
    fieldsets = (
    (None, {"fields": ("username", "password")}),
    (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone")}),
    (_("Roles / Extra"), {"fields": ("is_barber", "is_client")}),
    (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    (_("Important dates"), {"fields": ("last_login", "date_joined")}),
)


    # Cum arată pagina de create user (Create)
    add_fieldsets = (
    (None, {
        "classes": ("wide",),
        "fields": ("username", "email", "phone", "password1", "password2", "is_barber", "is_client", "is_staff", "is_superuser"),
    }),
)
