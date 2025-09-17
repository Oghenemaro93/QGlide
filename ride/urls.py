from django.urls import include, path

from ride import views

rides = [
    path("ride/", views.CreateRideAPIView.as_view(), name="create-brand"),
]

urlpatterns = [
    *rides,
]