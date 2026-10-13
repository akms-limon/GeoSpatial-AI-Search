
import json
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from properties.models import Location, Property, PropertyImage


class Command(BaseCommand):
    help = "Import demo locations and properties from CSV files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default="data/demo_dataset",
            help="Directory containing locations.csv and properties.csv",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])

        if not data_dir.is_absolute():
            data_dir = settings.BASE_DIR / data_dir

        locations_file = data_dir / "locations.csv"
        properties_file = data_dir / "properties.csv"

        if not locations_file.exists() or not properties_file.exists():
            raise CommandError(
                f"CSV files not found in {data_dir}. "
                "Check the --data-dir argument."
            )

        locations_df = pd.read_csv(locations_file).fillna("")
        properties_df = pd.read_csv(properties_file).fillna("")

        location_map = {}

        for _, row in locations_df.iterrows():
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])

            location, _ = Location.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "name": row["name"],
                    "country": row["country"],
                    "state": row["state"],
                    "city": row["city"],
                    "address": row["address"],
                    "point": Point(longitude, latitude, srid=4326),
                    "is_active": True,
                },
            )

            location_map[row["slug"]] = location

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {len(location_map)} locations."
            )
        )

        imported = 0

        for _, row in properties_df.iterrows():
            location = location_map.get(row["location_slug"])

            if location is None:
                raise CommandError(
                    f"Unknown location slug: {row['location_slug']}"
                )

            amenities = json.loads(row["amenities"] or "[]")

            latitude = float(row["latitude"])
            longitude = float(row["longitude"])

            property_obj, _ = Property.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "location": location,
                    "title": row["title"],
                    "description": row["description"],
                    "property_type": row["property_type"],
                    "price": row["price"],
                    "bedrooms": int(row["bedrooms"]),
                    "bathrooms": int(row["bathrooms"]),
                    "amenities": amenities,
                    "address": row["address"],
                    "point": Point(longitude, latitude, srid=4326),
                    "is_active": True,
                },
            )

            image_urls = [
                url.strip()
                for url in row["image_urls"].split("|")
                if url.strip()
            ]

            for index, image_url in enumerate(image_urls):
                PropertyImage.objects.update_or_create(
                    property=property_obj,
                    image_url=image_url,
                    defaults={
                        "alt_text": property_obj.title,
                        "is_primary": index == 0,
                        "sort_order": index,
                    },
                )

            imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {imported} properties."
            )
        )
