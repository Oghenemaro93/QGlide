from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.decorators import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import VehicleRegistration, VehicleSettings
from core.permissions import UserIsActive
from core.serializer import FetchVehicleRegistrationAdminSerializer, FetchVehicleRegistrationSerializer, FetchVehicleTypeSerializer, RegistrationSerializer, VehicleRegistrationSerializer

# Create your views here.


class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"


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
    

class FetchVehicleTypeAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    pagination_class = CustomPagination
    serializer_class = FetchVehicleTypeSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    
    search_fields = ("name",)

    def get_queryset(self):

        all_vehicle_type = VehicleSettings.objects.filter(is_active=True)

        return all_vehicle_type

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class FetchVehicleTypeAdminAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    pagination_class = CustomPagination
    serializer_class = FetchVehicleTypeSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)

    filterset_fields = ("is_active",)
    search_fields = ("name",)

    def get_queryset(self):

        all_vehicle_type = VehicleSettings.objects.all()

        return all_vehicle_type

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class VehicleRegistrationAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    pagination_class = CustomPagination
    serializer_class = FetchVehicleRegistrationSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    
    search_fields = ("name",)

    def get_queryset(self):

        all_vehicle_registration = VehicleRegistration.objects.filter(is_deleted=False, user=self.request.user)

        return all_vehicle_registration

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class VehicleRegistrationAdminAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    pagination_class = CustomPagination
    serializer_class = FetchVehicleRegistrationAdminSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    
    filterset_fields = ("is_active", "is_deleted", "is_approved", "vehichle_type__name")
    search_fields = ("vehichle_type__name", "user__phone", "vehicle_make", "vehicle_model", "vehicle_plate_number")

    def get_queryset(self):

        all_vehicle_registration = VehicleRegistration.objects.all()

        return all_vehicle_registration

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
