from django.urls import path

from . import views

app_name = "players"

urlpatterns = [
    path("send_auth_code", views.send_auth_code, name="send_auth_code"),
    path("check_auth_code", views.check_auth_code, name="check_auth_code"),
]
