
from rest_framework import serializers

from properties.models import Location, Property, PropertyImage


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "slug",
            "country",
            "state",
            "city",
            "address",
            "point",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = PropertyImage
        fields = [
            "id",
            "image",
            "image_url",
            "alt_text",
            "caption",
            "is_primary",
            "sort_order",
        ]
        read_only_fields = fields


class PropertyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "slug",
            "city",
            "state",
            "country",
        ]
        read_only_fields = fields


class PropertySerializer(serializers.ModelSerializer):
    location = PropertyLocationSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "location",
            "title",
            "slug",
            "description",
            "property_type",
            "price",
            "bedrooms",
            "bathrooms",
            "amenities",
            "address",
            "point",
            "images",
            "distance_km",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_distance_km(self, obj):
        distance = getattr(obj, "card_distance", None)

        if distance is None:
            return None

        return round(distance.km, 2)


class LocationQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )


class PropertyQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    location_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    property_type = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    min_price = serializers.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )
    max_price = serializers.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )
    bedrooms = serializers.IntegerField(
        required=False,
        min_value=0,
    )
    page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=50,
        default=10,
    )

    def validate(self, attrs):
        min_price = attrs.get("min_price")
        max_price = attrs.get("max_price")

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise serializers.ValidationError(
                {
                    "max_price": (
                        "Maximum price must be greater than "
                        "or equal to minimum price."
                    )
                }
            )

        return attrs


class SuggestionQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        min_length=2,
        max_length=200,
        trim_whitespace=True,
    )
    type = serializers.ChoiceField(
        choices=["location", "property"],
        default="location",
    )
    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        default=5,
    )


class SuggestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()
    subtitle = serializers.CharField()



class NearbyQuerySerializer(serializers.Serializer):
    radius_km = serializers.FloatField(
        required=False,
        min_value=0.1,
        max_value=200,
        default=50,
    )
    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        default=6,
    )
