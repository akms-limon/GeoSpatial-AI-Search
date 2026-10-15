from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    path("", views.home, name="home"),
    path("rentals/", views.property_listing, name="listing"),
    path("property/<slug:slug>/", views.property_detail, name="detail"),
]