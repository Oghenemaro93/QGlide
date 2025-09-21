from import_export import resources

from . import models

class RideResource(resources.ModelResource):
    class Meta:
        model = models.Ride