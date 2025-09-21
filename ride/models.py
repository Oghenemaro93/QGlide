from django.db import models

from core.models import RIDE_TYPE, VEHICLE_TYPE, BaseModel, User, VehicleRegistration
from django.core.validators import MinValueValidator


# Create your models here.

RIDE_STATUS = (
    ("PENDING", "Pending"),
    ("ACCEPTED", "Accepted"),
    ("WAITING", "Waiting"),
    ("PICKUP", "Pickup"),
    ("RIDE_END", "Ride End"),
    ("PAID", "Paid"),
    ("COMPLETED", "Completed"),
    ("CANCELLED", "Cancelled"),
)

RIDE_DISTANCE_UNIT = (
    ("MILES", "Mi"),
    ("KILOMETERS", "KM"),
    ("METERS", "M"),
)

CANCELLED_BY = (
    ("RIDER", "Rider"),
    ("USER", "User"),
    ("NONE", "None"),
)

RIDE_RATING = (
    ("ONE", "1"),
    ("TWO", "2"),
    ("THREE", "3"),
    ("FOUR", "4"),
    ("FIVE", "5"),
    ("NONE", "None"),   
)

class Ride(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ride_user", null=True, blank=True
    )
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ride_driver", null=True, blank=True)

    driver_pickup_longitude = models.FloatField(null=True, blank=True)
    driver_pickup_latitude = models.FloatField(null=True, blank=True)
    driver_pickup_address = models.CharField(max_length=255, null=True, blank=True)

    user_pickup_longitude = models.FloatField(null=True, blank=True)
    user_pickup_latitude = models.FloatField(null=True, blank=True)
    user_pickup_address = models.CharField(max_length=255, null=True, blank=True)

    user_location_longitude = models.FloatField(null=True, blank=True)
    user_location_latitude = models.FloatField(null=True, blank=True)
    user_location_address = models.CharField(max_length=255, null=True, blank=True)

    user_ride_end_longitude = models.FloatField(null=True, blank=True)
    user_ride_end_latitude = models.FloatField(null=True, blank=True)
    user_ride_end_address = models.CharField(max_length=255, null=True, blank=True)

    driver_ride_end_longitude = models.FloatField(null=True, blank=True)
    driver_ride_end_latitude = models.FloatField(null=True, blank=True)
    driver_ride_end_address = models.CharField(max_length=255, null=True, blank=True)

    ride_distance = models.FloatField(null=True, blank=True)
    ride_distance_unit = models.CharField(max_length=50, choices=RIDE_DISTANCE_UNIT, default="MILES")
    
    vehicle = models.ForeignKey(
        VehicleRegistration, on_delete=models.CASCADE, related_name="ride_vehicle", null=True, blank=True
    )
    ride_type = models.CharField(max_length=255, blank=True, null=True, choices=RIDE_TYPE)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True, choices=VEHICLE_TYPE)

    ride_start_time = models.DateTimeField(null=True, blank=True)
    ride_end_time = models.DateTimeField(null=True, blank=True)
    ride_duration = models.DurationField(null=True, blank=True)

    ride_status = models.CharField(max_length=50, choices=RIDE_STATUS, default="PENDING")

    price = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )
    discount_amount = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )
    discount_amount = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )
    payable_amount = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )
    cancellation_amount = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )

    cancelled_by = models.CharField(max_length=50, choices=CANCELLED_BY, default="NONE")
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.CharField(max_length=255,  null=True, blank=True)

    ride_rating = models.FloatField(null=True, choices=RIDE_RATING, default="NONE")
    rating = models.PositiveIntegerField(default=0)
    ride_feedback = models.TextField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    class Meta:
        oordering = ["-created_at"]
        verbose_name = "VEHICLE REGISTRATION"
        verbose_name_plural = "VEHICLE REGISTRATIONS"
    
    @classmethod
    def fetch_ride_status(cls, user):
        create_ride = cls.objects.filter(user=user, is_completed=False).first()
        if create_ride:
            return create_ride
        return None