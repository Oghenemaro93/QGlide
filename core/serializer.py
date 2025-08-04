from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.core.validators import FileExtensionValidator
from django.db import transaction
from rest_framework import exceptions, serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.helpers.func import (
    correct_password_check,
    generate_verification_code,
)

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
                    "please verify your account! check your sms"
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
    
    
class LoginView(TokenObtainPairView):
    """Log in a user."""

    serializer_class = CustomTokenObtainSerializer