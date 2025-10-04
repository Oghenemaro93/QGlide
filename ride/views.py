from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.decorators import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import ConstantTable, User
from core.permissions import (
    AlreadyStartedRide, AcceptedRiderActiveRide, CancelUserActiveRide, CashPaymentActiveRide, EndRiderActiveRide, StartRiderActiveRide, UserHasNoActiveRide, UserIsActive, WaitingRiderActiveRide
)
from ride.models import Ride
from ride.serializer import (
    AcceptRideSerializer, CancelUserRideSerializer, CashPaymentSerializer, CreateRideSerializer, EndRideSerializer, RideStatusSerializer, StartRideSerializer, WaitingRideSerializer
)
from haversine import haversine, Unit
from django.utils import timezone
# Create your views here.

class CreateRideAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, AlreadyStartedRide]
    """Start a Ride."""

    serializer_class = CreateRideSerializer
    @swagger_auto_schema(request_body=CreateRideSerializer, tags=['Rider/User'])
    def post(self, request):
        """Handle HTTP POST request."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_time = timezone.localtime().time()
        constant_table = ConstantTable.constant_table_instance(country_code=request.user.country_code)
        is_peak_hours = constant_table.is_peak_hour(peak_hours=constant_table.peak_hours, current_time=current_time)
        serializer["is_peak_hours"] = is_peak_hours
        serializer["user"] = request.user
        serializer.save()
        return Response(
            {
                "status": True,
                "message": "User has created a ride successfully",
            },
            status=status.HTTP_200_OK,
        )
    

class RideStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    """Start a Ride."""
    
    @swagger_auto_schema(tags=['Rider/User'])
    def get(self, request):
        """Handle HTTP POST request."""
        ride_status = Ride.fetch_ride_status(user=request.user)
        if ride_status is None:
            ride_status = False
        else:
            ride_status = True
        
        if ride_status is False:
            return Response(
                {
                    "status": ride_status,
                    "message": "User has no open ride",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        ride_data = RideStatusSerializer(ride_status)
        return Response(
            {
                "status": True,
                "message": "success",
                "ride_data": ride_data.data
            },
            status=status.HTTP_200_OK,
        )
    

class FetchUserLocationAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    """Start a Ride."""
    
    @swagger_auto_schema(tags=['Driver'])
    def get(self, request):
        """Handle HTTP POST request."""
        user_id = request.query_params.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": "invalid user",
            }, status=status.HTTP_403_FORBIDDEN)

        user_longitude = None
        user_latitude = None

        if user.user_type == "USER":
            get_ride = Ride.objects.filter(user=user, is_completed=False).first()
            if get_ride is None:
                return Response({
                    "status": False,
                    "message": "User has no open ride",
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                user_longitude = get_ride.user_pickup_longitude
                user_latitude = get_ride.user_pickup_latitude

        if user_longitude is None or user_latitude is None:
            return Response({
                "status": False,
                "message": "User has location co-ordinates",
            }, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "status": True,
                "message": "success",
                "user_longitude": user_longitude,
                "user_latitude": user_latitude
            },
            status=status.HTTP_200_OK,
        )
    

class AcceptRideAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, UserHasNoActiveRide]
    """Accept a Ride."""

    serializer_class = AcceptRideSerializer
    @swagger_auto_schema(request_body=AcceptRideSerializer, tags=['Driver'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(user=request.user, ride_status="PENDING", is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status": True,
                "message": "Ride Accepted",
            },
            status=status.HTTP_200_OK,
        )
    

class CancelRideByUserAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, CancelUserActiveRide]

    serializer_class = CancelUserRideSerializer
    @swagger_auto_schema(request_body=CancelUserRideSerializer, tags=['Rider/User'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(user=request.user, ride_status__in=["ACCEPTED", "WAITING"], is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status": True,
                "message": "Ride Cancelled",
            },
            status=status.HTTP_200_OK,
        )
    

class CancelRideByRiderAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, AcceptedRiderActiveRide]

    serializer_class = CancelUserRideSerializer
    @swagger_auto_schema(request_body=CancelUserRideSerializer, tags=['Driver'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(driver=request.user, ride_status__in=["ACCEPTED", "WAITING"], is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status": True,
                "message": "Ride Started",
            },
            status=status.HTTP_200_OK,
        )
    

class WaitingRideByRiderAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, WaitingRiderActiveRide]

    serializer_class = WaitingRideSerializer
    @swagger_auto_schema(request_body=WaitingRideSerializer, tags=['Driver'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="ACCEPTED", is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status": True,
                "message": "Rider Waiting",
            },
            status=status.HTTP_200_OK,
        )
    

class StartRideByRiderAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, StartRiderActiveRide]

    serializer_class = StartRideSerializer
    @swagger_auto_schema(request_body=StartRideSerializer, tags=['Driver'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="WAITING", is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status": True,
                "message": "Ride Started",
            },
            status=status.HTTP_200_OK,
        )
    

class RideEndByRiderAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, EndRiderActiveRide]

    serializer_class = EndRideSerializer
    @swagger_auto_schema(request_body=EndRideSerializer, tags=['Driver'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="START_RIDE", is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        constant_table = ConstantTable.constant_table_instance(country_code=request.user.country_code)

        distance = haversine(
            (opened_ride.driver_pickup_latitude, opened_ride.driver_pickup_longitude),
            (opened_ride.driver_ride_end_latitude, opened_ride.driver_ride_end_longitude),
            unit=Unit.KILOMETERS
        )

        duration = opened_ride.ride_end_time - opened_ride.ride_start_time
        
        duration_seconds = duration.seconds

        total_fare, point_discount, point_deducted, points_left = constant_table.calculate_fare(
            country_code=opened_ride.user.country_code, 
            ride_type=opened_ride.ride_type, 
            distance=distance, 
            duration=duration_seconds, 
            is_peak_hours=opened_ride.is_peak_hours
        )
        
        opened_ride.ride_distance = distance
        opened_ride.payable_amount = total_fare
        opened_ride.ride_duration = duration
        opened_ride.point_amount = point_discount
        opened_ride.save()

        if point_deducted:
            pass

        return Response(
            {
                "status": True,
                "message": "Ride Ended",
            },
            status=status.HTTP_200_OK,
        )
    

class CashPaymentByRiderAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive, CashPaymentActiveRide]

    serializer_class = CashPaymentSerializer
    @swagger_auto_schema(request_body=CashPaymentSerializer, tags=['Driver'])
    def post(self, request):
        """Handle HTTP POST request."""

        opened_ride = Ride.objects.filter(driver=request.user, ride_status="END_RIDE", is_completed=False).first()

        serializer = self.serializer_class(opened_ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "status": True,
                "ride_id": opened_ride.id,
                "message": "Payment Completed",
            },
            status=status.HTTP_200_OK,
        )