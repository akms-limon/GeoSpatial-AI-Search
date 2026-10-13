from django.contrib import admin

from .models import Location, Property


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "state",
        "country",
        "is_active",
        "created_at",
    )
    list_filter = ("country", "state", "is_active")
    search_fields = ("name", "city", "state", "country")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "location",
        "property_type",
        "price",
        "bedrooms",
        "bathrooms",
        "is_active",
    )

    list_filter = (
        "property_type",
        "is_active",
        "location__country",
    )

    search_fields = (
        "title",
        "description",
        "address",
        "location__name",
    )

    prepopulated_fields = {"slug": ("title",)}