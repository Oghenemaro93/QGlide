from django.urls import include, path

from ride import views

rides = [
    path("ride/", views.CreateRideAPIView.as_view(), name="create-ride"),
    path("ride_status/", views.RideStatusAPIView.as_view(), name="ride-status"),
    path("fetch_user_location/", views.FetchUserLocationAPIView.as_view(), name="fetch-user-location"),
    path("accept_ride/", views.AcceptRideAPIView.as_view(), name="accept-ride"),
    path("cancel_ride_user/", views.CancelRideByUserAPIView.as_view(), name="cancel-ride-user"),
    path("cancel_ride_rider/", views.CancelRideByRiderAPIView.as_view(), name="cancel-ride-rider"),
    path("start_ride_rider/", views.StartRideByRiderAPIView.as_view(), name="cancel-ride-rider"),
]

urlpatterns = [
    *rides,
]