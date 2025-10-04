from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import exceptions, serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework.exceptions import AuthenticationFailed
from drf_yasg.utils import swagger_auto_schema

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


class DriverPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    default_error_messages = {
        "does_not_exist": "Please provide a valid Driver ID.",
        "incorrect_type": "Incorrect type. Expected a valid Driver ID, but got {data_type}.",
    }

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    user_type = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        # Validate user_type
        user_type = attrs.get("user_type")
        if user_type not in ["USER", "RIDER"]:
            raise CustomSerializerError(
                {"status": False, "user_type": "Invalid User Type. Must be 'USER' or 'RIDER'"}
            )
        
        # Normalize email to avoid case-sensitivity issues during auth
        email = attrs[self.username_field]
        if isinstance(email, str):
            email = email.lower()
            attrs[self.username_field] = email

        authenticate_kwargs = {
            self.username_field: email,
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
            authenticate_kwargs["email"] = authenticate_kwargs["email"]
        except KeyError:
            pass
        """
            Checking if the user exists by getting the email(username field) from authentication_kwargs.
            If the user exists we check if the user account is active.
            If the user account is not active we raise the exception and pass the message.
            Thus stopping the user from getting authenticated altogether.

            And if the user does not exist at all we raise an exception with a different error message.
            Thus stopping the execution right there.
        """
        # if not authenticate_kwargs["password"].digit():
        #     raise CustomSerializerError(
        #         {"status": False, "password": "password must contain only digits."}
        #     )
        # if not len(authenticate_kwargs["password"]) == 6:
        #     raise CustomSerializerError(
        #         {"status": False, "password": f"password must be 6 digits."}
        #     )
        try:
            user = User.objects.get(email=authenticate_kwargs["email"].lower())
            
            # Validate user_type matches the user's actual user_type
            if user.user_type != user_type:
                self.error_messages["no_active_account"] = "account does not exist!"
                raise exceptions.AuthenticationFailed(
                    self.error_messages["no_active_account"],
                )

            if not user.password:
                self.error_messages["no_password"] = (
                    "please create a password for login!"
                )
                raise exceptions.AuthenticationFailed(
                    self.error_messages["no_password"],
                )
            self.user = authenticate(
                username=user.email, password=authenticate_kwargs["password"]
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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "country_code": user.country_code
        }
        return this_user


class RegistrationSerializer(ModelCustomSerializer):
    """Serializers registration requests and creates a new user."""
    confirm_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    country_code = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "email",
            "ip_address",
            "referral_code",
            "confirm_password",
            "user_type",
            "country_code"
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "email": {"required": True},
            "user_type": {"required": True},
            "country_code": {"required": True},
        }

    def validate(self, attrs):
        user_type = attrs.get("user_type")
        if user_type not in ["USER", "RIDER"]:
            raise CustomSerializerError(
                {"status": False, "user_type": "Invalid User Type"}
            )
        country_code = attrs.get("country_code")
        if not country_code:
            raise CustomSerializerError(
                {"status": False, "country_code": "Country Code is Required"}
            )
        # Require leading '+' and at least 1 digit after
        if not isinstance(country_code, str) or not country_code.startswith("+") or not country_code[1:].isdigit():
            raise CustomSerializerError(
                {"status": False, "country_code": "Country code must start with '+' and contain digits only"}
            )
        constant_data = ConstantTable.constant_table_instance(country_code=country_code)
        if constant_data.allow_registration is False:
            raise CustomSerializerError(
                {"status": False, "message": "Registration is temporarily unavailable"}
            )
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        phone_number = attrs.get("phone_number")
        email = attrs.get("email")

        # Basic password strength checks
        if not isinstance(password, str) or len(password) < 8:
            raise CustomSerializerError(
                {"status": False, "password": "Password must be at least 8 characters"}
            )
        if password.isdigit() or password.isalpha():
            raise CustomSerializerError(
                {"status": False, "password": "Password must include letters and numbers"}
            )

        # Check for existing users (including deleted ones)
        existing_user_phone = User.user_exist(phone_number=phone_number)
        if existing_user_phone is not None:
            # If user exists and is deleted, allow re-registration
            if existing_user_phone.is_deleted:
                # User is deleted, allow re-registration by deleting the old record
                existing_user_phone.delete()
            else:
                # User exists and is not deleted, prevent registration
                raise CustomSerializerError(
                    {"status": False, "phone_number": f"{phone_number} is associated with another account"}
                )
        
        # Check for existing users by email (including deleted ones)
        existing_user_email = User.user_email_exist(email=email)
        if existing_user_email is not None:
            # If user exists and is deleted, allow re-registration
            if existing_user_email.is_deleted:
                # User is deleted, allow re-registration by deleting the old record
                existing_user_email.delete()
            else:
                # User exists and is not deleted, prevent registration
                raise CustomSerializerError(
                    {"status": False, "email": f"{email} is associated with another account"}
                )
        
        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            raise CustomSerializerError(
                {"status": False, "email": "Invalid email format"}
            )
        
        if password != confirm_password:
            raise CustomSerializerError(
                {"status": False, "password": "passwords do not match."}
            )
        correct_phone_number = User.format_phone_number(phone_number)
        if correct_phone_number is None:
            raise CustomSerializerError(
                {"status": False, "phone_number": "invalid phone number"}
            )
        
        attrs["password"] = make_password(password)
        del attrs["confirm_password"]
        verification_code = generate_verification_code()
        attrs["otp_code"] = make_password(verification_code)
        attrs["un_hashed_otp_code"] = verification_code
        attrs["phone_number"] = correct_phone_number
        attrs["is_active"] = True
        return attrs
    
    def create(self, validated_data):
        """Create user and return user-friendly errors on unique conflicts."""
        from django.db import IntegrityError
        try:
            return User.objects.create(**validated_data)
        except IntegrityError as exc:
            error_text = str(exc)
            if "core_user_email_key" in error_text:
                raise CustomSerializerError({"status": False, "email": "Email already exists"})
            if "core_user_phone_number_key" in error_text:
                raise CustomSerializerError({"status": False, "phone_number": "Phone number already exists"})
            raise CustomSerializerError({"status": False, "message": "Could not create user"})
    
    
