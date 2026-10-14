from django.shortcuts import render

from .forms import PropertySearchForm


def home(request):
    form = PropertySearchForm(request.GET or None)

    context = {
        "form": form,
        "properties": [],
        "has_searched": False,
    }

    if request.GET:
        context["has_searched"] = True

    return render(request, "properties/home.html", context)
