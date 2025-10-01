from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from core import views
from core.serializer import LoginView

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
    path(
        "send_verification_code/",
        views.ResendVerificationCodeAPIView.as_view(),
        name="re-send-verification-code",
    ),
    path("user_profile/", views.GetUserProfileAPIView.as_view(), name="user-profile"),
        path(
        "update_user_profile/",
        views.UpdateUserProfileAPIView.as_view(),
        name="update-user-profile",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
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
        "change_password/",
        views.ChangeUserPasswordAPIView.as_view(),
        name="change-user-password",
    ),
    path("google_auth/",views.GoogleAuthAPIView.as_view(), name="google-auth"),
    path("google/signin/", views.GoogleLoginAPIView.as_view(), name="google_login"),
    path("google/signup/", views.GoogleSignupWithProfile.as_view(), name="google_signup_profile"),
]
