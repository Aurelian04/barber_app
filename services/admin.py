from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "barber", "duration_minutes", "price", "is_active")
    list_display_links = ("id", "name")  # <-- asta îți dă link de editare
    list_filter = ("is_active", "barber")
    search_fields = ("name", "description", "barber__username")
    ordering = ("-id",)
