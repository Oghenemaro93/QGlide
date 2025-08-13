from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import transaction
from rest_framework import exceptions, serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.helpers.func import (
    generate_verification_code,
)
from core.models import ConstantTable, VehicleRegistration, VehicleSettings

User = get_user_model()


class CustomSerializerError(APIException):
    status_code = 400  # You can customize the status code
    default_detail = {"message": "an error occurred"}
    default_code = "authentication_failed"

    def __init__(self, detail=None, code=None):
        # Use the provided detail if present, otherwise fallback to default_detail
        if detail is None:
            detail = self.default_detail
        super().__init__(detail, code)


class CustomSerializer(serializers.Serializer):

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            # Convert lists of errors into single strings
            exc.detail = self._convert_error_lists_to_strings(exc.detail)
            raise exc

    def _convert_error_lists_to_strings(self, errors):
        """Recursively convert lists of errors with a single string to just a string."""
        if isinstance(errors, dict):
            for key, value in errors.items():
                errors[key] = self._convert_error_lists_to_strings(value)
        elif isinstance(errors, list) and len(errors) == 1:
            return errors[0]
        return errors
    

class ModelCustomSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            # Convert lists of errors into single strings
            exc.detail = self._convert_error_lists_to_strings(exc.detail)
            raise exc

    def _convert_error_lists_to_strings(self, errors):
        """Recursively convert lists of errors with a single string to just a string."""
        if isinstance(errors, dict):
            for key, value in errors.items():
                errors[key] = self._convert_error_lists_to_strings(value)
        elif isinstance(errors, list) and len(errors) == 1:
            return errors[0]
        return errors


class VehiclePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    default_error_messages = {
        "does_not_exist": "Please provide a valid Category ID.",
        "incorrect_type": "Incorrect type. Expected a valid Category ID, but got {data_type}.",
    }

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        phone_number = attrs[self.username_field]

        authenticate_kwargs = {
            self.username_field: phone_number,
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
            authenticate_kwargs["phone_number"] = authenticate_kwargs["phone_number"]
        except KeyError:
            pass
        """
            Checking if the user exists by getting the phone_number(username field) from authentication_kwargs.
            If the user exists we check if the user account is active.
            If the user account is not active we raise the exception and pass the message.
            Thus stopping the user from getting authenticated altogether.

            And if the user does not exist at all we raise an exception with a different error message.
            Thus stopping the execution right there.
        """
        if not authenticate_kwargs["password"].digits():
            raise CustomSerializerError(
                {"status": False, "password": "password must contain only digits."}
            )
        if not len(authenticate_kwargs["password"]) == 6:
            raise CustomSerializerError(
                {"status": False, "password": f"password must be 6 digits."}
            )
        try:
            user = User.objects.get(phone_number=authenticate_kwargs["phone_number"])
            authenticate_kwargs["phone_number"] = user.phone_number

            if not user.password:
                self.error_messages["no_password"] = (
                    "please create a password for login!"
                )
                raise exceptions.AuthenticationFailed(
                    self.error_messages["no_password"],
                )
            self.user = authenticate(
                phone_number=user.phone_number, password=authenticate_kwargs["password"]
            )
            if self.user is None:
                self.error_messages["no_active_account"] = "invalid login credentials!"
                raise exceptions.AuthenticationFailed(
                    self.error_messages["no_active_account"],
                )

            if user.is_deleted is True:
                self.error_messages["error"] = "account does not exist!"
                raise exceptions.AuthenticationFailed(self.error_messages["error"])

            if user.is_suspended is True:
                self.error_messages["error"] = "account suspended! contact admin."
                raise exceptions.AuthenticationFailed(self.error_messages["error"])

            if user.is_verified is False:
                self.error_messages["error"] = (
                    "please verify your account!"
                )
                raise exceptions.AuthenticationFailed(self.error_messages["error"])

            if user.is_active is False:
                self.error_messages["error"] = "account disabled! contact admin."
                raise exceptions.AuthenticationFailed(self.error_messages["error"])

        except User.DoesNotExist:
            self.error_messages["no_active_account"] = "account does not exist!"
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
            )

        update_last_login(None, user)
        all_data = super().validate(attrs)

        this_user = {
            "access": all_data["access"],
            "refresh": all_data["refresh"],
            "user_type": user.user_type,
        }
        return this_user


