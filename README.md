# GeoSpatial AI Search

A Django-based vacation-rental discovery application combining **geospatial search** with **AI-powered semantic search** using PostgreSQL, PostGIS, pgvector, and Sentence Transformers.

> **Demo data:** Includes 200 synthetic properties and 16 Bangladesh locations. Addresses, prices, and coordinates are illustrative, not verified real listings.

## Requirements

Use Ubuntu or another Linux distribution with:

- Python 3.12+
- Docker Engine and Docker Compose
- `uv`
- Git and required geospatial libraries

Install system dependencies:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates gdal-bin libgdal-dev libgeos-dev
```

Install `uv` if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/akms-limon/GeoSpatial-AI-Search.git
cd GeoSpatial-AI-Search
```

### 2. Install dependencies

```bash
uv sync --locked
```

### 3. Start PostgreSQL

```bash
docker compose up --build -d
docker compose ps
```

The `geospatial_db` container exposes PostgreSQL on host port `5433`.

### 4. Enable database extensions

```bash
docker exec geospatial_db psql \
  -U geospatial_user \
  -d geospatial_db \
  -c "CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS vector;"
```

Verify:

```bash
docker exec geospatial_db psql \
  -U geospatial_user \
  -d geospatial_db \
  -c "SELECT extname FROM pg_extension WHERE extname IN ('postgis', 'vector') ORDER BY extname;"
```

### 5. Apply migrations and import data

```bash
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py import_demo_data
```

The import command loads:

- `data/demo_dataset/locations.csv`
- `data/demo_dataset/properties.csv`

### 6. Generate embeddings

```bash
uv run python manage.py generate_embeddings
```

This generates **384-dimensional embeddings** for locations and property titles using `all-MiniLM-L6-v2` and stores them in PostgreSQL.

The first run downloads the model from Hugging Face and requires an internet connection. Regenerate embeddings after changing the source text.

### 7. Start the application

```bash
uv run python manage.py runserver
```

Optional: create an admin account.

```bash
uv run python manage.py createsuperuser
```

| Page | URL |
|---|---|
| Home / Search | http://127.0.0.1:8000/ |
| Property Listings | http://127.0.0.1:8000/rentals/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

## Search Features

- **Location Search:** Find properties by location.
- **Semantic Autocomplete:** Get related location or property suggestions.
- **Property Search:** Find properties using semantically similar titles.
- **Geospatial Search:** Discover nearby properties by distance.
- **Property Filters:** Filter by location, price, property type, bedrooms, and text query.
- **Pagination:** Retrieve results in manageable pages.

### Example Searches

- Location: `Dhaka`, `Sylhet`, `Cox's Bazar`
- Property name: `Modern Residence`, `Sunny Homestay`

Select an autocomplete suggestion for a specific result, or submit a text query for semantic matching.

## REST API

Base URL: `http://127.0.0.1:8000/api/`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/locations/` | List and search locations |
| GET | `/locations/<pk>/` | Retrieve a location |
| GET | `/properties/` | List and filter properties |
| GET | `/properties/<slug>/` | Retrieve a property |
| GET | `/properties/<pk>/nearby/` | Find nearby properties |
| GET | `/search-suggestions/` | Semantic autocomplete |

### Location Search

```bash
curl "http://127.0.0.1:8000/api/locations/?q=Dhaka"
```

### Semantic Autocomplete

Location suggestions:

```bash
curl -G "http://127.0.0.1:8000/api/search-suggestions/" \
  --data-urlencode "q=Dhaka" \
  --data-urlencode "type=location"
```

Property suggestions:

```bash
curl -G "http://127.0.0.1:8000/api/search-suggestions/" \
  --data-urlencode "q=Modern Residence" \
  --data-urlencode "type=property"
```

The `type` parameter accepts `location` or `property`, and `q` must contain at least two characters. Suggestions are based on stored embeddings and may include semantically related results.

## Database Configuration

The default local development settings are configured in `config/settings.py` and `compose.yaml`.

| Setting | Value |
|---|---|
| Database | `geospatial_db` |
| User | `geospatial_user` |
| Password | `local_dev_password` |
| Host | `127.0.0.1` |
| Port | `5433` |

These credentials are for local development only.

## Validation

```bash
uv run python manage.py check
uv run python manage.py migrate
```

