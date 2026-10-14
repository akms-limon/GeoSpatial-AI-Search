import random

from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import render

from .forms import PropertySearchForm
from .models import Property
from .services.semantic_search import (
    search_properties,
    search_properties_by_location,
)


HOME_PAGE_SIZE = 6


def home(request):
    query_submitted = "query" in request.GET
    form = PropertySearchForm(request.GET if query_submitted else None)
    has_searched = False

    if query_submitted and form.is_valid():
        query = form.cleaned_data["query"]
        search_type = form.cleaned_data["search_type"]
        has_searched = True

        if search_type == "location":
            properties = search_properties_by_location(query)
        else:
            properties = search_properties(query)

        properties = properties.select_related("location").prefetch_related("images")
        context = {
            "form": form,
            "properties": properties,
            "has_searched": has_searched,
            "query": query,
        }
        return render(request, "properties/home.html", context)

    # Keep the random order in the session so Show More adds cards without
    # reshuffling the ones the visitor has already seen.
    active_ids = list(
        Property.objects.filter(is_active=True).values_list("id", flat=True)
    )
    homepage_ids = request.session.get("homepage_property_ids", [])

    if not homepage_ids or set(homepage_ids) != set(active_ids):
        homepage_ids = active_ids[:]
        random.shuffle(homepage_ids)
        request.session["homepage_property_ids"] = homepage_ids

    try:
        requested_count = int(request.GET.get("show", HOME_PAGE_SIZE))
    except (TypeError, ValueError):
        requested_count = HOME_PAGE_SIZE

    shown_count = min(max(HOME_PAGE_SIZE, requested_count), len(homepage_ids))
    shown_ids = homepage_ids[:shown_count]

    if shown_ids:
        ordering = Case(
            *[
                When(pk=property_id, then=Value(position))
                for position, property_id in enumerate(shown_ids)
            ],
            output_field=IntegerField(),
        )
        properties = (
            Property.objects.filter(pk__in=shown_ids, is_active=True)
            .select_related("location")
            .prefetch_related("images")
            .order_by(ordering)
        )
    else:
        properties = Property.objects.none()

    return render(
        request,
        "properties/home.html",
        {
            "form": form if query_submitted else PropertySearchForm(),
            "properties": properties,
            "has_searched": False,
            "has_more": shown_count < len(homepage_ids),
            "next_show_count": shown_count + HOME_PAGE_SIZE,
        },
    )
