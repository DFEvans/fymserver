from django.contrib import admin

from .models import Player


# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["username", "email"]}),
    ]
    readonly_fields = ("id", "token")


admin.site.register(Player, PlayerAdmin)
