from functools import lru_cache

from sentence_transformers import SentenceTransformer
from properties.models import Property, Location
from pgvector.django import CosineDistance


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the model once per application process."""
    return SentenceTransformer(MODEL_NAME, device="cpu")


def generate_embedding(text: str) -> list[float]:
    """Convert text into a normalized 384-dimensional vector."""
    embedding = get_embedding_model().encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embedding.tolist()



def location_embedding_text(location: Location) -> str:
    """Build searchable text from all relevant location fields."""
    fields = [
        location.name,
        location.city,
        location.state,
        location.country,
        location.address,
    ]

    return ", ".join(
        value.strip()
        for value in fields
        if value and value.strip()
    )



def property_embedding_text(property_obj: Property) -> str:
    """Use only the property title for semantic search."""
    return property_obj.title.strip()



def search_locations(query: str, limit: int = 5):
    """Find locations semantically similar to the query."""
    query = query.strip()

    if not query:
        return Location.objects.none()

    embedding = generate_embedding(query)

    return (
        Location.objects
        .filter(is_active=True, embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", embedding))
        .order_by("distance")[:limit]
    )


def search_properties(query: str, limit: int = 6):
    """Find properties semantically similar to the query."""
    query = query.strip()

    if not query:
        return Property.objects.none()

    embedding = generate_embedding(query)

    return (
        Property.objects
        .filter(is_active=True, embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", embedding))
        .order_by("distance")[:limit]
    )



def search_properties_by_location(query: str, limit: int = 6):
    """Find properties belonging to semantically matched locations."""
    locations = search_locations(query, limit=5)

    return (
        Property.objects
        .filter(
            is_active=True,
            location__in=locations,
        )
        .select_related("location")
        .prefetch_related("images")
        .order_by("id")[:limit]
    )