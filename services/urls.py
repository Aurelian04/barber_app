from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ServiceViewList, BarberServiceViewSet

router = DefaultRouter()
router.register(r"barber/services", BarberServiceViewSet, basename="barber-services")

urlpatterns = [
    path("services/", ServiceViewList.as_view(), name="service-list"),
    path("", include(router.urls)),
]
