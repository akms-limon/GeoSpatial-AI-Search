
from django import forms


class PropertySearchForm(forms.Form):
    SEARCH_CHOICES = [
        ("location", "Location"),
        ("property", "Property Name"),
    ]

    query = forms.CharField(
        max_length=200,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Where do you want to stay?",
                "autocomplete": "off",
                "class": "search-input",
            }
        ),
    )

    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial="location",
        widget=forms.Select(
            attrs={"class": "search-type"}
        ),
    )
