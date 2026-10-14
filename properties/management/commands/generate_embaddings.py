
from django.core.management.base import BaseCommand

from properties.models import Location, Property
from properties.services.semantic_search import (
    get_embedding_model,
    location_embedding_text,
    property_embedding_text,
)


BATCH_SIZE = 64


class Command(BaseCommand):
    help = "Generate and store embeddings for locations and property titles."

    def handle(self, *args, **options):
        model = get_embedding_model()

        location_count = self.generate_embeddings(
            model=model,
            queryset=Location.objects.all().order_by("id"),
            text_builder=location_embedding_text,
            model_class=Location,
        )

        property_count = self.generate_embeddings(
            model=model,
            queryset=Property.objects.all().order_by("id"),
            text_builder=property_embedding_text,
            model_class=Property,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Embedding generation complete: "
                f"{location_count} locations and "
                f"{property_count} properties."
            )
        )

    def generate_embeddings(
        self,
        model,
        queryset,
        text_builder,
        model_class,
    ):
        total = queryset.count()
        updated_count = 0

        for start in range(0, total, BATCH_SIZE):
            batch = list(queryset[start : start + BATCH_SIZE])

            if not batch:
                continue

            texts = [text_builder(obj) for obj in batch]

            embeddings = model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            for obj, embedding in zip(batch, embeddings):
                obj.embedding = embedding.tolist()

            model_class.objects.bulk_update(
                batch,
                ["embedding"],
                batch_size=BATCH_SIZE,
            )

            updated_count += len(batch)

            self.stdout.write(
                f"{model_class.__name__}: "
                f"{updated_count}/{total} processed"
            )

        return updated_count
