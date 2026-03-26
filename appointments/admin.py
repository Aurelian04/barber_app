from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "status", "barber", "client", "service")
    list_display_links = ("id", "start_time")
    list_filter = ("status", "barber", "client")
    search_fields = ("barber__username", "client__username", "service__username")
    ordering = ("-start_time",)