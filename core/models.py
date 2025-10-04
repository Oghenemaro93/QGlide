import random
import re
import string
import time
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _

from core.helpers.func import generate_verification_code
from typing import Optional
from datetime import datetime
from django.utils import timezone


# Create your models here.
VEHICLE_STATUS = (
    ("ONLINE", "Online"),
    ("OFFLINE", "Offline"),
)

RIDE_TYPE = (
    ("ECONOMY", "Economy"),
    ("SUV", "SUV"),
    ("LUXURY", "Luxury"),
)

VEHICLE_TYPE = (
    ("RIDES", "Rides"),
    ("PACKAGE_DELIVERY", "Package Delivery"),
)


class BaseModel(models.Model):
    """Base model for reuse.
    Args:
        models (Model): Django's model class.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("date updated"), auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser, BaseModel):
    """User model."""

    USER_TYPE = [
        ("USER", "USER"),
        ("RIDER", "RIDER"),
    ]

    username = models.CharField(max_length=255, blank=False, null=True, unique=True)
    # email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    referral_code = models.CharField(max_length=255, blank=True, null=True)
    otp_code = models.CharField(max_length=128, blank=True, null=True)
    promotion_notification = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=255, blank=True, null=True, choices=USER_TYPE, default="USER"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=0)
    terms_and_conditions = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    country_code = models.CharField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]
    objects = UserManager()

    def __str__(self) -> str:
        return str(self.email)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "USER PROFILE"
        verbose_name_plural = "USER PROFILES"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def user_deleted(cls, phone_number):
        try:
            user = cls.objects.get(phone_number=phone_number)
        except cls.DoesNotExist:
            return None
        if user.is_deleted:
            return None
        else:
            return user
        
    @classmethod
    def user_email_deleted(cls, email):
        try:
            user = cls.objects.get(email=email)
        except cls.DoesNotExist:
            return None
        if user.is_deleted:
            return None
        else:
            return user

    @classmethod
    def user_exist(cls, phone_number):
        try:
            user = cls.objects.get(phone_number=phone_number)
        except cls.DoesNotExist:
            return None
        return user
    
    @classmethod
    def user_email_exist(cls, email):
        try:
            user = cls.objects.get(email=email)
        except cls.DoesNotExist:
            return None
        return user

    @classmethod
    def username_exist(cls, username):
        try:
            username = cls.objects.get(username=username)
        except cls.DoesNotExist:
            return False
        return True

    @classmethod
    def generate_username(
        cls,
    ):
        """Generate a random username of the specified length."""
        activities = [
            "lift",
            "run",
            "jump",
            "squat",
            "push",
            "stretch",
            "spin",
            "row",
            "kick",
            "punch",
        ]
        adjectives = [
            "strong",
            "fit",
            "power",
            "active",
            "dynamic",
            "vital",
            "flex",
            "endure",
            "peak",
            "solid",
        ]
        numbers = str(random.randint(1000, 9999))  # Generate a random 4-digit number

        activity = random.choice(activities)
        adjective = random.choice(adjectives)

        username = f"{adjective}_{activity}_{numbers}"
        return username

    @classmethod
    def add_username(
        cls,
    ):
        """Add a username to a user."""
        username = User.generate_username()
        while User.username_exist(username):
            username = User.generate_username()
        return username

    @classmethod
    def check_user_password(cls, user, password):
        return check_password(password, user.password)

    @classmethod
    def create_user_password(cls, user, password):
        hashed_password = make_password(password)
        user.password = hashed_password
        user.save()
        return user

    @classmethod
    def hash_otp(cls, user, otp_code):
        hashed_otp_code = make_password(otp_code)
        user.otp_code = hashed_otp_code
        user.save()
        return user

    @classmethod
    def check_otp(cls, user, otp_code):
        return check_password(otp_code, user.otp_code)


    @classmethod
    def is_phone_number_verified(cls, phone_number):
        user = cls.objects.filter(phone_number=phone_number).first()
        if user:
            if user.is_verified:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def format_phone_number(phone_number: str):
        if phone_number is None:
            return None

        if phone_number.startswith("234") and len(phone_number) == 13:
            return phone_number

        formatted_num = phone_number[-10:]
        if len(formatted_num) != 10 or formatted_num[0] == "0":
            return None
        else:
            return "234" + formatted_num
        
    @classmethod
    def is_email_verified(cls, email):
        user = cls.objects.filter(email=email).first()
        if user:
            if user.is_verified:
                return True
            else:
                return False
        else:
            return False

class ConstantTable(BaseModel):
    allow_registration = models.BooleanField(default=True)
    allow_vehicle_registration = models.BooleanField(default=True)
    country_code = models.CharField(null=True, blank=True)
    base_rate = models.FloatField(default=5.0)
    economy_kilometer_rate = models.FloatField(default=2.5)
    suv_kilometer_rate = models.FloatField(default=3.5)
    luxury_kilometer_rate = models.FloatField(default=4.0)
    time_based_rate = models.FloatField(default=0.5)
    peak_hour_rate = models.FloatField(default=1.5)
    peak_hours = models.JSONField(default={
        "1": {
            "start": "06:00",
            "end": "09:00",
        },
        "2": {
            "start": "17:00",
            "end": "20:00",
        },
    })
    package_delivery_rate = models.FloatField(default=1.0)
    duration_seconds = models.IntegerField(default=600)
    minimum_rate = models.FloatField(default=10.0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "CONSTANT TABLE"
        verbose_name_plural = "CONSTANT TABLES"

    @classmethod
    def constant_table_instance(cls, country_code):
        """
        This function always returns an instance of the constant table
        """
        # Try to retrieve the cached data
        constant_instance = cls.objects.filter(country_code=country_code).last()
        if constant_instance is None:
            # If the cache is empty, create a new instance
            constant_instance = cls.objects.create(
                country_code=country_code
            )
        return constant_instance
    
    @classmethod
    def is_peak_hour(cls, peak_hours, current_time):
        # get current local time with timezone
        now = current_time

        for period in peak_hours.values():
            start = datetime.strptime(period["start"], "%H:%M").time()
            end = datetime.strptime(period["end"], "%H:%M").time()

            # normal case: start < end
            if start <= now <= end:
                return True

            # handle crossing midnight (e.g., 23:00 - 02:00)
            if start > end and (now >= start or now <= end):
                return True

        return False
    
    @classmethod
    def calculate_fare(
        cls, 
        country_code: str, 
        ride_type: str, 
        distance: float, 
        duration: int, 
        is_peak_hours: bool, 
        points: Optional[int] = 0, 
        is_delivery: Optional[bool] = False, 
        package_weight: Optional[float] = 0
    ):
        country_constants = cls.constant_table_instance(cls, country_code)
        if ride_type == "ECONOMY":
            kilometer_rate = country_constants.economy_kilometer_rate
        elif ride_type == "SUV":
            kilometer_rate = country_constants.suv_kilometer_rate
        else:
            kilometer_rate = country_constants.luxury_kilometer_rate

        total_fare = 0  
        total_fare += country_constants.base_rate
        total_fare += kilometer_rate * distance
        if duration > country_constants.duration_seconds:
            total_fare += country_constants.time_based_rate * (distance/60)
        if is_peak_hours:
            total_fare += country_constants.peak_hour_rate
        if is_delivery:
            total_fare += country_constants.package_delivery_rate * package_weight
        
        if total_fare >= total_fare:
            total_fare = total_fare
        else:
            total_fare = total_fare

        if points > 0:
            if total_fare >= points:
                point_discount = total_fare - points
                point_deducted = True
                points_left = 0
            else:
                point_discount = total_fare
                point_deducted = True
                points_left = point_discount - total_fare
        else:
            point_discount = 0
            point_deducted = False
            points_left = 0

        return total_fare, point_discount, point_deducted, points_left
    

class VehicleSettings(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    ride_type = models.CharField(
        max_length=255, blank=True, null=True, choices=RIDE_TYPE
    )
    vehicle_type = models.CharField(max_length=50, blank=True, null=True, choices=VEHICLE_TYPE)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "VEHICLE SETTING"
        verbose_name_plural = "VEHICLE SETTINGS"


class VehicleRegistration(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicle_owner", null=True, blank=True
    )
    vehicle_make = models.CharField(max_length=255, null=True, blank=True)
    vehichle_type = models.ForeignKey(
        VehicleSettings, on_delete=models.CASCADE, related_name="vehicle_registration_type", null=True, blank=True
    )
    vehicle_model = models.CharField(max_length=255, null=True, blank=True)
    vehicle_plate_number = models.CharField(max_length=255, null=True, blank=True)
    vehicle_color = models.CharField(max_length=255, null=True, blank=True)
    vehicle_year = models.CharField(max_length=255, null=True, blank=True)
    vehicle_seat_number = models.PositiveIntegerField(null=True, blank=True)
    vehicle_status = models.CharField(max_length=50, choices=VEHICLE_STATUS, default="NONE")
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "VEHICLE REGISTRATION"
        verbose_name_plural = "VEHICLE REGISTRATIONS"