from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientAppointmentViewSet, BarberAppointmentViewSet

router = DefaultRouter()
router.register("appointments", ClientAppointmentViewSet, basename="client-appointments")
router.register("barber/appointments", BarberAppointmentViewSet, basename="barber-appointments")

urlpatterns = [
    path("", include(router.urls)),
]