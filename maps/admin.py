from django.contrib import admin

from .models import Map


# Register your models here.
class MapAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["id", "modified_date"]}),
        ("Files", {"fields": ["jpg_file", "yrd_file", "his_file"]}),
    ]


admin.site.register(Map, MapAdmin)
