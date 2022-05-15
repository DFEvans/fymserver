from django.urls import path

from . import views

app_name = "players"

urlpatterns = [
    path("uuid", views.uuid, name="uuid"),
    path("send_auth_code", views.send_auth_code, name="send_auth_code"),
]
