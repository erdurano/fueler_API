from django.urls import path, include
from maps.views import MapView


urlpatterns = [
    path("<str:map_id>/", MapView.as_view(), name="map-view"),
]
