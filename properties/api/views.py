
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from properties.models import Location, Property
from properties.services.property_distance import get_nearby_properties
from properties.services.semantic_search import (
    search_locations,
    search_properties,
)

from .serializers import (
    LocationQuerySerializer,
    LocationSerializer,
    NearbyQuerySerializer,
    PropertyQuerySerializer,
    PropertySerializer,
    SuggestionQuerySerializer,
    SuggestionSerializer,
)


class QueryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


@api_view(["GET"])
def location_list(request):
    params = LocationQuerySerializer(data=request.query_params)
    params.is_valid(raise_exception=True)

    query = params.validated_data.get("q", "").strip()

    locations = Location.objects.filter(is_active=True).order_by("name")

    if query:
        locations = locations.filter(
            Q(name__icontains=query)
            | Q(city__icontains=query)
            | Q(state__icontains=query)
            | Q(country__icontains=query)
        )

    paginator = QueryPagination()
    page = paginator.paginate_queryset(locations, request)

    serializer = LocationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def location_detail(request, pk):
    location = get_object_or_404(
        Location.objects.filter(is_active=True),
        pk=pk,
    )

    serializer = LocationSerializer(location)
    return Response(serializer.data)


@api_view(["GET"])
def property_list(request):
    params = PropertyQuerySerializer(data=request.query_params)
    params.is_valid(raise_exception=True)
    filters = params.validated_data

    properties = (
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images")
        .order_by("id")
    )

    query = filters.get("q", "").strip()

    if query:
        properties = properties.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(address__icontains=query)
        )

    location_id = filters.get("location_id")
    if location_id is not None:
        properties = properties.filter(location_id=location_id)

    property_type = filters.get("property_type", "").strip()
    if property_type:
        properties = properties.filter(
            property_type__iexact=property_type
        )

    min_price = filters.get("min_price")
    if min_price is not None:
        properties = properties.filter(price__gte=min_price)

    max_price = filters.get("max_price")
    if max_price is not None:
        properties = properties.filter(price__lte=max_price)

    bedrooms = filters.get("bedrooms")
    if bedrooms is not None:
        properties = properties.filter(bedrooms=bedrooms)

    paginator = QueryPagination()
    paginator.page_size = filters.get("page_size", 10)

    page = paginator.paginate_queryset(properties, request)
    serializer = PropertySerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def property_detail(request, slug):
    property_obj = get_object_or_404(
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images"),
        slug=slug,
    )

    serializer = PropertySerializer(property_obj)
    return Response(serializer.data)


@api_view(["GET"])
def nearby_properties(request, pk):
    radius_serializer = NearbyQuerySerializer(
        data=request.query_params
    )
    radius_serializer.is_valid(raise_exception=True)
    params = radius_serializer.validated_data

    property_obj = get_object_or_404(
        Property.objects.filter(is_active=True),
        pk=pk,
    )

    if property_obj.point is None:
        return Response({
            "count": 0,
            "results": [],
            "message": "This property has no coordinates.",
        })

    properties = get_nearby_properties(
        property_obj,
        radius_km=params["radius_km"],
        limit=params["limit"],
    ).select_related("location").prefetch_related("images")

    serializer = PropertySerializer(properties, many=True)

    return Response({
        "count": len(serializer.data),
        "radius_km": params["radius_km"],
        "results": serializer.data,
    })


@api_view(["GET"])
def search_suggestions(request):
    params = SuggestionQuerySerializer(data=request.query_params)
    params.is_valid(raise_exception=True)
    values = params.validated_data

    query = values["q"]
    search_type = values["type"]
    limit = values["limit"]

    if search_type == "location":
        matches = search_locations(query, limit=limit)

        results = [
            {
                "id": location.id,
                "label": location.name,
                "subtitle": ", ".join(
                    value
                    for value in [
                        location.city,
                        location.state,
                        location.country,
                    ]
                    if value
                ),
            }
            for location in matches
        ]

    else:
        matches = search_properties(query, limit=limit)

        results = [
            {
                "id": property_obj.id,
                "label": property_obj.title,
                "subtitle": property_obj.location.name,
            }
            for property_obj in matches
        ]

    serializer = SuggestionSerializer(results, many=True)

    return Response({"results": serializer.data})


