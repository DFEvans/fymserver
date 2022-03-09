from django.contrib import admin

from .models import Player


# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["id", "username"]}),
    ]


admin.site.register(Player, PlayerAdmin)
