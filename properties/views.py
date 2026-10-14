
from django.shortcuts import render

from .forms import PropertySearchForm
from .services.semantic_search import (
    search_properties,
    search_properties_by_location,
)


def home(request):
    form = PropertySearchForm(request.GET or None)

    properties = []
    has_searched = False

    if request.GET and form.is_valid():
        has_searched = True

        query = form.cleaned_data["query"]
        search_type = form.cleaned_data["search_type"]

        if search_type == "location":
            properties = search_properties_by_location(query)
        elif search_type == "property":
            properties = search_properties(query)

    context = {
        "form": form,
        "properties": properties,
        "has_searched": has_searched,
    }

    return render(request, "properties/home.html", context)
