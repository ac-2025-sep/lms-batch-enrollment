from django.urls import include, path

from . import views

urlpatterns = [
    path("userops/", views.dashboard, name="userops-dashboard"),
    path("api/userops/v1/", include("userops.urls_api")),
]
