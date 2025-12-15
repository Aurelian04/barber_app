from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MeView, UserAdminViewSet

router = DefaultRouter()
router.register('admin/users', UserAdminViewSet, basename='user-admin')

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("me/", MeView.as_view()),
    path("", include(router.urls)),
]
