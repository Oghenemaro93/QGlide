from django.urls import path

from core.serializer import LoginView

urlpatterns = [
        path("signin/", LoginView.as_view(), name="signin"),
]