from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render

from .forms import PropertySearchForm
from .models import Property
from .services.semantic_search import (
    search_properties,
    search_properties_by_location,
)

from .services.property_distance import (
    add_city_center_distance,
    get_nearby_properties,
)




PROPERTIES_PER_LOAD = 6


def home(request):
    form = PropertySearchForm()
    total = Property.objects.filter(is_active=True).count()

    try:
        shown_count = max(
            PROPERTIES_PER_LOAD,
            int(request.GET.get("show", PROPERTIES_PER_LOAD)),
        )
    except (TypeError, ValueError):
        shown_count = PROPERTIES_PER_LOAD

    shown_count = min(shown_count, total)

    properties = add_city_center_distance(
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images")
        .order_by("?")[:shown_count]
    )

    return render(
        request,
        "properties/home.html",
        {
            "form": form,
            "properties": properties,
            "has_searched": False,
            "has_more": shown_count < total,
            "next_show_count": shown_count + PROPERTIES_PER_LOAD,
        },
    )


def property_listing(request):
    query = request.GET.get("query", "").strip()
    search_type = request.GET.get("search_type", "location")

    if search_type not in {"location", "property"}:
        search_type = "location"

    has_searched = "query" in request.GET

    if has_searched and query:
        form = PropertySearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data["query"]
            search_type = form.cleaned_data["search_type"]

            if search_type == "location":
                properties = search_properties_by_location(
                    query,
                    limit=None,
                )
            else:
                properties = search_properties(
                    query,
                    limit=None,
                )
        else:
            properties = Property.objects.none()
    elif has_searched:
        properties = Property.objects.none()
    else:
        properties = (
            Property.objects.filter(is_active=True)
            .select_related("location")
            .prefetch_related("images")
            .order_by("title")
        )

    properties = add_city_center_distance(properties)
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