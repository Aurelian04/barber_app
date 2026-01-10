from django.urls import path, include
from .views import ServiceViewList, ServiceAdminViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"admin/services", ServiceAdminViewSet, basename="admin-services")

urlpatterns = [
    path("services/", ServiceViewList.as_view(), name="service-list"),
    path("", include(router.urls)),
]
