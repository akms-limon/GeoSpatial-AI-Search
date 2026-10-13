from django.contrib import admin
from django.utils.html import format_html

from .models import Location, Property, PropertyImage


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



class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "image_preview", "alt_text", "caption", "is_primary", "sort_order")
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" width="120" style="object-fit: cover;" />',
                obj.image.url,
            )
        return "No image uploaded"


class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]