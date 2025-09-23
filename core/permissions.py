from rest_framework import permissions, status
from rest_framework.exceptions import APIException

from ride.models import Ride


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


class AlreadyStartedRide(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "status": False,
        "message": "user has already started a ride",
    }
    default_code = "Not permitted"


class NoOpenRide(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "status": False,
        "message": "user has no open ride",
    }
    default_code = "Not permitted"

class NoAcceptedRide(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        "status": False,
        "message": "user has no available ride to cancel",
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
    

class UserHasActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(user=request.user, is_completed=False).first()
        if opened_ride:
            raise AlreadyStartedRide()
        return True
    
class UserHasNoActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(user=request.user, ride_status="PENDING", is_completed=False).first()
        if opened_ride is None:
            raise NoOpenRide()
        return True
    
class CancelUserActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(user=request.user, ride_status__in=["ACCEPTED", "WAITING"], is_completed=False).first()
        if opened_ride is None:
            raise NoAcceptedRide()
        return True
    
class AcceptedRiderActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(driver=request.user, ride_status__in=["ACCEPTED", "WAITING"], is_completed=False).first()
        if opened_ride is None:
            raise NoAcceptedRide()
        return True
    

class WaitingRiderActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="ACCEPTED", is_completed=False).first()
        if opened_ride is None:
            raise NoAcceptedRide()
        return True
    

class StartRiderActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="WAITING", is_completed=False).first()
        if opened_ride is None:
            raise NoAcceptedRide()
        return True
    

class EndRiderActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="RIDE_START", is_completed=False).first()
        if opened_ride is None:
            raise NoAcceptedRide()
        return True
    

class CashPaymentActiveRide(permissions.BasePermission):

    def has_permission(self, request, view):

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="RIDE_END", is_completed=False).first()
        if opened_ride is None:
            raise NoAcceptedRide()
        return True
