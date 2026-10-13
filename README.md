# GeoSpatial-Search
Geospatial search, distance filtering and property recommendations


# GeoSpatial-AI-Search demo dataset

Contains 200 synthetic demo properties across 16 Bangladesh location records.

- `locations.csv`: locations, coordinates, and `parent_slug`.
- `properties.csv`: 100 synthetic properties, amenities, coordinates, and two image URLs per property.
- These are demo records, not real listings. Prices and addresses are illustrative.
- Saint Martin Island is a distinct location with `city=Cox's Bazar` and `parent_slug=cox-bazar`.
- The current Django `Location` model has no parent field; `parent_slug` is metadata only until the model/import logic maps the hierarchy.
- Coordinates are approximate city/island centers with synthetic offsets for testing only, not verified property coordinates.
- `image_urls` contains two Unsplash URLs separated by `|`. URLs should be verified for accessibility.
- Current `PropertyImage.image` is an `ImageField`, not a URL field. To persist images locally, an importer must download each URL and save the file; alternatively add a URL field if storing links only.
- Import locations first, then properties using `location_slug`. Generate 384-dimensional embeddings separately using `all-MiniLM-L6-v2`.


Dataset update: `properties.csv` now contains **200 synthetic demo properties** distributed across all 16 locations. Property records and coordinates are illustrative demo data, not verified real-world listings.