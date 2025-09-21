from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from . import resources
from .models import (
    Ride
)
# Register your models here.

class RideResourceAdmin(ImportExportModelAdmin):
    resource_class = resources.RideResource

    # search_fields = ["ride_type"]
    # list_filter = ["is_active"]
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    


admin.site.register(Ride, RideResourceAdmin)