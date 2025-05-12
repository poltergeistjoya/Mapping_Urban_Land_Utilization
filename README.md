# Mapping Urban Land Utilization

A web application for visualizing and analyzing urban land utilization patterns using geographical data.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL dump file (`recent_dump.sql`) for initial data

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Mapping_Urban_Land_Utilization.git
cd Mapping_Urban_Land_Utilization
```

2. Place the `recent_dump.sql` file in the project root directory

3. Start the application:
```bash
docker compose up
```

4. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Adding New Data

### Using Marimo Notebook

The project includes a Marimo notebook for data exploration and cleaning. To run it:

1. Install the data normalization dependencies using uv (make sure you're in the project root):
```bash
uv pip install --group normalize-data
```

2. Start the notebook:
```bash
marimo edit location_geojsons.py
```

3. The notebook will open in your browser. Use it to:
   - Explore and clean geographical data
   - Generate GeoJSON files
   - Prepare data for database import
   - Access the same database as the Docker setup (using the same environment variables)

Note: This installs all data normalization dependencies including Marimo, geopandas, osmnx, and other required packages.

### Development

For development tools and testing:
```bash
uv pip install --group dev
```

For linting and code quality:
```bash
uv pip install --group lint
```

To install multiple groups at once:
```bash
uv pip install --group dev --group lint
```

### Database Updates

After preparing new data in the Marimo notebook:

1. Export the data to SQL format
2. Update the database using the backend's import utilities
3. Restart the backend service to load new data:
```bash
docker compose restart backend
```

## Development

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + PostGIS
- Database: PostgreSQL with PostGIS extension

## Project Structure

```
.
├── backend/           # FastAPI backend
│   └── src/          # Backend source code
├── frontend/         # React frontend
├── location_geojsons.py  # Marimo notebook for data processing
├── docker-compose.yml    # Docker services configuration
└── recent_dump.sql   # Initial database data
```

## Troubleshooting

- If the frontend can't connect to the backend, ensure both services are running:
  ```bash
  docker compose ps
  ```
- Check backend logs:
  ```bash
  docker compose logs backend
  ```
- Check frontend logs:
  ```bash
  docker compose logs frontend
  ```

## Database 
Postgres + postgis (spatial) + pgrouting (routing)
## Data
~baltimore city limits 

Trying census shapefiles, places, maryland https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2024&layergroup=Places 

nyc bouroughs api endpoint: "https://data.ci
tyofnewyork.us/resource/wh2p-dxnf.geojson"

stret vendor data:

baltimore:https://data.baltimorecity.gov/datasets/baltimore::food-vendor-locations-1/about
nyc: Trying to contact someone from the DOHMH to find this data ugh
overpass-turbo, look at wiki tags https://taginfo.openstreetmap.org/

public trash cans:
nyc: https://data.cityofnewyork.us/Environment/DSNY-Litter-Basket-Inventory/8znf-7b2c/about_data
baltimore: from overpass turbo 

grocery stores:
baltimore: https://data.baltimorecity.gov/maps/baltimore::grocery-stores 
nyc: https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj/about_data 

schools:
baltimore: https://data.baltimorecity.gov/datasets/baltimore::baltimore-city-schools/explore?location=39.296028%2C-76.620343%2C11.38 
nyc: https://data.cityofnewyork.us/Education/2019-2020-School-Locations/wg9x-4ke6/about_data 

https://data.cityofnewyork.us/Education/NYC-DOE-Public-School-Location-Information/3bkj-34v2/about_data outdated? Has less schools? but maybe that means its more up to date?

public_transit 
baltimore: https://data.baltimorecity.gov/datasets/2272d1a39c214ae8a1ac3807b1108ba9_0/explore?location=39.285736%2C-76.612584%2C11.34 ... https://www.mta.maryland.gov/developer-resources 
nyc: https://www.mta.info/developers (all GTFS for subway, LIRR, Metro North, Bus) No ferry service though

neither include private schools? 
walkable road networks:
osmnx 


potential
nyc: farmers markets
Baltimore: liquor Licenses


## TODO 
-[ ] Config file for all settings (batch size, database url, backend url, etc)
-[ ] add batching to populate functions in `populate_db.py`
-[ ] existence checks (either by row or forget it during insert and add deduping function)
-[ ] fix existence check for edges ON CONFLICT DO NOTHING 
-[ ] Pydantic models for routes 
-[ ] Async routes ?
-[ ] Add spatial partitioning (tiling)
-[ ] strange state stuff happens in frontend
-[ ] staten island/governers island dont have edges cuz they not a part of new york 
-[ ] tab image on frontend/public
-[ ] add intermediate nodes for more accurate isochrone (10-20 meter spacing)
-[ ] add allowed highway types to walkableEdge table (low priority)
-[ ] add node table for more accurate isochrone + figure out how to optimize that and make it fast
-[ ] move styling to css 

## Deployment 
make sure you have pg routing 


