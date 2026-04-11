from django.contrib import admin

from .models import BarberWeeklySchedule, LunchBreak, BarberScheduleException


@admin.register(BarberWeeklySchedule)
class BarberWeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "barber",
        "weekday",
        "start_time",
        "end_time",
        "is_active",
    )
    list_filter = ("weekday", "is_active")
    search_fields = ("barber__username",)
    ordering = ("barber", "weekday", "start_time")


@admin.register(LunchBreak)
class LunchBreakAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "weekly_schedule",
        "start_time",
        "end_time",
    )
    search_fields = ("weekly_schedule__barber__username",)
    ordering = ("weekly_schedule", "start_time")


@admin.register(BarberScheduleException)
class BarberScheduleExceptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "barber",
        "date",
        "start_time",
        "end_time",
        "is_day_off",
        "reason",
    )
    list_filter = ("is_day_off", "date")
    search_fields = ("barber__username", "reason")
    ordering = ("barber", "date", "start_time")