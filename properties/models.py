
from django.contrib.gis.db import models
from pgvector.django import HnswIndex, VectorField


class Location(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    point = models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
    )

    boundary = models.MultiPolygonField(
        srid=4326,
        null=True,
        blank=True,
    )

    embedding = VectorField(
        dimensions=384,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            HnswIndex(
                name="location_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.name}, {self.country}"



class Property(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="properties",
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    property_type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    amenities = models.JSONField(default=list, blank=True)

    address = models.TextField(blank=True)

    point = models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
    )

    embedding = VectorField(
        dimensions=384,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            HnswIndex(
                name="property_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return self.title




class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="properties/%Y/%m/",
        blank=True,
    )

    image_url = models.URLField(blank=True)

    alt_text = models.CharField(
        max_length=255,
        blank=True,
    )

    caption = models.TextField(blank=True)

    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"Image for {self.property.title}"
