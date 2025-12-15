from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Home Page")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),

    # DRF Users API
    path("api/user/", include("users.urls")),
]
