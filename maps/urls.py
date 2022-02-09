from django.urls import path

from . import views

app_name = "maps"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/jpg_file/", views.jpg_file, name="jpg_file"),
    path("<int:pk>/yrd_file/", views.yrd_file, name="yrd_file"),
    path("<int:pk>/his_file/", views.his_file, name="his_file"),
    path("<int:pk>/modified_date/", views.modified_date, name="modified_date"),
]
