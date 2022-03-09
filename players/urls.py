from django.urls import path

from . import views

app_name = "players"

urlpatterns = [
    path("uuid", views.uuid, name="uuid"),
]
