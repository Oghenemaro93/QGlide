from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from core import views
from core.serializer import LoginView
from core import otp_views


class TaggedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        tags=['Rider/User'],
        operation_summary="Refresh JWT Token",
        operation_description="Refresh an expired JWT access token using a valid refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The refresh token'
                )
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='New access token'
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="Invalid refresh token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Error message'
                        )
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

urlpatterns = [
    path("signup/", views.RegistrationAPIView.as_view(), name="account_signup"),
    path("signin/", LoginView.as_view(), name="signin"),
    path("verify-token/", views.VerifyUserAPIView.as_view(), name="signiverify-token"),
    path("fetch_vehicle_type/", views.FetchVehicleTypeAPIView.as_view(), name="fetch_vehicle_type"),
    path("fetch_vehicle_type_admin/", views.FetchVehicleTypeAdminAPIView.as_view(), name="fetch_vehicle_type_admin"),
    path("register_vehicle/", views.VehicleRegistrationAPIView.as_view(), name="register_vehicle"),
    path("fetch_vehicle_registration/", views.FetchVehicleRegistrationAPIView.as_view(), name="fetch_vehicle_registration"),
    path("fetch_vehicle_registration_admin/", views.FetchVehicleRegistrationAdminAPIView.as_view(), name="fetch_vehicle_registration_admin"),
    path("verify_email/", views.VerificationAPIView.as_view(), name="verify-email"),
    path("user_profile/", views.GetUserProfileAPIView.as_view(), name="user-profile"),
        path(
        "update_user_profile/",
        views.UpdateUserProfileAPIView.as_view(),
        name="update-user-profile",
    ),
    path("token/refresh/", TaggedTokenRefreshView.as_view(), name="token-refresh"),
    path(
        "forgot_password/",
        views.ForgotPasswordAPIView.as_view(),
        name="forgot-password",
    ),
    path(
        "change_forgot_password/",
        views.ChangeForgotPasswordAPIView.as_view(),
        name="change-forgot-password",
    ),
    path(
        "reset_password/<str:token>/",
        views.ResetPasswordAPIView.as_view(),
        name="reset-password",
    ),
    path(
        "change_password/",
        views.ChangeUserPasswordAPIView.as_view(),
        name="change-user-password",
    ),
    path("google_auth/",views.GoogleAuthAPIView.as_view(), name="google-auth"),
    path("google/signin/", views.GoogleLoginAPIView.as_view(), name="google_login"),
    path("google/signup/", views.GoogleSignupWithProfile.as_view(), name="google_signup_profile"),
    # OTP endpoints
    path("send-otp/", otp_views.send_otp, name="send-otp"),
    path("verify-otp/", otp_views.verify_otp, name="verify-otp"),
    path("resend-otp/", otp_views.resend_otp, name="resend-otp"),
]
