from rest_framework import exceptions, serializers
from rest_framework.exceptions import APIException

from core.models import ConstantTable, VehicleRegistration
from core.serializer import CustomSerializerError, DriverPrimaryKeyRelatedField, ModelCustomSerializer
from ride.models import Ride
from haversine import haversine, Unit
from django.utils import timezone


class CreateRideSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "user",
            "user_location_longitude",
            "user_location_latitude",
            "user_location_address",
            "user_pickup_longitude",
            "user_pickup_latitude",
            "user_pickup_address",
            "user_ride_end_longitude",
            "user_ride_end_latitude",
            "user_ride_end_address",
            "vehicle_type",
            "ride_type",
            "ride_distance",
            "ride_distance_unit",
            "payment_method",
            "price",
        )
        extra_kwargs = {
            "user_location_longitude": {"required": True},
            "user_location_latitude": {"required": True},
            "user_location_address": {"required": True},
            "user_pickup_longitude": {"required": True},
            "user_pickup_latitude": {"required": True},
            "user_pickup_address": {"required": True},
            "user_ride_end_longitude": {"required": True},
            "user_ride_end_latitude": {"required": True},
            "user_ride_end_address": {"required": True},
            "vehicle_type": {"required": True},
            "ride_type": {"required": True},
            "payment_method": {"required": True},
        }

    def validate(self, attrs):

        user_pickup_longitude = attrs.get("user_pickup_longitude")
        user_pickup_latitude = attrs.get("user_pickup_latitude")
        user_ride_end_longitude = attrs.get("user_ride_end_longitude")
        user_ride_end_latitude = attrs.get("user_ride_end_latitude")

        distance = haversine(
            (user_pickup_latitude, user_pickup_longitude),
            (user_ride_end_latitude, user_ride_end_longitude),
            unit=Unit.KILOMETERS
        )
        attrs["ride_distance"] = distance
        attrs["ride_distance_unit"] = Unit.KILOMETERS
        return attrs


class RideStatusSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "user",
            "driver",

            # where user initaied the booking
            "user_location_longitude",
            "user_location_latitude",
            "user_location_address",

            # where user wants to be picked up
            "user_pickup_longitude",
            "user_pickup_latitude",
            "user_pickup_address",

            # where user is going to
            "user_ride_end_longitude",
            "user_ride_end_latitude",
            "user_ride_end_address",

            # where user was waiting for pickup
            "driver_waiting_longitude",
            "driver_waiting_latitude",
            "driver_waiting_address",
            
            # where user was picked up
            "driver_pickup_longitude",
            "driver_pickup_latitude",
            "driver_pickup_address",

            # where driver dropped the user
            "driver_ride_end_longitude",
            "driver_ride_end_latitude",
            "driver_ride_end_address",

            "ride_type",
            "vehicle_type",
            "ride_status",

            "ride_distance",
            "ride_distance_unit",
            
            "vehicle",

            "ride_start_time",
            "ride_end_time",
            "ride_duration",


            "price",
            "discount_amount",
            "discount_amount",
            "payable_amount",
            "cancellation_amount",

            "cancelled_by",
            "cancelled_reason",
            
            "cancelled_at",
            "waiting_at",

            "payment_method",

            "rating",
            "ride_feedback",

            "payment_method",
            
            "is_paid",
            "is_completed",
        )


class AcceptRideSerializer(ModelCustomSerializer):
    driver = DriverPrimaryKeyRelatedField(
        queryset=VehicleRegistration.objects.filter(vehicle_status="ONLINE", is_active=True)
    )
    class Meta:
        model = Ride
        fields = (
            "id",
            "driver",
            "ride_status",
        )

    def validate(self, attrs):
        driver = attrs.get("driver")
        if Ride.objects.filter(driver=driver.user, is_completed=False).exists():
            raise CustomSerializerError(
                {"status": False, "messgae": "Rider already has an open Ride"}
            )
        attrs["ride_status"] = "ACCEPTED"
        return attrs
    
    
class CancelUserRideSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "id",
            "ride_status",
            "cancelled_by",
            "cancelled_at",
            "cancelled_reason",
            "is_completed",
        )

        extra_kwargs = {
            "cancelled_reason": {"required": True},
        }

    def validate(self, attrs):
        attrs["ride_status"] = "CANCELLED"
        attrs["cancelled_at"] = timezone.now()
        attrs["cancelled_by"] = "USER"
        attrs["is_completed"] = True
        return attrs
    

class CancelRiderRideSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "id",
            "ride_status",
            "cancelled_by",
            "cancelled_at",
            "cancelled_reason",
        )

        extra_kwargs = {
            "cancelled_reason": {"required": True},
        }

    def validate(self, attrs):
        attrs["ride_status"] = "CANCELLED"
        attrs["cancelled_at"] = timezone.now()
        attrs["cancelled_by"] = "RIDER"
        attrs["is_completed"] = True
        return attrs
    

class WaitingRideSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "driver_waiting_longitude",
            "driver_waiting_latitude",
            "driver_waiting_address",
        )
        extra_kwargs = {
            "driver_waiting_longitude": {"required": True},
            "driver_waiting_latitude": {"required": True},
            "driver_waiting_address": {"required": True},
        }
    def validate(self, attrs):
        attrs["ride_status"] = "WAITING"
        attrs["waiting_at"] = timezone.now()
        return attrs
    


class StartRideSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "driver_pickup_longitude",
            "driver_pickup_latitude",
            "driver_pickup_address",
        )
        extra_kwargs = {
            "driver_pickup_longitude": {"required": True},
            "driver_pickup_latitude": {"required": True},
            "driver_pickup_address": {"required": True},
        }
    def validate(self, attrs):
        attrs["ride_status"] = "RIDE_START"
        attrs["ride_start_time"] = timezone.now()
        return attrs
    
    
class EndRideSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "driver_ride_end_longitude",
            "driver_ride_end_latitude",
            "driver_ride_end_address",
        )
        extra_kwargs = {
            "driver_ride_end_longitude": {"required": True},
            "driver_ride_end_latitude": {"required": True},
            "driver_ride_end_address": {"required": True},
        }
    def validate(self, attrs):
        attrs["ride_status"] = "RIDE_END"
        attrs["ride_end_time"] = timezone.now()
        return attrs


class CashPaymentSerializer(ModelCustomSerializer):
    class Meta:
        model = Ride
        fields = (
            "is_paid",
        )
        extra_kwargs = {
            "is_paid": {"required": True},
        }
    def validate(self, attrs):
        payment_is_paid = attrs.get("is_paid")
        if payment_is_paid is False:
            raise CustomSerializerError(
                {"status": False, "messgae": "Payment Incomplete"}
            )
        attrs["ride_status"] = "PAID"
        attrs["payment_method"] = "CASH"
        attrs["is_completed"] = True
        attrs["payment_at"] = timezone.now()
        return attrs