class RegistrationSerializer(ModelCustomSerializer):
    """Serializers registration requests and creates a new user."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "ip_address",
            "referral_code",
            "confirm_password",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "user_type": {"required": True},
        }

    def validate(self, attrs):
        constant_data = ConstantTable.constant_table_instance()
        if constant_data.allow_registration is False:
            raise CustomSerializerError(
                {"status": False, "message": "Registration is temporarily unavailable"}
            )
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        phone_number = attrs.get("phone_number")

        if not password.digits():
            raise CustomSerializerError(
                {"status": False, "password": "password must contain only digits."}
            )
        if not len(password) == 6:
            raise CustomSerializerError(
                {"status": False, "password": f"password must be 6 digits."}
            )
        if password != confirm_password:
            raise CustomSerializerError(
                {"status": False, "password": "passwords do not match."}
            )
        if User.user_deleted(phone_number=phone_number):
            raise CustomSerializerError(
                {"status": False, "phone_number": f"{phone_number} has been used, try another phone_number"}
            )
        if User.user_exist(phone_number=phone_number):
            raise CustomSerializerError(
                {"status": False, "phone_number": f"{phone_number} is associated with another account"}
            )
        # correct_phone_number = User.format_phone_number(phone_number)
        # if correct_phone_number is None:
        #     raise CustomSerializerError(
        #         {"status": False, "phone_number": "invalid phone number"}
        #     )
        
        attrs["password"] = make_password(password)
        del attrs["confirm_password"]
        verification_code = generate_verification_code()
        attrs["otp_code"] = make_password(verification_code)
        attrs["un_hashed_otp_code"] = verification_code
        attrs["phone_number"] = phone_number
        attrs["is_active"] = True
        return attrs
    
    
class LoginView(TokenObtainPairView):
    """Log in a user."""

    serializer_class = CustomTokenObtainSerializer


class VehicleRegistrationSerializer(ModelCustomSerializer):
    """Serializers registration requests and creates a new user vehicle"""
    vehichle_type = VehiclePrimaryKeyRelatedField(
        queryset=VehicleSettings.objects.filter(is_active=True)
    )
    class Meta:
        model = VehicleRegistration
        fields = (
            "vehicle_make",
            "vehichle_type",
            "vehicle_model",
            "vehicle_plate_number",
            "vehicle_color",
            "vehicle_year",
            "vehicle_seat_number",
        )
        extra_kwargs = {
            "vehicle_make": {"required": True},
            "vehicle_model": {"required": True},
            "vehicle_plate_number": {"required": True},
            "vehicle_year": {"required": True},
            "vehicle_seat_number": {"required": True},
        }

    def validate(self, attrs):
        user = self.context.get("user")
        previous_vehicle = VehicleRegistration.objects.filter(user=user, is_deleted=False)
        constant_data = ConstantTable.constant_table_instance()
        if constant_data.allow_vehicle_registration is False:
            raise CustomSerializerError(
                {"status": False, "message": "Vehicle Registration is temporarily unavailable"}
            )
        vehicle_make = attrs.get("vehicle_make")
        vehicle_model = attrs.get("vehicle_model")
        vehicle_plate_number = attrs.get("vehicle_plate_number")
        vehicle_color = attrs.get("vehicle_color")

        attrs["vehicle_make"] = vehicle_make.title()
        attrs["vehicle_model"] = vehicle_model.title()
        attrs["vehicle_plate_number"] = vehicle_plate_number.upper()
        attrs["vehicle_color"] = vehicle_color.title()
        if previous_vehicle.exists():
            attrs["previous_vehicle"] = previous_vehicle

        return attrs
    

class FetchVehicleTypeSerializer(ModelCustomSerializer):
    """Serializers Fetch Brand for all Users."""

    class Meta:
        model = VehicleSettings
        fields = (
            "id",
            "name",
            "base_fare",
            "base_distance",
            "waiting_charge",
            "is_active",
        )


class FetchVehicleRegistrationSerializer(ModelCustomSerializer):
    """Serializers Fetch Brand for all Users."""

    class Meta:
        model = VehicleRegistration
        fields = (
            "id",
            "user",
            "vehicle_make",
            "vehichle_type",
            "vehicle_model",
            "vehicle_plate_number",
            "vehicle_color",
            "vehicle_year",
            "vehicle_seat_number",
            "is_approved",
            "is_active",
            "is_deleted",
            "created_at",
        )


class FetchVehicleRegistrationAdminSerializer(ModelCustomSerializer):
    """Serializers Fetch Brand for all Users."""

    class Meta:
        model = VehicleRegistration
        fields = (
            "id",
            "user",
            "vehicle_make",
            "vehichle_type",
            "vehicle_model",
            "vehicle_plate_number",
            "vehicle_color",
            "vehicle_year",
            "vehicle_seat_number",
            "is_approved",
            "is_active",
            "is_deleted",
            "created_at",
            "deleted_at",
            "updated_at",
        )