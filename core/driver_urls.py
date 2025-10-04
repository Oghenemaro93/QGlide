from django.urls import path
from core import views

urlpatterns = [
    path("signup/", views.DriverRegistrationAPIView.as_view(), name="driver_signup"),
    path("signin/", views.DriverSigninView.as_view(), name="driver_signin"),
]
