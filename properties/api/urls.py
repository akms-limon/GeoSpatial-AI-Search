
from django.urls import path

from . import views

app_name = "property_api"

urlpatterns = [
    path("locations/", views.location_list, name="location-list"),
    path(
        "locations/<int:pk>/",
        views.location_detail,
        name="location-detail",
    ),
    path("properties/", views.property_list, name="property-list"),
    path(
        "properties/<slug:slug>/",
        views.property_detail,
        name="property-detail",
    ),
    path(
        "properties/<int:pk>/nearby/",
        views.nearby_properties,
        name="nearby-properties",
    ),
    path(
        "search-suggestions/",
        views.search_suggestions,
        name="search-suggestions",
    ),
]
