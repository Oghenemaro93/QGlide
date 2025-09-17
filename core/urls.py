from django.urls import path

from core import views
from core.serializer import LoginView

urlpatterns = [
    path("signup/", views.RegistrationAPIView.as_view(), name="signup"),
    path("signin/", LoginView.as_view(), name="signin"),
    path("verify-token/", views.VerifyUserAPIView.as_view(), name="signiverify-token"),
    path("fetch_vehicle_type/", views.FetchVehicleTypeAPIView.as_view(), name="fetch_vehicle_type"),
    path("fetch_vehicle_type_admin/", views.FetchVehicleTypeAdminAPIView.as_view(), name="fetch_vehicle_type_admin"),
    path("register_vehicle/", views.VehicleRegistrationAPIView.as_view(), name="register_vehicle"),
    path("fetch_vehicle_registration/", views.VehicleRegistrationAPIView.as_view(), name="fetch_vehicle_registration"),
    path("fetch_vehicle_registration_admin/", views.VehicleRegistrationAdminAPIView.as_view(), name="fetch_vehicle_registration_admin"),
]