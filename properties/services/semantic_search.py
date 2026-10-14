from functools import lru_cache

from sentence_transformers import SentenceTransformer
from property.models import Property, Location


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