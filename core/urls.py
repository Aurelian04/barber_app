from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def home(request):
    return HttpResponse("Welcome to the Home Page")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("api-auth/", include("rest_framework.urls")),
    
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # DRF Users API
    path("api/user/", include("users.urls")),
    path("api/", include("services.urls")),
    path("api/", include("appointments.urls")),
    path("api/", include("availability.urls")),
]
