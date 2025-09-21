from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

from . import resources
from .models import (

    ConstantTable,
    User,
    VehicleRegistration,
    VehicleSettings,
)
# Register your models here.

@admin.register(LogEntry)
class LogEntryAdmin(ImportExportModelAdmin):
    date_hierarchy = "action_time"

    list_filter = ["user", "content_type", "action_flag"]

    search_fields = ["object_repr", "change_message"]

    list_display = [
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_flag",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse(
                    "admin:%s_%s_change" % (ct.app_label, ct.model),
                    args=[obj.object_id],
                ),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    # object_link.admin_order_field = "object_repr"
    # object_link.short_description = "object"


class UserResourceAdmin(ImportExportModelAdmin):
    resource_class = resources.UserResource
    search_fields = ["phone_number", "first_name", "last_name"]
    list_filter = ["is_superuser", "is_staff", "terms_and_conditions"]
    list_display = (
        "id",
        "is_superuser",
        "is_staff",
        "username",
        "is_active",
        "is_verified",
        "is_deleted",
        "is_suspended",
        "phone_number",
        "first_name",
        "last_name",
        "referral_code",
        "promotion_notification",
        "terms_and_conditions",
        "referral_code",
        "ip_address",
        "created_at",
        "updated_at",
    )


class ConstantTableResourceAdmin(ImportExportModelAdmin):
    resource_class = resources.ConstantTableResource

    list_display = (
        "id",
        "allow_registration",
        "allow_vehicle_registration",
        "created_at",
        "updated_at",
    )


class VehicleSettingsResourceAdmin(ImportExportModelAdmin):
    resource_class = resources.VehicleSettingsResource

    search_fields = ["ride_type"]
    list_filter = ["is_active"]
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]


class VehicleRegistrationResourceAdmin(ImportExportModelAdmin):
    resource_class = resources.VehicleRegistrationResource

    search_fields = ["user__phone", "vehicle_make", "vehicle_model", "vehicle_plate_number"]
    list_filter = ["is_approved", "is_active", "is_deleted"]
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]


admin.site.register(User, UserResourceAdmin)
admin.site.register(ConstantTable, ConstantTableResourceAdmin)
admin.site.register(VehicleSettings, VehicleSettingsResourceAdmin)
admin.site.register(VehicleRegistration, VehicleRegistrationResourceAdmin)