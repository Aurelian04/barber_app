from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientAppointmentView, BarberAppointmentListView

router = DefaultRouter()
router.register("appointments", ClientAppointmentView, basename="client-appointments")
router.register("barber/appointments", BarberAppointmentListView, basename="barber-appointments")

urlpatterns = [
    path("", include(router.urls)),
]