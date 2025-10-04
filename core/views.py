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
from core.helpers.brevor import BervorApi
from core.helpers.func import generate_verification_code
from core.helpers.mailersend import MailerSendApi
from core.models import User, VehicleRegistration, VehicleSettings
from core.permissions import UserIsActive
from core.serializer import ChangeForgotPasswordSerializer, ChangeUserPasswordSerializer, DriverLoginRequestSerializer, DriverRegistrationSerializer, DriverSigninSerializer, FetchVehicleRegistrationAdminSerializer, FetchVehicleRegistrationSerializer, FetchVehicleTypeSerializer, ForgotPasswordSerializer, GoogleSigninSerializer, GoogleSignupSerializer, RegistrationSerializer, ResetPasswordSerializer, UserProfileSerializer, VehicleRegistrationSerializer, VerificationCodeSerializer
from ride.models import Ride
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.


class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"


class RegistrationAPIView(APIView):
    """Register a new user."""
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        operation_description="User Registration",
        request_body=RegistrationSerializer,
        tags=['Rider/User']
    )
    def post(self, request):
        """Handle HTTP POST request."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        un_hashed_otp_code = serializer.validated_data.get("un_hashed_otp_code")
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        email = serializer.validated_data.get("email")
        del serializer.validated_data["un_hashed_otp_code"]
        serializer.save()

        full_name = f"{first_name} {last_name}"
        phone_number = serializer.validated_data.get("phone_number")
        
        try:
            from core.helpers.gmail_smtp import GmailSMTP
            GmailSMTP.send_otp_email(recipient=email, name=full_name, otp_code=un_hashed_otp_code)
        except Exception as e:
            # Log the error but don't fail registration
            # User is already created, so we continue
            pass
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

    @swagger_auto_schema(
        operation_description="Register Vehicle",
        request_body=VehicleRegistrationSerializer,
        tags=['Rider/User']
    )
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

    @swagger_auto_schema(
        operation_description="Fetch Vehicle Types",
        tags=['Rider/User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_description="Fetch Vehicle Types (Admin)",
        tags=['Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
    

class FetchVehicleRegistrationAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    pagination_class = CustomPagination
    serializer_class = FetchVehicleRegistrationSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    
    search_fields = ("name",)

    @swagger_auto_schema(
        operation_description="Fetch Vehicle Registrations",
        tags=['Rider/User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
    

class FetchVehicleRegistrationAdminAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    pagination_class = CustomPagination
    serializer_class = FetchVehicleRegistrationAdminSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    
    filterset_fields = ("is_active", "is_deleted", "is_approved", "vehichle_type__name")
    search_fields = ("vehichle_type__name", "user__phone", "vehicle_make", "vehicle_model", "vehicle_plate_number")

    @swagger_auto_schema(
        operation_description="Fetch Vehicle Registrations (Admin)",
        tags=['Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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


class VerifyUserAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    
    @swagger_auto_schema(
        operation_description="Verify User Token",
        tags=['Rider/User']
    )
    def get(self, request):

        user = request.user
        user_id = user.id
        is_driver = user.user_type
        country_code = user.country_code

        ride_type = None
        vehicle_type = None

        # if user.user_type == "USER":
        #     get_ride = Ride.objects.filter(user=user, is_completed=False).first()
        #     if get_ride is None:
        #         return Response({
        #             "status": False,
        #             "message": "User has no open ride",
        #         }, status=status.HTTP_403_FORBIDDEN)
        #     else:
        #         ride_type = get_ride.ride_type
        #         vehicle_type = get_ride.vehicle_type
        # else:
        #     get_rider = VehicleRegistration.objects.filter(user=user, vehicle_status="ONLINE", is_active=True).first()
        #     if get_rider is None:
        #         return Response({
        #             "status": False,
        #             "message": "Rider has no available vehicle",
        #         }, status=status.HTTP_403_FORBIDDEN)

        #     else:
        #         if get_rider.vehichle_type is None:
        #             return Response({
        #                 "status": False,
        #                 "message": "Rider has no available vehicle",
        #             }, status=status.HTTP_403_FORBIDDEN)
        #         else:
        #             ride_type = get_rider.vehichle_type.ride_type
        #             vehicle_type = get_rider.vehichle_type.vehicle_type
                    
        # if ride_type is None or vehicle_type is None:
        #     return Response({
        #         "status": False,
        #         "message": "Rider has no available vehicle",
        #     }, status=status.HTTP_403_FORBIDDEN) 
        
        return Response({
            'user_id': user_id,
            'is_driver': True if is_driver == "RIDER" else False,
            'ride_type': ride_type,
            'vehicle_type': vehicle_type,
            'country_code': country_code
        }, status=status.HTTP_200_OK)


class VerificationAPIView(APIView):
    """Verify a user."""

    serializer_class = VerificationCodeSerializer

    @swagger_auto_schema(
        operation_description="Verify Email with OTP",
        request_body=VerificationCodeSerializer,
        tags=['Rider/User']
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification_code = serializer.validated_data.get("otp_code")
        email = serializer.validated_data.get("email")

        verified_user = User.is_email_verified(email=email)
        if verified_user:
            return Response(
                {"status": False, "message": f"{email} already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.user_email_exist(email=email)
        if user is None:
            return Response(
                {"status": False, "message": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_otp_code = User.check_otp(user=user, otp_code=verification_code)
        if valid_otp_code is False:
            return Response(
                {"status": False, "message": "Invalid otp code"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_verified = True
        user.save()
        return Response(
            {"message": "verification successful"}, status=status.HTTP_200_OK
        )
    



class GetUserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(
        operation_description="Get User Profile",
        tags=['Rider/User']
    )
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateUserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(
        operation_description="Update User Profile",
        request_body=UserProfileSerializer,
        tags=['Rider/User']
    )
    def put(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "user profile successfully"}, status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):
    """Send user forgotten password reset link"""

    serializer_class = ForgotPasswordSerializer
    @swagger_auto_schema(
        operation_description="Forgot Password",
        request_body=ForgotPasswordSerializer,
        tags=['Rider/User']
    )
    def post(self, request):
        """Handle HTTP POST request."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")

        user = User.user_email_exist(email)
        if user is None:
            return Response(
                {"status": False, "message": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_verified is False:
            return Response(
                {"status": False, "message": "User is not verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create password reset token
        from core.models import PasswordResetToken
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # Generate reset link
        reset_link = f"{request.build_absolute_uri('/')[:-1]}/reset-password/{reset_token.token}"
        
        # Send reset link via email
        from core.helpers.gmail_smtp import GmailSMTP
        success = GmailSMTP.send_password_reset_email(
            recipient=email, 
            name=user.full_name, 
            reset_link=reset_link
        )
        
        if not success:
            return Response(
                {"status": False, "message": "Failed to send reset email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        return Response(
            {"status": True, "message": "Password reset link sent to your email"},
            status=status.HTTP_200_OK,
        )


class ChangeForgotPasswordAPIView(APIView):
    """Change user forgotten password."""

    serializer_class = ChangeForgotPasswordSerializer

    @swagger_auto_schema(
        operation_description="Change Forgot Password",
        request_body=ChangeForgotPasswordSerializer,
        tags=['Rider/User']
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password changed successful"}, status=status.HTTP_200_OK
        )


class ResetPasswordAPIView(APIView):
    """Reset user password using token from email link."""

    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(
        operation_description="Reset Password using token from email",
        request_body=ResetPasswordSerializer,
        tags=['Rider/User']
    )
    def post(self, request, token):
        """Handle password reset using token from email link."""
        try:
            from core.models import PasswordResetToken
            
            # Find the reset token
            reset_token = PasswordResetToken.objects.get(token=token)
            
            # Check if token is valid
            if not reset_token.is_valid():
                return Response(
                    {"status": False, "message": "Invalid or expired reset token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Validate the new password data
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update user password
            password = serializer.validated_data.get("password")
            reset_token.user.set_password(password)
            reset_token.user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.used_at = timezone.now()
            reset_token.save()
            
            return Response(
                {"status": True, "message": "Password reset successfully"},
                status=status.HTTP_200_OK,
            )
            
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"status": False, "message": "Invalid reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": f"Error resetting password: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def reset_password_page(request, token):
    """Serve the password reset page."""
    try:
        from core.models import PasswordResetToken
        
        # Check if token exists and is valid
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            return render(request, 'reset_password.html', {
                'error_message': 'This reset link has expired or is invalid. Please request a new password reset.'
            })
        
        return render(request, 'reset_password.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        return render(request, 'reset_password.html', {
            'error_message': 'Invalid reset link. Please request a new password reset.'
        })


class ChangeUserPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated, UserIsActive]
    serializer_class = ChangeUserPasswordSerializer

    @swagger_auto_schema(
        operation_description="Change User Password",
        request_body=ChangeUserPasswordSerializer,
        tags=['Rider/User']
    )
    def put(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "password updated successfully"}, status=status.HTTP_200_OK
        )
    

class GoogleAuthAPIView(APIView):
    # serializer_class = ChangeUserPasswordSerializer

    @swagger_auto_schema(
        operation_description="Google Auth Info",
        tags=['Rider/User']
    )
    def get(self, request):
        return Response(
            {"message": "Google Auth"}, status=status.HTTP_200_OK
        )


class GoogleSignupWithProfile(APIView):

    serializer_class = GoogleSignupSerializer
    
    @swagger_auto_schema(
        operation_description="Google Signup with Profile",
        request_body=GoogleSignupSerializer,
        tags=['Rider/User']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_token = serializer.validated_data["access_token"]

        # ✅ Verify token with Google
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        response = requests.get(google_url)
        if response.status_code != 200:
            return Response({"status": False, "message": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        email = data.get("email")
        first_name = data.get("given_name", "")
        last_name = data.get("family_name", "")
        phone_number = serializer.validated_data.get("phone_number")
        user_type = serializer.validated_data.get("user_type")
        country_code = serializer.validated_data.get("country_code")

        if User.user_deleted(phone_number=phone_number):
            return Response(
                {"status": False, "phone_number": f"{phone_number} has been used, try another phone_number"}
            )
        if User.user_exist(phone_number=phone_number):
            return Response(
                {"status": False, "phone_number": f"{phone_number} is associated with another account"}
            )
        if User.user_email_deleted(email=email):
            return Response(
                {"status": False, "email": f"{email} has been used, try another email"}
            )
        if User.user_email_exist(email=email):
            return Response(
                {"status": False, "email": f"{email} is associated with another account"}
            )
        user = User.objects.create(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            country_code=country_code
        )

        return Response(
            {
                "status": True,
                "message": "User registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )
    

class GoogleLoginAPIView(APIView):
    serializer_class = GoogleSigninSerializer  # reuse for token input

    @swagger_auto_schema(
        operation_description="Google Sign In",
        request_body=GoogleSigninSerializer,
        tags=['Rider/User']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data["access_token"]

        # Verify Google token
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={access_token}"
        response = requests.get(google_url)
        if response.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        email = data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status": False, "error": "User not found. Please sign up first."}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_type": user.user_type,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "country_code": user.country_code
        }, status=status.HTTP_200_OK)


# Driver-specific views
class DriverRegistrationAPIView(APIView):
    """Register a new driver."""
    serializer_class = DriverRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Driver Registration",
        request_body=DriverRegistrationSerializer,
        responses={
            201: DriverRegistrationSerializer,
            400: "Bad Request"
        },
        tags=['Driver']
    )
    def post(self, request):
        """Handle HTTP POST request for driver registration."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        un_hashed_otp_code = serializer.validated_data.get("un_hashed_otp_code")
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        email = serializer.validated_data.get("email")
        del serializer.validated_data["un_hashed_otp_code"]
        serializer.save()

        full_name = f"{first_name} {last_name}"
        message = f"Hi {full_name}, your driver account has been created successfully. Please verify your account with the OTP sent to your email."

        return Response({
            "status": True,
            "message": message,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class DriverSigninView(TokenObtainPairView):
    """Driver signin view."""
    
    serializer_class = DriverSigninSerializer

    @swagger_auto_schema(
        operation_description="Driver Sign In",
        request_body=DriverLoginRequestSerializer,
        responses={
            200: "Login successful",
            400: "Bad Request",
            401: "Unauthorized"
        },
        tags=['Driver']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)