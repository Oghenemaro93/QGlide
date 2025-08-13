from rest_framework import permissions, status
from rest_framework.exceptions import APIException


class UserIsDeleted(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "status": False,
        "message": "user account does not exist",
    }
    default_code = "Not permitted"


class UserNotVerified(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "status": False,
        "message": "please verify your account",
    }
    default_code = "Not permitted"


class UserIsSuspended(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "status": False,
        "message": "user has been suspended, please contact support",
    }
    default_code = "Not permitted"


class UserIsActive(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_deleted is True:
            raise UserIsDeleted()
        if request.user.is_suspended is True or request.user.is_active is False:
            raise UserIsSuspended()
        if request.user.is_verified is False:
            raise UserNotVerified()

        return True
