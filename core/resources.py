from import_export import resources

from . import models


class UserResource(resources.ModelResource):
    class Meta:
        model = models.User