class LoginView(TokenObtainPairView):
    """Log in a user."""

    serializer_class = CustomTokenObtainSerializer


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    user_type = serializers.CharField(required=True)


class DriverLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    user_type = serializers.CharField(required=True)


class LoginView(TokenObtainPairView):
    """Log in a user."""

    serializer_class = CustomTokenObtainSerializer

    @swagger_auto_schema(
        operation_description="User Sign In",
        request_body=LoginRequestSerializer,
        tags=['User']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class VehicleRegistrationSerializer(ModelCustomSerializer):
    """Serializers registration requests and creates a new user vehicle"""
    vehicle_type = VehiclePrimaryKeyRelatedField(
        queryset=VehicleSettings.objects.filter(is_active=True)
    )
    class Meta:
        model = VehicleRegistration
        fields = (
            "vehicle_make",
            "vehicle_type",
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
        constant_data = ConstantTable.constant_table_instance(country_code=user.country_code)
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
            "vehicle_type",
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


class VerificationCodeSerializer(CustomSerializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=4, min_length=4, required=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        attrs["email"] = email
        return attrs
    

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializers update user profile"""

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number", "date_of_birth")


class ForgotPasswordSerializer(CustomSerializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        attrs["email"] = email
        return attrs
    

class ChangeForgotPasswordSerializer(CustomSerializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=4, min_length=4, required=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        otp_code = attrs.get("otp_code")

        user = User.user_email_deleted(email=email)
        if user is None:
            raise CustomSerializerError(
                {"status": False, "email": f"{email} does not exist"}
            )

        if User.is_email_verified(email=email) is False:
            raise CustomSerializerError(
                {"status": False, "message": "user has not been verified"}
            )

        if password != confirm_password:
            raise CustomSerializerError(
                {"status": False, "password": "passwords do not match!"}
            )

        valid_otp_code = User.check_otp(user=user, otp_code=otp_code)
        if valid_otp_code is False:
            raise CustomSerializerError(
                {"status": False, "message": "Invalid otp code"}
            )

        try:
            with transaction.atomic():
                User.create_user_password(user=user, password=password)
        except Exception as e:
            raise CustomSerializerError({"status": False, "message": f"{e}"})
        attrs["email"] = email
        return attrs


class ChangeUserPasswordSerializer(CustomSerializer):
    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        user = self.context.get("user")
        check_password = User.check_user_password(user=user, password=old_password)
        if not check_password:
            raise CustomSerializerError(
                {"status": False, "old_password": "old password is incorrect!"}
            )
        try:
            with transaction.atomic():
                User.create_user_password(user=user, password=new_password)
        except Exception as e:
            raise CustomSerializerError({"status": False, "message": f"{e}"})
        return attrs




class GoogleSignupSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True, allow_blank=False)
    user_type = serializers.CharField(required=False, allow_blank=False)
    country_code = serializers.CharField(required=False, allow_blank=False)

class GoogleSigninSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)


# Driver-specific serializers
class DriverRegistrationSerializer(ModelCustomSerializer):
    """Serializers driver registration requests and creates a new driver."""
    confirm_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    country_code = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "email",
            "ip_address",
            "referral_code",
            "confirm_password",
            "user_type",
            "country_code"
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "email": {"required": True},
            "country_code": {"required": True},
        }

    def validate(self, attrs):
        # Force user_type to be "RIDER" for drivers
        attrs["user_type"] = "RIDER"
        
        country_code = attrs.get("country_code")
        if not country_code:
            raise CustomSerializerError(
                {"status": False, "country_code": "Country Code is Required"}
            )
        # Require leading '+' and at least 1 digit after
        if not isinstance(country_code, str) or not country_code.startswith("+") or not country_code[1:].isdigit():
            raise CustomSerializerError(
                {"status": False, "country_code": "Country code must start with '+' and contain digits only"}
            )
        constant_data = ConstantTable.constant_table_instance(country_code=country_code)
        if constant_data.allow_registration is False:
            raise CustomSerializerError(
                {"status": False, "country_code": "Registration is not allowed for this country"}
            )

        phone_number = attrs.get("phone_number")
        email = attrs.get("email")

        # Check for deleted users by phone number
        deleted_user_phone = User.user_deleted(phone_number=phone_number)
        if deleted_user_phone: # If a deleted user with this phone number exists
            deleted_user_phone.delete() # Delete the old record to allow re-registration

        # Check for existing users (including newly re-registered ones)
        existing_user_phone = User.user_exist(phone_number=phone_number)
        if existing_user_phone:
            raise CustomSerializerError(
                {"status": False, "phone_number": f"{phone_number} is associated with another account"}
            )

        # Check for deleted users by email
        deleted_user_email = User.user_email_deleted(email=email)
        if deleted_user_email: # If a deleted user with this email exists
            deleted_user_email.delete() # Delete the old record to allow re-registration

        # Check for existing users by email (including newly re-registered ones)
        existing_user_email = User.user_email_exist(email=email)
        if existing_user_email:
            raise CustomSerializerError(
                {"status": False, "email": f"{email} is associated with another account"}
            )

        if attrs.get("password") != attrs.get("confirm_password"):
            raise CustomSerializerError(
                {"status": False, "password": "Password and Confirm Password does not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class DriverSigninSerializer(TokenObtainPairSerializer):
    """Driver-specific signin serializer."""
    user_type = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        # Validate user_type is RIDER for drivers
        user_type = attrs.get("user_type")
        if user_type != "RIDER":
            raise CustomSerializerError(
                {"status": False, "user_type": "Invalid User Type. Must be 'RIDER' for driver login"}
            )
        
        # Normalize email to avoid case-sensitivity issues during auth
        email = attrs[self.username_field]
        if isinstance(email, str):
            email = email.lower()
            attrs[self.username_field] = email

        authenticate_kwargs = {
            self.username_field: email,
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
            authenticate_kwargs["email"] = authenticate_kwargs["email"]
        except KeyError:
            pass

        try:
            user = User.objects.get(email=authenticate_kwargs["email"].lower())
            
            # Validate user_type matches the user's actual user_type (must be RIDER)
            if user.user_type != "RIDER":
                self.error_messages["no_active_account"] = "account does not exist!"
                raise exceptions.AuthenticationFailed(
                    self.error_messages["no_active_account"],
                )

            if not user.password:
                self.error_messages["no_password"] = (
                    "please create a password for login!"
                )
                raise exceptions.AuthenticationFailed(
                    self.error_messages["no_password"],
                )
            self.user = authenticate(
                username=user.email, password=authenticate_kwargs["password"]
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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "country_code": user.country_code
        }
        return this_user

# Force rebuild
