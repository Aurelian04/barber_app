from rest_framework.routers import DefaultRouter

from .views import BarberWeeklyScheduleViewSet, LunchBreakViewSet, BarberScheduleExceptionViewSet

router = DefaultRouter()
router.register(r"barber/weekly-schedules", BarberWeeklyScheduleViewSet, basename="weekly-schedule")
router.register(r"barber/lunch-breaks", LunchBreakViewSet, basename="barber-lunch")
router.register(r"barber/exception-schedules", BarberScheduleExceptionViewSet, basename="keekly-exception")