from django.contrib import admin

# Register your models here.
from .models import Train


# Register your models here.
class TrainAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "from_player",
                    "to_player",
                    "downloaded_by",
                    "upload_date",
                    "state",
                ]
            },
        ),
        ("Files", {"fields": ["train_file"]}),
    ]


admin.site.register(Train, TrainAdmin)
