from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["id", "username", "email", "is_barber", "is_client", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        ("Roluri", {"fields": ("is_barber", "is_client", "phone")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Roluri", {"fields": ("is_barber", "is_client", "phone")}),
    )
