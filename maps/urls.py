from django.urls import path

from . import views

app_name = "maps"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/jpg_file", views.jpg_file, name="jpg_file"),
    path("<int:pk>/yrd_file", views.yrd_file, name="yrd_file"),
    path("<int:pk>/his_file", views.his_file, name="his_file"),
    path("<int:pk>/modified_date", views.modified_date, name="modified_date"),
    path("<int:pk>/jpg_file/update", views.update_jpg_file, name="update_jpg_file"),
    path("<int:pk>/yrd_file/update", views.update_yrd_file, name="update_yrd_file"),
    path("<int:pk>/his_file/update", views.update_his_file, name="update_his_file"),
    path(
        "<int:pk>/modified_date/update",
        views.update_modified_date,
        name="update_modified_date",
    ),
]
