from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import BarberWeeklyScheduleViewSet, LunchBreakViewSet, BarberScheduleExceptionViewSet, AvailableSlotsView

router = DefaultRouter()
router.register(r"barber/weekly-schedules", BarberWeeklyScheduleViewSet, basename="weekly-schedule")
router.register(r"barber/lunch-breaks", LunchBreakViewSet, basename="barber-lunch")
router.register(r"barber/exception-schedules", BarberScheduleExceptionViewSet, basename="keekly-exception")

urlpatterns = [
    path("barber/available-slots", AvailableSlotsView.as_view()),
]

urlpatterns += router.urls