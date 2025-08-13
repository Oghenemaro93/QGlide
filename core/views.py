from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import UserIsActive
from core.serializer import RegistrationSerializer, VehicleRegistrationSerializer

# Create your views here.


class RegistrationAPIView(APIView):
    """Register a new user."""
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(request_body=RegistrationSerializer)
    def post(self, request):
        """Handle HTTP POST request."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        un_hashed_otp_code = serializer.validated_data.get("un_hashed_otp_code")
        print(un_hashed_otp_code)
        del serializer.validated_data["un_hashed_otp_code"]
        serializer.save()
        phone_number = serializer.validated_data.get("phone_number")

        # send_user_welcome_email(email=email, otp_code=un_hashed_otp_code)
        return Response(
            {
                "status": True,
                "message": "User registered successfully. Please verify your account.",
            },
            status=status.HTTP_201_CREATED,
        )
    

class VehicleRegistrationAPIView(APIView):
    """Register a new vehicle."""
    permission_classes = [IsAuthenticated, UserIsActive]
    serializer_class = VehicleRegistrationSerializer

    @swagger_auto_schema(request_body=VehicleRegistrationSerializer)
    def post(self, request):
        """Handle HTTP POST request."""

        serializer = self.serializer_class(data=request.data, context={"user": request.user})
        previous_vehicle = serializer.validated_data.pop("previous_vehicle", None)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if previous_vehicle:
            previous_vehicle.update(is_deleted=True, is_active=False, deleted_at=timezone.now())

        # send_user_welcome_email(email=email, otp_code=un_hashed_otp_code)
        return Response(
            {
                "status": True,
                "message": "User registered successfully. Please verify your account.",
            },
            status=status.HTTP_201_CREATED,
        )