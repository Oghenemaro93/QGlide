from import_export import resources

from . import models


class UserResource(resources.ModelResource):
    class Meta:
        model = models.User


class ConstantTableResource(resources.ModelResource):
    class Meta:
        model = models.ConstantTable


class VehicleSettingsResource(resources.ModelResource):
    class Meta:
        model = models.VehicleSettings


class VehicleRegistrationResource(resources.ModelResource):
    class Meta:
        model = models.VehicleRegistration