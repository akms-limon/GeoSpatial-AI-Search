from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from properties.models import Property


def add_city_center_distance(queryset):
    """Calculate each property's distance from its location center."""
    return queryset.annotate(
        card_distance=Distance("point", "location__point")
    )


def get_nearby_properties(property_obj, radius_km=50, limit=6):
    """Find properties within a radius of the current property."""
    if property_obj.point is None:
        return Property.objects.none()

    return (
        Property.objects.filter(
            is_active=True,
            point__isnull=False,
        )
        .exclude(pk=property_obj.pk)
        .annotate(
            card_distance=Distance("point", property_obj.point)
        )
        .filter(card_distance__lte=D(km=radius_km))
        .order_by("card_distance", "id")[:limit]
    )