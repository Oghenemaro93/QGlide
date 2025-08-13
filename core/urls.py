from django.urls import path

from core import views
from core.serializer import LoginView

urlpatterns = [
    path("signup/", views.RegistrationAPIView.as_view(), name="signup"),
    path("signin/", LoginView.as_view(), name="signin"),
]