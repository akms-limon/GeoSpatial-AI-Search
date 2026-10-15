from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F

from .forms import PropertySearchForm
from .models import Property, Location
from .services.semantic_search import (
    search_properties,
    search_locations,
    search_properties_by_location,
)

from .services.property_distance import (
    add_city_center_distance,
    get_nearby_properties,
)

PROPERTIES_PER_LOAD = 6

def home(request):
    form = PropertySearchForm()

    return render(
        request,
        "properties/home.html",
        {
            "form": form,
        },
    )


@require_GET
def search_suggestions(request):
    query = request.GET.get("q", "").strip()
    search_type = request.GET.get("type", "location")

    if len(query) < 2:
        return JsonResponse({"results": []})

    if search_type == "location":
        suggestions = search_locations(query, limit=5)

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
            for location in suggestions
        ]

    elif search_type == "property":
        suggestions = search_properties(query, limit=5)

        results = [
            {
                "id": property_obj.id,
                "label": property_obj.title,
                "subtitle": property_obj.location.name,
            }
            for property_obj in suggestions
        ]

    else:
        return JsonResponse(
            {"results": []},
            status=400,
        )

    return JsonResponse({"results": results})


def property_listing(request):
    query = request.GET.get("query", "").strip()
    search_type = request.GET.get("search_type", "location")
    location_id = request.GET.get("location_id", "").strip()
    property_id = request.GET.get("property_id", "").strip()

    if search_type not in {"location", "property"}:
        search_type = "location"

    has_searched = "query" in request.GET

    properties = Property.objects.none()

    if has_searched and query:
        form = PropertySearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data["query"]
            search_type = form.cleaned_data["search_type"]

            if search_type == "location":
                location = None

                if location_id.isdigit():
                    location = Location.objects.filter(
                        pk=int(location_id),
                        is_active=True,
                    ).first()

                if location:
                    properties = (
                        Property.objects.filter(
                            is_active=True,
                            location=location,
                        )
                        .select_related("location")
                        .prefetch_related("images")
                    )

                    if location.point is not None:
                        properties = (
                            properties
                            .annotate(
                                card_distance=Distance(
                                    "point",
                                    location.point,
                                )
                            )
                            .order_by(
                                F("card_distance").asc(nulls_last=True),
                                "id",
                            )
                        )
                    else:
                        properties = properties.order_by("id")
                else:
                    # Typed query without a selected location suggestion.
                    properties = search_properties_by_location(
                        query,
                        limit=None,
                    )

                    properties = properties.annotate(
                        card_distance=Distance(
                            "point",
                            "location__point",
                        )
                    ).order_by(
                        F("card_distance").asc(nulls_last=True),
                        "id",
                    )

            else:
                selected_property = None

                if property_id.isdigit():
                    selected_property = Property.objects.filter(
                        pk=int(property_id),
                        is_active=True,
                    ).first()

                # Use the selected property's title as the semantic query.
                semantic_query = (
                    selected_property.title
                    if selected_property
                    else query
                )

                properties = search_properties(
                    semantic_query,
                    limit=None,
                )

                if selected_property and selected_property.point is not None:
                    properties = (
                        properties
                        .annotate(
                            card_distance=Distance(
                                "point",
                                selected_property.point,
                            )
                        )
                        .order_by(
                            "distance",
                            F("card_distance").asc(nulls_last=True),
                            "id",
                        )
                    )

        else:
            properties = Property.objects.none()

    elif not has_searched:
        properties = (
            Property.objects.filter(is_active=True)
            .select_related("location")
            .prefetch_related("images")
            .order_by("title")
        )

    if search_type == "property" and not property_id:
        properties = properties.order_by("distance", "id") if has_searched and query and properties.query.annotations.get("distance") else properties

    paginator = Paginator(properties, 6)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    page_range = paginator.get_elided_page_range(
        page_obj.number,
        on_each_side=2,
        on_ends=1,
    )

    return render(
        request,
        "properties/property_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "search_type": search_type,
            "has_searched": has_searched,
            "page_range": page_range,
        },
    )


def property_detail(request, slug):
    property_obj = get_object_or_404(
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images"),
        slug=slug,
    )

    nearby_properties = get_nearby_properties(
        property_obj,
        radius_km=70,
        limit=6,
    )

    return render(
        request,
        "properties/property_detail.html",
        {
            "property": property_obj,
            "nearby_properties": nearby_properties,
        },
    )